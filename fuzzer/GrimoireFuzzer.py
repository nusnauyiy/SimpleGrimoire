"""
A simple python fuzzer.

This is not a fully-featured/robust fuzzer. Notably:
- the fuzzer only allows for coverage tracking of the file in which the
  module under test is defined
- the fuzzer keeps track only of failures due to AssertionError or IndexError
  in the program under test; if the program under test raises other types of errors,
  the whole fuzzer will stop with that error.

Authors: Caroline Lemieux + <YOURNAME> for CPSC 539L
Took caroline 28 minutes to complete the programming assignment part of it.
"""

import logging
import os
import random
import time
import json
from typing import Tuple, Set, Union, List, Dict

import coverage

from models.Blank import Blank
from models.Fuzzer import Fuzzer
from models.GeneralizedInput import GeneralizedInput
from models.SavedInput import SavedInput
from util.dictionary_builder import build_dictionary
from util.grimoire_util import random_generalized
from util.splitting_rules import increment_by_offset, find_gaps, find_next_char, find_closures, find_gaps_in_closures
from util.util import log, str_to_bytes, replace_all_instances, replace_random_instance, find_random_substring


class GrimoireFuzzer(Fuzzer):
    def __init__(
            self,
            module_under_test,
            test_file_name: str,
            cov: coverage.Coverage,
            output_dir: str,
            initial_inputs: Set[bytes] = None,
            cumulative: bool = True
    ):
        super().__init__(module_under_test, test_file_name, cov, output_dir)
        # Start with an input of 20 null bytes if no initial inputs are provided.
        if initial_inputs is None:
            initial_inputs = {b"\x00" * 20}

        # list of all previously generalized input
        self.generalized: List[GeneralizedInput] = []

        # mapping of original input to generalized input
        self.generalized_map: Dict[bytes, GeneralizedInput] = {}
        # provided dictionary obtained from the binary
        self.strings: List[bytes] = [str_to_bytes(s) for s in build_dictionary(test_file_name)]

        # cumulative flag for input generalization
        self.cumulative = cumulative

        # Set up the initial inputs to populate `self.saved_inputs`
        for input_data in initial_inputs:
            has_error, input_cov, exec_time = self.exec_with_coverage(input_data)
            logging.warning("fuzzing seed")
            self.generalize_and_save_if_has_new_coverage(input_data, has_error, input_cov, exec_time)

    def is_generalized(self, input_bytes: bytes):
        return input_bytes in self.generalized_map

    def fuzz_prob(self, saved_input: SavedInput) -> float:
        """
        Return the probability with which we should select `saved_input` for mutation.
        """
        minimum_mutated_times = min([i.times_mutated for i in self.saved_inputs])
        return 1 / (1 + (saved_input.times_mutated - minimum_mutated_times))

    def num_mutants(self, saved_input: SavedInput) -> int:
        """
        Return the number of mutated inputs we should produce from `saved_input`.
        """
        base_children = 10
        # Boost for not mutated recently
        base_children += base_children * (max(4 - saved_input.times_mutated, 0))
        # Boost for smaller than average
        smaller_boost = (
            2
            if len(saved_input.data)
               < sum([len(i.data) for i in self.saved_inputs]) / len(self.saved_inputs)
            else 1
        )
        # Boost for faster-running than average
        faster_boost = (
            4
            if saved_input.runtime
               < sum([i.runtime for i in self.saved_inputs]) / len(self.saved_inputs)
            else 1
        )
        base_children = base_children * smaller_boost * faster_boost
        return base_children

    def mutate_input(self, input_bytes: bytes) -> bytes:
        """
        Produce a new byte-level input by mutating `input_data`.

        Note: this function should not alter the original `input_data` object.
        """

        def havoc_amount() -> int:  # note: removed input_bytes parameter
            return 1 << random.randint(1, 7)

        # perhaps some constants here are related https://github.com/RUB-SysSec/redqueen/search?l=Python&q=havoc
        # n ← havoc_amount(input.performance())
        n = havoc_amount()

        # logging.debug(f"!!! MUTATING INPUT: {input_bytes}")
        for i in range(0, n):
            if self.is_generalized(input_bytes):
                generalized_input = self.generalized_map[input_bytes]
                self.input_extension(generalized_input)
                self.recursive_replacement(generalized_input)
            self.string_replacement(input_bytes, self.strings)

    def send_to_fuzzer(self, input_bytes: bytes):
        """
        implies that the fuzzer executes the target application with the mutated input.
        It expects concrete inputs. Thus, mutations working
        on generalized inputs first replace all remaining [] by an empty string
        """
        # logging.debug(f"!!! SENDING TO FUZZER: {input_bytes}")
        has_error, input_cov, exec_time = self.exec_with_coverage(
            input_bytes
        )
        self.generalize_and_save_if_has_new_coverage(
            input_bytes, has_error, input_cov, exec_time
        )

    def input_extension(self, generalized_input: GeneralizedInput):
        """
        we extend a generalized input by placing another randomly
        chosen generalized input, slice, token or string before and
        after the given one.
        """
        rand = random_generalized(self.generalized, self.strings)
        if isinstance(rand, GeneralizedInput):
            rand = rand.get_bytes()
        input_bytes: bytes = generalized_input.get_bytes()
        # logging.debug(f"input extension 1: input_bytes={input_bytes}, rand={rand}, new={input_bytes + rand}")
        self.send_to_fuzzer(input_bytes + rand)
        # logging.debug(f"input extension 2: input_bytes={input_bytes}, rand={rand}, new={rand + input_bytes}")
        self.send_to_fuzzer(rand + input_bytes)

    def recursive_replacement(self, generalized_input: GeneralizedInput):
        def pad_with_gaps(generalized_input: GeneralizedInput) -> GeneralizedInput:
            # adding gaps to the beginning and the end of inputs
            return GeneralizedInput([Blank.get_blank()] + generalized_input.input + [Blank.get_blank()])

        def random_power_of_two() -> int:
            # arbitrarily chosen
            return pow(2, random.randint(1, 10))

        def replace_random_gaps(generalized_input: GeneralizedInput,
                                rand: Union[GeneralizedInput, bytes]) -> GeneralizedInput:
            blank_pos = [i for i in range(len(generalized_input.input)) if
                         isinstance(generalized_input.input[i], Blank)]
            if len(blank_pos) == 0:
                return GeneralizedInput(generalized_input.input[:])
            chosen = random.choice(blank_pos)
            rand_list = []
            if isinstance(rand, GeneralizedInput):
                rand_list = rand.input
            else:
                rand_list.append(rand)
            return GeneralizedInput(generalized_input.input[:chosen] + rand_list + generalized_input.input[chosen + 1:])

        generalized_input = pad_with_gaps(generalized_input)
        for i in range(0, random_power_of_two()):
            rand = random_generalized(self.generalized, self.strings)
            generalized_input = replace_random_gaps(generalized_input, rand)
        # logging.debug("recursive replacement")
        self.send_to_fuzzer(generalized_input.get_bytes())

    def string_replacement(self, input_bytes: bytes, strings: List[bytes]):
        """
        Given an input, it locates all substrings in the input that match
        strings from the obtained dictionary and chooses one randomly.
        GRIMOIRE first selects a random occurrence of the matching substring
        and replaces it with a random string. In a second step, it replaces
        all occurrences of the substring with the same random string. Finally,
        the mutation sends both mutated inputs to the fuzzer.
        """

        def random_string(strings: List[bytes]) -> Union[bytes, None]:
            if len(strings) == 0:
                return None
            return random.choice(strings)

        # note that currently find_random_substring finds all among overlapping substrings,
        # but replace_all_instances will replace non-overlapping instances
        sub = find_random_substring(input_bytes, strings)
        if sub:
            rand = random_string(strings)
            data = replace_random_instance(input_bytes, sub, rand)
            # logging.debug("string replacement 1")
            self.send_to_fuzzer(data)
            data = replace_all_instances(input_bytes, sub, rand)
            # logging.debug("string replacement 2")
            self.send_to_fuzzer(data)

    def fuzz(self, search_time: int):
        """
        Fuzz the test_one_input function defined in `self.module_to_fuzz`
        for time `search_time`.
        """
        start_time = time.time()
        while time.time() - start_time < search_time:
            num_saved_inputs = len(self.saved_inputs)
            for i in range(0, num_saved_inputs):
                saved_input = self.saved_inputs[i]
                # random.random() returns a float in [0,1). There is a higher
                # chance of fuzzing `saved_input` if `fuzz_prob(saved_input)`
                # is near 1.
                if random.random() < self.fuzz_prob(saved_input):
                    self.mutate_input(
                        saved_input.data)  # performs different mutations one at a time and sends each to fuzzer

                    saved_input.times_mutated += 1
        self.save_data()

    def generalize(self, input_data: bytes, new_edges: Set[Tuple[str, int, int]], splitting_rule=None):

        def get_new_bytes(candidate):  # change to edges for the coverage library
            _, edges, _ = self.exec_with_coverage(candidate)
            return edges.difference(self.edges_covered)

        def candidate_check(candidate: bytes):
            # logging.debug(f"checking candidate for blank: {candidate}")
            original_edges = new_edges
            candidate_edges = get_new_bytes(candidate)
            # logging.warning(f"CANDIDATE BYTES {sorted(candidate_edges)}")
            # logging.warning(f"ORIGINAL BYTES {sorted(original_edges)}")
            # logging.warning(f"ORIGINAL-CANDIDATE {original_edges.difference(candidate_edges)}")
            # logging.warning(f"CANDIDATE-ORIGINAL {candidate_edges.difference(original_edges)}")
            return get_new_bytes(candidate) == new_edges

        generalized_input = GeneralizedInput([input_data]).to_exploded_input()

        # Delete-blank Generalization
        generalized_input = find_gaps(generalized_input, Blank.DELETE, candidate_check, increment_by_offset, 256, self.cumulative)
        generalized_input = find_gaps(generalized_input, Blank.DELETE, candidate_check, increment_by_offset, 128, self.cumulative)
        generalized_input = find_gaps(generalized_input, Blank.DELETE, candidate_check, increment_by_offset, 64, self.cumulative)
        generalized_input = find_gaps(generalized_input, Blank.DELETE, candidate_check, increment_by_offset, 32, self.cumulative)
        generalized_input = find_gaps(generalized_input, Blank.DELETE, candidate_check, increment_by_offset, 1, self.cumulative)
        generalized_input = find_gaps(generalized_input, Blank.DELETE, candidate_check, find_next_char, '.', self.cumulative)
        generalized_input = find_gaps(generalized_input, Blank.DELETE, candidate_check, find_next_char, ';', self.cumulative)
        generalized_input = find_gaps(generalized_input, Blank.DELETE, candidate_check, find_next_char, ',', self.cumulative)
        generalized_input = find_gaps(generalized_input, Blank.DELETE, candidate_check, find_next_char, '\n', self.cumulative)
        generalized_input = find_gaps(generalized_input, Blank.DELETE, candidate_check, find_next_char, '\r', self.cumulative)
        generalized_input = find_gaps(generalized_input, Blank.DELETE, candidate_check, find_next_char, '#', self.cumulative)
        generalized_input = find_gaps(generalized_input, Blank.DELETE, candidate_check, find_next_char, ' ', self.cumulative)
        generalized_input = find_gaps_in_closures(generalized_input, Blank.DELETE, candidate_check, find_closures, '(', ')', self.cumulative)
        generalized_input = find_gaps_in_closures(generalized_input, Blank.DELETE, candidate_check, find_closures, '[', ']', self.cumulative)
        generalized_input = find_gaps_in_closures(generalized_input, Blank.DELETE, candidate_check, find_closures, '{', '}', self.cumulative)
        generalized_input = find_gaps_in_closures(generalized_input, Blank.DELETE, candidate_check, find_closures, '<', '>', self.cumulative)
        generalized_input = find_gaps_in_closures(generalized_input, Blank.DELETE, candidate_check, find_closures, '\'', '\'', self.cumulative)
        generalized_input = find_gaps_in_closures(generalized_input, Blank.DELETE, candidate_check, find_closures, '"', '"', self.cumulative)
        # logging.debug(f"Input with delete blanks: {''.join([s if isinstance(s, str) else s.pretty_print() for s in generalized_input])}")

        # Replace-blank Generalization
        generalized_input = find_gaps(generalized_input, Blank.REPLACE, candidate_check, increment_by_offset, 256, self.cumulative)
        generalized_input = find_gaps(generalized_input, Blank.REPLACE, candidate_check, increment_by_offset, 128, self.cumulative)
        generalized_input = find_gaps(generalized_input, Blank.REPLACE, candidate_check, increment_by_offset, 64, self.cumulative)
        generalized_input = find_gaps(generalized_input, Blank.REPLACE, candidate_check, increment_by_offset, 32, self.cumulative)
        generalized_input = find_gaps(generalized_input, Blank.REPLACE, candidate_check, increment_by_offset, 1, self.cumulative)
        generalized_input = find_gaps(generalized_input, Blank.REPLACE, candidate_check, find_next_char, '.', self.cumulative)
        generalized_input = find_gaps(generalized_input, Blank.REPLACE, candidate_check, find_next_char, ';', self.cumulative)
        generalized_input = find_gaps(generalized_input, Blank.REPLACE, candidate_check, find_next_char, ',', self.cumulative)
        generalized_input = find_gaps(generalized_input, Blank.REPLACE, candidate_check, find_next_char, '\n', self.cumulative)
        generalized_input = find_gaps(generalized_input, Blank.REPLACE, candidate_check, find_next_char, '\r', self.cumulative)
        generalized_input = find_gaps(generalized_input, Blank.REPLACE, candidate_check, find_next_char, '#', self.cumulative)
        generalized_input = find_gaps(generalized_input, Blank.REPLACE, candidate_check, find_next_char, ' ', self.cumulative)
        generalized_input = find_gaps_in_closures(generalized_input, Blank.REPLACE, candidate_check, find_closures, '(', ')', self.cumulative)
        generalized_input = find_gaps_in_closures(generalized_input, Blank.REPLACE, candidate_check, find_closures, '[', ']', self.cumulative)
        generalized_input = find_gaps_in_closures(generalized_input, Blank.REPLACE, candidate_check, find_closures, '{', '}', self.cumulative)
        generalized_input = find_gaps_in_closures(generalized_input, Blank.REPLACE, candidate_check, find_closures, '<', '>', self.cumulative)
        generalized_input = find_gaps_in_closures(generalized_input, Blank.REPLACE, candidate_check, find_closures, '\'', '\'', self.cumulative)
        generalized_input = find_gaps_in_closures(generalized_input, Blank.REPLACE, candidate_check, find_closures, '"', '"', self.cumulative)

        return GeneralizedInput(generalized_input, is_exploded_data=True)

    def generalize_and_save_if_has_new_coverage(
            self,
            input_data: bytes,
            has_error: bool,
            input_coverage: Set[Tuple[str, int, int]],
            exec_time: float,
    ):
        """
        Save an input to `self.saved_inputs` if it has new coverage and does not throw an AssertionError,
        or to `self.failing_inputs` if it does throw an AssertionError.
        """

        def splitting_rule():
            return NotImplemented

        for edge in input_coverage:
            if edge not in self.edges_covered and not has_error:
                # logging.warning(f"NEW EDGES COVERED: {sorted(input_coverage.difference(self.edges_covered))}")
                generalized_input: GeneralizedInput = self.generalize(input_data,
                                                                      input_coverage.difference(self.edges_covered),
                                                                      splitting_rule)
                self.edges_covered = self.edges_covered.union(input_coverage)
                self.saved_inputs.append(
                    SavedInput(input_data, input_coverage, exec_time, generalized_input)
                )
                # this is the only new part here
                # logging.debug(f"{input_data} ---generalized to---> {generalized_input.input} = {generalized_input}")
                logging.debug(f"{input_data} ---generalized to---> {generalized_input.pretty_print()}")
                self.generalized.append(generalized_input)
                self.generalized_map[input_data] = generalized_input

                self.coverage_through_time.append(
                    (
                        time.time(),
                        len(self.edges_covered),
                        len(self.edges_covered_failing),
                    )
                )
                logging.info(f"Found new coverage. Total coverage: {len(self.edges_covered)}")
                log(f"Found new coverage. Total coverage: {len(self.edges_covered)}")
                break
            if edge not in self.edges_covered_failing and has_error:
                self.edges_covered_failing = self.edges_covered_failing.union(
                    input_coverage
                )
                self.failing_inputs.append(
                    SavedInput(input_data, input_coverage, exec_time)
                )
                self.coverage_through_time.append(
                    (
                        time.time(),
                        len(self.edges_covered),
                        len(self.edges_covered_failing),
                    )
                )
                logging.info(f"Found new crash. Total coverage: {len(self.edges_covered)}")
                log(f"Found new crash. Total coverage: {len(self.edges_covered)}")
                break

    def save_data(self):
        super().save_data()
        log("Saving generalized input...")
        generalized_file_name = os.path.join(
            self.output_dir, "generalized_input.json"
        )
        with open(generalized_file_name, "w") as input_file:
            input_file.write(json.dumps(
                [g.to_map() for g in self.saved_inputs]
            ))
