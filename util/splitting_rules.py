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
    return start_index, endings

'''
Adds gap in exploded input while retaining information of the removed text.
For example, for:
    exploded_input=['h','e','l','l','o']
    start_index=0
    end_index=3 (non-inclusive)
the exploded_input will be modified to:
    [Blank('hel'), Blank(), Blank(), 'l', 'o']
'''
def add_gap_in_exploded_input(exploded_input, start_index, end_index, blank_type, blank_content=None):
    removed = exploded_input[start_index:end_index]
    removed_blank = Blank.get_blank(blank_type=blank_type)
    if blank_type == Blank.DELETE:
        for token in removed:
            removed_blank.append(token)
    elif blank_type == Blank.REPLACE:
        for token in removed: # TODO: change this to save replace blank input family
            removed_blank.append(token)
    # fill the removed range with Blank objects, with the first Blank containing
    # the removed text (blanks will be merged later)
    exploded_input[start_index:end_index] = [removed_blank] + ([Blank.get_blank()] * (end_index - start_index - 1))

def create_delete_candidate(exploded_input, blank_start, blank_end):
    candidate_exploded_input = exploded_input[0:blank_start] + exploded_input[blank_end:]
    return GeneralizedInput(candidate_exploded_input, True).get_bytes()

def create_replace_candidate(exploded_input, blank_start, blank_end):
    candidate_exploded_input = exploded_input[0:blank_start] + ["1"] + exploded_input[blank_end:] # TODO: fix hardcode
    return GeneralizedInput(candidate_exploded_input, True).get_bytes()

def find_gaps(exploded_input: List[Union[str, Blank]],
              blank_type,
              create_candidate: Callable[[List[Union[str, Blank]], int, int], bytes],
              candidate_check: Callable[[bytes], bool],
              find_next_index: Callable[[List[Union[str, Blank]], int, Union[int, str]], int],
              split_char: str,
              cumulative: bool):
    # if non-cumulative, working_exploded_input will not be modified
    working_exploded_input = exploded_input if cumulative else exploded_input.copy()
    index = 0
    while index < len(working_exploded_input):
        resume_index = find_next_index(working_exploded_input, index, split_char)
        candidate = GeneralizedInput(working_exploded_input[0:index] + working_exploded_input[resume_index:], True).get_bytes()

        if candidate_check(candidate):
            add_gap_in_exploded_input(exploded_input, index, resume_index, blank_type)

        index = resume_index

    ret = GeneralizedInput(exploded_input, True)
    ret.merge_adjacent_gaps_and_bytes()
    return ret.to_exploded_input()


def find_gaps_in_closures(exploded_input: List[Union[str, None]],
                          blank_type,
                          create_candidate: Callable[[List[Union[str, Blank]], int, int], bytes],
                          candidate_check: Callable[[bytes], bool],
                          find_closures: Callable[[List[Union[str, None]], int, str, str], Tuple[int, List[int]]],
                          opening_char: str,
                          closing_char: str,
                          cumulative: bool):
    # if non-cumulative, working_exploded_input will not be modified
    working_exploded_input = exploded_input if cumulative else exploded_input.copy()
    index = 0
    while index < len(working_exploded_input):
        index, endings = find_closures(working_exploded_input, index, opening_char, closing_char)

        if len(endings) == 0:
            break

        ending = len(working_exploded_input)
        while endings:
            ending = endings.pop(0)
            candidate = create_candidate(working_exploded_input, index, ending)

            if candidate_check(candidate):
                add_gap_in_exploded_input(exploded_input, index, ending, blank_type)
                break

        index = ending

    ret = GeneralizedInput(exploded_input, True)
    ret.merge_adjacent_gaps_and_bytes()
    return ret.to_exploded_input()
