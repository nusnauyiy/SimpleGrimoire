import random
from typing import List, Union, Set

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
