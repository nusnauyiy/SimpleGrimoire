from typing import List, Union, Callable, Tuple

from models.Blank import Blank, ReplaceClass
from models.GeneralizedInput import GeneralizedInput


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


def add_gap_in_exploded_input(exploded_input, start_index, end_index, removed_blank: Blank):
    # fill the removed range with Blank objects, with the first Blank containing
    # the removed text (blanks will be merged later)
    exploded_input[start_index:end_index] = [removed_blank] + ([Blank.get_blank()] * (end_index - start_index - 1))


def create_delete_candidates(exploded_input: List[Union[str, Blank]], blank_start, blank_end) -> Tuple[List[Tuple[bytes, str, Union[ReplaceClass, None]]], List[Union[str, Blank]]]:
    candidate_exploded_input = exploded_input[0:blank_start] + exploded_input[blank_end:]
    candidate = GeneralizedInput(candidate_exploded_input, True).get_bytes()
    return [(candidate, "", None)], exploded_input[blank_start:blank_end]


def create_replace_candidates(exploded_input, blank_start, blank_end) -> List[Tuple[bytes, str, ReplaceClass]]:
    res = []
    for replace_class in ReplaceClass:
        seen_candidates = set()
        for i in range(10):
            replacement = ReplaceClass.generate(replace_class)
            while replacement in seen_candidates:
                replacement = ReplaceClass.generate(replace_class)
            seen_candidates.add(replacement)

            candidate_exploded_input = exploded_input[0:blank_start] + [replacement] + exploded_input[blank_end:]
            candidate = GeneralizedInput(candidate_exploded_input, True).get_bytes()
            res.append((candidate, replacement, replace_class))
    return res, exploded_input[blank_start:blank_end]


def find_gaps(exploded_input: List[Union[str, Blank]],
              blank_type,
              candidate_check: Callable[[bytes], bool],
              find_next_index: Callable[[List[Union[str, Blank]], int, Union[int, str]], int],
              split_char: str,
              cumulative: bool):
    # if non-cumulative, working_exploded_input will not be modified
    working_exploded_input = exploded_input if cumulative else exploded_input.copy()
    index = 0

    # index = start of blank that we're trying
    while index < len(working_exploded_input):
        '''
        # start
        exploded_input = "helloworld"
        working = "helloworld"
        
        # after 1st iteration
        exploded_input = "__lloworld"
        working = "__lloworld" # cumulative case, working == exploded_input
        working = "helloworld" # non-cumulative case
        '''

        # resume_index = end of blank that we're trying
        resume_index = find_next_index(working_exploded_input, index, split_char)

        create_candidates = create_delete_candidates if blank_type == Blank.DELETE else create_replace_candidates

        valid_replace_classes = set()  # set of replace classes with passing candidates
        invalid_replace_classes = set()  # set of replace classes with failing candidates

        # candidate_info = [(candidate, replacement, replace class), ...]
        candidate_info, removed = create_candidates(working_exploded_input, index, resume_index)

        # create the blank object to store the information for the current blank we're trying
        removed_blank = Blank.get_blank(blank_type=blank_type)  # blank containing info about the removed chunk
        for token in removed:
            removed_blank.append(token)

        # run each candidate through the fuzzer
        for (candidate, replacement, replace_class) in candidate_info:
            if candidate_check(candidate):
                valid_replace_classes.add(replace_class)
            else:
                invalid_replace_classes.add(replace_class)

        # replace classes = set of valid replace classes for this blank
        replace_classes = valid_replace_classes.difference(invalid_replace_classes)
        # if there is anything in replace_classes, it means the blank is valid
        # -> add the blank in the exploded input
        if len(replace_classes) != 0:
            if blank_type == Blank.REPLACE:
                removed_blank.replacements = replace_classes
            add_gap_in_exploded_input(exploded_input, index, resume_index, removed_blank)

        index = resume_index

    ret = GeneralizedInput(exploded_input, True)
    ret.merge_adjacent_gaps_and_bytes()
    return ret.to_exploded_input()


def find_gaps_in_closures(exploded_input: List[Union[str, None]],
                          blank_type,
                          candidate_check: Callable[[bytes], bool],
                          find_closures: Callable[[List[Union[str, None]], int, str, str], Tuple[int, List[int]]],
                          opening_char: str,
                          closing_char: str,
                          cumulative: bool):
    # if non-cumulative, working_exploded_input will not be modified
    working_exploded_input = exploded_input if cumulative else exploded_input.copy()
    index = 0
    create_candidates = create_delete_candidates if blank_type == Blank.DELETE else create_replace_candidates
    while index < len(working_exploded_input):
        index, endings = find_closures(working_exploded_input, index, opening_char, closing_char)

        if len(endings) == 0:
            break

        ending = len(working_exploded_input)
        while endings:
            ending = endings.pop(0)

            valid_replace_classes = set()
            invalid_replace_classes = set()
            candidate_info, removed = create_candidates(working_exploded_input, index, ending)
            removed_blank = Blank.get_blank(blank_type=blank_type)  # blank containing info about the removed chunk
            for token in removed:
                removed_blank.append(token)
            for (candidate, replacement, replace_class) in candidate_info:
                if candidate_check(candidate):
                    valid_replace_classes.add(replace_class)
                else:
                    invalid_replace_classes.add(replace_class)

            valid_replace_classes = valid_replace_classes.difference(invalid_replace_classes)
            if len(valid_replace_classes) != 0:
                if blank_type == Blank.REPLACE:
                    removed_blank.replacements = valid_replace_classes
                add_gap_in_exploded_input(exploded_input, index, ending, removed_blank)
                break

        index = ending

    ret = GeneralizedInput(exploded_input, True)
    ret.merge_adjacent_gaps_and_bytes()
    return ret.to_exploded_input()
