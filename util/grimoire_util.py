import random
from typing import List, Union, Set, Callable, Tuple

from models.Blank import Blank
from models.GeneralizedInput import GeneralizedInput


def random_slice(generalized: List[GeneralizedInput]) -> GeneralizedInput:
    """
    select a substring between two arbitrary blanks in a generalized input
    """
    chosen = random.choice(generalized).input
    blank_indices = [i for i in range(len(chosen)) if isinstance(chosen[i], Blank)]
    blank_indices.extend([-1, len(chosen)])  # consider the beginning and end of the string a blank
    # TODO: will all generalized inputs be saved with start/end blanks? do we need this step?
    boundaries = random.sample(blank_indices, 2)
    start = min(boundaries)
    end = max(boundaries)
    return GeneralizedInput(chosen[start + 1:end])  # does not include start and end blanks


def random_generalized(generalized: List[GeneralizedInput], strings: List[bytes]) -> Union[GeneralizedInput, bytes]:
    """
    takes as input a set of all previously
    generalized inputs, tokens and strings from the dictionary and
    returns—based on random coin flips—a random (slice of a )
    generalized input, token or string. In case we pick an input
    slice, we select a substring between two arbitrary [] in a generalized input.
    """

    # if random_coin() then
    #     2 if random_coin() then
    #         3 rand ← random_slice(generalized)
    #     4 else
    #         5 rand ← random_token_or_string(generalized)
    # 6 else
    # 7 rand ← random_generalized_input(generalized)
    def random_coin() -> int:
        return random.randint(0, 1)

    # def random_slice(generalized: List[GeneralizedInput]) -> bytes:
    #     """
    #     select a substring between two arbitrary blanks in a generalized input
    #     """
    #     chosen = random.choice(generalized).input
    #     blank_indices = [i for i in range(len(chosen)) if isinstance(chosen[i], Blank)]
    #     boundaries = random.sample(blank_indices, 2)
    #     start = min(boundaries)
    #     end = max(boundaries)
    #     return GeneralizedInput(chosen[start+1:end]) # does not include start and end blanks

    def random_token_or_string(tokens: Set[bytes]) -> bytes:
        """
        randomly selects from tokens and strings from the dictionary
        """
        return random.choice(tokens)

    def random_generalized_input(generalized: List[GeneralizedInput]) -> GeneralizedInput:
        return random.choice(generalized)

    if random_coin():
        if random_coin():
            rand = random_slice(generalized)
        else:
            rand = random_token_or_string(strings)
    else:
        rand = random_generalized_input(generalized)
    return rand


def generic_generalized(input_data: bytes, candidate_check: Callable[[bytes], bool], splitting_rule=None):
    def find_next_boundary(input, start, splitting_rule=None):
        chunk_size = 2
        if start + chunk_size - 1 >= len(input):
            return len(input) - 1
        return start + chunk_size - 1

    def remove_substring(input: bytes, start: int, end: int) -> Tuple[bytes, bytes]:
        return input[0:start] + input[end + 1:], input[start:end + 1]

        # 1 start ← 0
    start = 0
    generalized = GeneralizedInput()
    # 2 while start < input.length() do
    while start < len(input_data):
        # 3 end ← find_next_boundary(input, splitting_rule)
        end = find_next_boundary(input_data, start)  # note: end is inclusive
        # 4 candidate ← remove_substring(input, start, end)
        candidate, substring = remove_substring(input_data, start, end)
        # 5 if get_new_bytes(candidate) == new_bytes then
        if candidate_check(candidate):
            # 6 input ← replace_by_gap(input, start, end)
            # input = replace_by_gap(input, start, end)
            generalized.input.append(Blank())
        else:
            generalized.input.append(substring)
        # 7 start ← end
        start = end
    # 8 input ← merge_adjacent_gaps(input)
    return generalized.merge_adjacent_gaps()
