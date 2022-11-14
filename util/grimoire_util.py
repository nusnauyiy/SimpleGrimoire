import random
from typing import List, Union, Set, Callable, Tuple

from models.Blank import Blank
from models.GeneralizedInput import GeneralizedInput
from util import splitting_rules
import logging

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
    def random_coin() -> int:
        return random.randint(0, 1)

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


def generic_generalized(input_bytes: bytes, candidate_check: Callable[[bytes], bool]) -> GeneralizedInput:
    def find_next_boundary(input_bytes: bytes, start: int, splitting_rule: Callable[[bytes, int], int]):
        return splitting_rule(input_bytes, start)

    def remove_substring(input: bytes, start: int, end: int) -> Tuple[bytes, bytes]:
        return input[0:start] + input[end:], input[start:end]

    # Because of the way we represent generalized inputs
    # (GeneralizedInput obj containing list of bytes and Blank),
    # we need to start with a GeneralizedInput object with the
    # entire input.
    # Whenever we apply a new splitting rule, we need to iterate
    # through all the bytes tokens in the list so far and apply
    # the splitting rule to each token.
    generalized = GeneralizedInput([input_bytes])
    logging.debug("GENERALIZING... ===================================")
    # apply each splitting rule
    for splitting_rule in splitting_rules.split_overlapping_chunk_size_rules:
        logging.debug("New splitting rule!!")
        # temporary obj so we do not alter our `generalized` object
        # while iterating through its tokens
        next_generalized = GeneralizedInput()

        # iterate through each token
        for i in range(len(generalized.input)):
            logging.debug(f"i={i}")
            token = generalized.input[i]

            if isinstance(token, Blank):
                next_generalized.input.append(Blank())

            else:
                # apply splitting rule to token
                start = 0
                while start < len(token):
                    end = find_next_boundary(token, start, splitting_rule)  # note: end is exclusive

                    # since we are splitting a token and not the entire input,
                    # but we still want to consider the entire input as a candidate,
                    # append all surrounding tokens to the current token to create
                    # the candidate.
                    # eg. ["hello", Blank(), "world", Blank(), "goodbye"], current token is "world"
                    # and we are splitting with chunk size of 2.
                    # then we generate the following candidates: (only middle token changes)
                    # "hello" + "rld" + "goodbye" = "hellorldgoodbye"
                    # "hello" + "wod" + "goodbye" = "hellowodgoodbye"
                    # "hello" + "worl" + "goodbye" = "helloworlgoodbye"
                    candidate_token, substring = remove_substring(token, start, end)
                    candidate = GeneralizedInput(generalized.input[0:i] + [candidate_token] + generalized.input[i+1:])\
                                    .get_bytes()
                    logging.debug(f"Candidate: {candidate}")
                    if candidate_check(candidate):
                        logging.debug(f"Adding blank")
                        next_generalized.input.append(Blank())
                    else:
                        logging.debug(f"Adding substring")
                        next_generalized.input.append(substring)
                    start = end
                    logging.debug(f"next_generalized={next_generalized}")

        generalized = next_generalized
        generalized.merge_adjacent_gaps_and_bytes()

    return generalized
