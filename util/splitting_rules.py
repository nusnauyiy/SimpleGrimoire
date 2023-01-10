from typing import List, Union, Callable, Tuple

from models.Blank import Blank
from models.GeneralizedInput import GeneralizedInput


def split_overlapping_chunk_size(chunk_size: int):
    if chunk_size <= 0:
        raise Exception(f"Chunk size cannot be <= 0: {chunk_size}")

    def _split_overlapping_chunk_size(input_bytes: bytes, start: int):
        if start + chunk_size > len(input_bytes):
            return len(input_bytes)
        return start + chunk_size

    return _split_overlapping_chunk_size


chunk_sizes = [256, 128, 64, 32, 2, 1]
split_overlapping_chunk_size_rules = [split_overlapping_chunk_size(chunk_size) for chunk_size in chunk_sizes]


# def trim_generalized(exploded_generalized_input):
#     ret = []
#     before = ""
#     for char_class in exploded_generalized_input:
#         if char_class == before and char_class == "gap":
#             pass
#         else:
#             ret.append(char_class)
#         before = char_class
#     return ret

def increment_by_offset(_, index, offset):
    return index + offset


def find_next_char(exploded_input: List[Union[str, Blank]], index: int, char: str):
    while index < len(exploded_input):
        if exploded_input[index] == char:
            return index + 1
        index += 1
    return index


def find_closures(l, index, opening_char, closing_char):
    endings = []

    while index < len(l):
        if l[index] == opening_char:
            break
        index += 1

    start_index = index
    index_ending = len(l) - 1

    while index_ending > start_index:
        if l[index_ending] == closing_char:
            endings.append(index_ending + 1)
        index_ending -= 1

        index += 1
    return start_index, endings


"""
generalized = ['hel', Blank("hi"), 'lo']
exploded = ['h', 'e', 'l', None, 'l', 'o']
candidate = "heo"
"""

'''
Adds gap in exploded input while retaining information of the removed text.
For example, for:
    exploded_input=['h','e','l','l','o']
    start_index=0
    end_index=3 (non-inclusive)
the exploded_input will be modified to:
    [Blank('hel'), Blank(), Blank(), 'l', 'o']
'''
def add_gap_in_exploded_input(exploded_input, start_index, end_index):
    removed = exploded_input[start_index:end_index]
    removed_blank = Blank()
    for token in removed:
        removed_blank.append(token)
    # fill the removed range with Blank objects, with the first Blank containing
    # the removed text (blanks will be merged later)
    exploded_input[start_index:end_index] = [removed_blank] + ([Blank()] * (end_index - start_index - 1))


def find_gaps(exploded_input: List[Union[str, Blank]],
              candidate_check: Callable[[bytes], bool],
              find_next_index: Callable[[List[Union[str, Blank]], int, Union[int, str]], int],
              split_char: str):
    index = 0
    while index < len(exploded_input):
        resume_index = find_next_index(exploded_input, index, split_char)
        candidate = GeneralizedInput(exploded_input[0:index] + exploded_input[resume_index:], True).get_bytes()

        if candidate_check(candidate):
            add_gap_in_exploded_input(exploded_input, index, resume_index)

        index = resume_index

    ret = GeneralizedInput(exploded_input, True)
    ret.merge_adjacent_gaps_and_bytes()
    return ret.to_exploded_input()


def find_gaps_in_closures(exploded_input: List[Union[str, None]],
                          candidate_check: Callable[[bytes], bool],
                          find_closures: Callable[[List[Union[str, None]], int, str, str], Tuple[int, List[int]]],
                          opening_char: str,
                          closing_char: str):
    index = 0
    while index < len(exploded_input):
        index, endings = find_closures(exploded_input, index, opening_char, closing_char)

        if len(endings) == 0:
            break

        ending = len(exploded_input)
        while endings:
            ending = endings.pop(0)
            candidate = GeneralizedInput(exploded_input[0:index] + exploded_input[ending:], True).get_bytes()

            if candidate_check(candidate):
                add_gap_in_exploded_input(exploded_input, index, ending)
                break

        index = ending

    ret = GeneralizedInput(exploded_input, True)
    ret.merge_adjacent_gaps_and_bytes()
    return ret.to_exploded_input()
