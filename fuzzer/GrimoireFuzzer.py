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

import coverage
import random
import time
from typing import Tuple, Set, Union, List

from models.SavedInput import SavedInput
from models.Fuzzer import Fuzzer
from models.GeneralizedInput import GeneralizedInput
from models.Blank import Blank
from util.dictionary_builder import build_dictionary
from util.util import log, bytes_to_str, str_to_bytes, find_all_overlapping_substr, find_all_nonoverlapping_substr, \
    replace_all_instances, replace_random_instance, find_random_substring
from util.grimoire_util import random_generalized


class GrimoireFuzzer(Fuzzer):
    def __init__(
            self,
            module_under_test,
            test_file_name: str,
            cov: coverage.Coverage,
            output_dir: str,
            initial_inputs: Set[bytes] = None,
    ):
        super().__init__(module_under_test, test_file_name, cov, output_dir)
        # Start with an input of 20 null bytes if no initial inputs are provided.
        if initial_inputs is None:
            initial_inputs = {b"\x00" * 20}
        # Set up the initial inputs to populate `self.saved_inputs`
        for input_data in initial_inputs:
            has_error, input_cov, exec_time = self.exec_with_coverage(input_data)
            self.save_if_has_new_coverage(input_data, has_error, input_cov, exec_time)

        # list of all previously generalized input
        self.generalized: List[GeneralizedInput] = []

        # mapping of original input to generalized input
        self.generalized_map: dict[bytes, GeneralizedInput] = {}
        # provided dictionary obtained from the binary
        self.strings: List[bytes] = [str_to_bytes(s) for s in build_dictionary(test_file_name)]

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

        def havoc_amount(input: bytes) -> int:
            return 512  # TODO: change this to actual value

        # could this be where we're converting byte data to text content?
        # content <- input.content
        # content = bytes_to_str(input_bytes) # TODO: do we need this?

        # this is supposedly a method from redqueen. However, I'm not exactly able to find it in the repo
        # but the paper mentioned that it's generally between 512 - 1024
        # perhaps some constants here are related https://github.com/RUB-SysSec/redqueen/search?l=Python&q=havoc
        # n ← havoc_amount(input.performance())
        n = 512

        # 3 for i ← 0 to n do
        #     4 if input.is_generalized() then
        #         5 input_extension(input, generalized)
        #         6 recursive_replacement(input, generalized)
        #     string_replacement(content, strings)
        # return bytes(mutated_data)

        print(f"!!! MUTATING INPUT: {input_bytes}")
        for i in range(0, n):
            if self.is_generalized(input_bytes):
                generalized_input = self.generalized_map[input_bytes]
                self.input_extension(generalized_input)
                self.recursive_replacement(generalized_input, self.generalized)
            self.string_replacement(input_bytes, self.strings)

    def send_to_fuzzer(self, input_bytes: bytes):
        """
        implies that the fuzzer executes the target application with the mutated input.
        It expects concrete inputs. Thus, mutations working
        on generalized inputs first replace all remaining [] by an empty string
        """
        print(f"!!! SENDING TO FUZZER: {input_bytes}")
        has_error, input_cov, exec_time = self.exec_with_coverage(
            input_bytes
        )
        self.generalize_and_save_if_has_new_coverage(
            input_bytes, has_error, input_cov, exec_time
        )

    def input_extension(self, generalized_input: GeneralizedInput):
        """
        we extend an generalized input by placing another randomly
        chosen generalized input, slice, token or string before and
        after the given one.
        """
        # 1 rand ← random_generalized(generalized_inputs)
        # 2 send_to_fuzzer(concat(input.content(), rand.content()))
        # 3 send_to_fuzzer(concat(rand.content(),input.content()))
        rand = random_generalized(self.generalized, self.strings)
        if isinstance(rand, GeneralizedInput):
            rand = rand.get_bytes()
        input_bytes: bytes = generalized_input.get_bytes()
        self.send_to_fuzzer(input_bytes + rand)
        self.send_to_fuzzer(rand + input_bytes)

    def recursive_replacement(self, generalized_input: GeneralizedInput):
        # 1 input ← pad_with_gaps(input)
        # 2 for i ← 0 to random_power_of_two() do
        #     3 rand ← random_generalized(generalized_inputs)
        #     4 input ← replace_random_gap(input, rand)
        # 5 send_to_fuzzer(input.content())
        def pad_with_gaps(generalized_input: GeneralizedInput) -> GeneralizedInput:
            # adding gaps to the beginning and the end of inputs
            return GeneralizedInput([Blank()] + generalized_input.input + [Blank()])

        def random_power_of_two() -> int:
            # arbitrarily chosen
            return pow(2, random.randint(1, 10))

        def replace_random_gaps(generalized_input: GeneralizedInput, rand: Union[GeneralizedInput, bytes]) -> GeneralizedInput:
            blank_pos = [i for i in range(len(generalized_input.input)) if isinstance(generalized_input.input[i], Blank)]
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

        # 1 sub ← find_random_substring(input, strings)
        # 2 if sub then
        # 3 rand ← random_string(strings)
        # 4 data ← replace_random_instance(input, sub, rand)
        # 5 send_to_fuzzer(data)
        # 6 data ← replace_all_instances(input, sub, and)
        # 7 send_to_fuzzer(data)

        def random_string(strings: List[bytes]):
            return random.choice(strings)

        # note that currently find_random_substring finds all among overlapping substrings,
        # but replace_all_instances will replace non-overlapping instances
        sub = find_random_substring(input_bytes, strings)
        if sub:
            rand = random_string(strings)
            data = replace_random_instance(input_bytes, sub, rand)
            self.send_to_fuzzer(data)
            data = replace_all_instances(input_bytes, sub, rand)
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
                    num_mutants = self.num_mutants(saved_input)
                    for _ in range(0, num_mutants):
                        mutated_input = self.mutate_input(saved_input.data)
                        print(f"!!! MUTATED INPUT: {mutated_input}")
                        has_error, input_cov, exec_time = self.exec_with_coverage(
                            mutated_input
                        )
                        self.generalize_and_save_if_has_new_coverage(
                            mutated_input, has_error, input_cov, exec_time
                        )

                    saved_input.times_mutated += 1
        self.save_data()

    def generalize(self, input, new_edges, splitting_rule=None):
        def merge_adjacent_gaps(generalized):
            i = len(generalized.input) - 1
            while i >= 1:
                elem = generalized.input[i]
                prev_elem = generalized.input[i - 1]
                if isinstance(elem, Blank) and isinstance(prev_elem, Blank):
                    del generalized.input[i]
                i -= 1
            return generalized

        def find_next_boundary(input, start, splitting_rule=None):
            chunk_size = 2
            if start + chunk_size - 1 >= len(input):
                return len(input) - 1
            return start + chunk_size - 1

        def generator():
            for i in range(10):
                yield i

        def remove_substring(input, start, end):
            return (input[0:start] + input[end + 1:], input[start:end + 1])

        def get_new_bytes(candidate):  # change to edges for the coverage library
            _, edges, _ = self.exec_with_coverage(candidate)
            return self.edges_covered.difference(edges)

        # def replace_by_gap(input, start, end):
        #     return NotImplemented

        # 1 start ← 0
        start = 0
        generalized = GeneralizedInput()
        # 2 while start < input.length() do
        while start < len(input):
            # 3 end ← find_next_boundary(input, splitting_rule)
            end = find_next_boundary(input, start)  # note: end is inclusive
            # 4 candidate ← remove_substring(input, start, end)
            candidate, substring = remove_substring(input, start, end)
            # 5 if get_new_bytes(candidate) == new_bytes then
            if get_new_bytes(candidate) == new_edges:
                # 6 input ← replace_by_gap(input, start, end)
                # input = replace_by_gap(input, start, end)
                generalized.input.append(Blank())
            else:
                generalized.input.append(substring)
            # 7 start ← end
            start = end
        # 8 input ← merge_adjacent_gaps(input)
        return merge_adjacent_gaps(generalized)

    def generalize_and_save_if_has_new_coverage(
            self,
            input_data: bytes,
            has_error: bool,
            input_coverage: Set[Tuple[int, int]],
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
                self.edges_covered = self.edges_covered.union(input_coverage)
                self.saved_inputs.append(
                    SavedInput(input_data, input_coverage, exec_time)
                )
                # this is the only new part here
                generalized_input: GeneralizedInput = self.generalize(input_data, edge,
                                                                      splitting_rule)  # TODO does this have to be the set of all new edges?
                self.generalized.append(generalized_input)
                self.generalized_map[input_data] = generalized_input

                self.coverage_through_time.append(
                    (
                        time.time(),
                        len(self.edges_covered),
                        len(self.edges_covered_failing),
                    )
                )
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
                log(f"Found new crash. Total coverage: {len(self.edges_covered)}")
                break
