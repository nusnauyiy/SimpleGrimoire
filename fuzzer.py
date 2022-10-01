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
from abc import ABC, abstractmethod
import argparse
from cgi import test
from genericpath import isdir
import coverage
import importlib
import inspect
import os
import random
import time
from typing import Callable, Tuple, List, Set


class SavedInput:
    """
    A class to store an input and other useful information associated to the input.

    You may add any extra fields you need. You do not need to use all existing fields.
    """

    def __init__(
        self, input_data: bytes, edge_coverage: Set[Tuple[int, int]], runtime: float
    ):
        # The actual input
        self.data = input_data
        # The observed edge coverage of the input
        self.coverage = edge_coverage
        # The observed runtime of the input
        self.runtime = runtime
        # Tracks the time at which the input was discovered
        self.time_discovered = time.time()
        # Tracks the number of times the input has been chosen as a parent for mutation
        self.times_mutated = 0


def log(*args, **kwargs):
    """Log the fuzzing results"""
    current_time = time.strftime("%H:%M:%S", time.localtime())
    print(f"[{current_time}]", *args, **kwargs)


class Fuzzer(ABC):
    """
    Abstract base class for a fuzzer. Defines common methods.
    """

    def __init__(
        self,
        module_under_test,
        test_file_name: str,
        cov: coverage.Coverage,
        output_dir: str,
    ):
        # Keep track of coverage from non-error inputs
        self.edges_covered: Set[Tuple[int, int]] = set()
        # Keep track of coverage from error inputs
        self.edges_covered_failing: Set[Tuple[int, int]] = set()
        # Keep track of coverage achieved through time
        self.coverage_through_time: List[Tuple[float, int, int]] = []
        # Coverage-increasing non-error inputs
        self.saved_inputs: List[SavedInput] = []
        # Coverage-increasing error inputs
        self.failing_inputs: List[SavedInput] = []
        # Module object
        self.module_under_test = module_under_test
        # The test file in which module under test is defined
        self.test_file_name = test_file_name
        # coverage.Coverage object to keep track of coverage.
        self.cov = cov
        # fuzzing output directory.
        self.output_dir = output_dir

    def save_if_has_new_coverage(
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
        for edge in input_coverage:
            if edge not in self.edges_covered and not has_error:
                self.edges_covered = self.edges_covered.union(input_coverage)
                self.saved_inputs.append(
                    SavedInput(input_data, input_coverage, exec_time)
                )
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

    def exec_with_coverage(
        self, input_data: bytes
    ) -> Tuple[bool, Set[Tuple[int, int]], float]:
        """
        Runs the test_one_input function from `self.module_under_test` defined in `self.test_file_name` on the input `input_data`.

        Returns whether or not the input failed with an assertion error, the edges in `self.test_file_name` covered by the input,
        and the execution time.
        """
        self.cov.erase()
        has_error = False
        start_time = time.time()
        self.cov.start()
        try:
            self.module_under_test.test_one_input(input_data)
        except (AssertionError, IndexError):
            # We will let other errors percolate up for debugging purposes,
            # but they may reflect bugs found in the program under test.
            has_error = True
        self.cov.stop()
        exec_time = time.time() - start_time
        edges_covered = self.cov.get_data().arcs(self.test_file_name)

        return has_error, set(edges_covered), exec_time

    def save_data(self):
        """
        Saves the generated inputs, coverage over time, and coverage report
        to `self.output_dir`
        """
        log("Finalizing the fuzzing run...")
        # Add an end-of-run coverage measurement.
        self.coverage_through_time.append(
            (
                time.time(),
                len(self.edges_covered),
                len(self.edges_covered_failing),
            )
        )
        # Save all the inputs
        os.mkdir(os.path.join(self.output_dir, "saved_inputs"))
        for i, saved_input in enumerate(self.saved_inputs):
            input_file_name = os.path.join(
                self.output_dir, "saved_inputs", f"input_{i}"
            )
            with open(input_file_name, "wb") as input_file:
                input_file.write(saved_input.data)
        # Save the crashing inputs
        os.mkdir(os.path.join(self.output_dir, "crashing_inputs"))
        for i, saved_input in enumerate(self.failing_inputs):
            input_file_name = os.path.join(
                self.output_dir, "crashing_inputs", f"crashing_input_{i}"
            )
            with open(input_file_name, "wb") as input_file:
                input_file.write(saved_input.data)
        # Write the coverage over time CSV
        with open(
            os.path.join(self.output_dir, "coverage_through_time.csv"), "w"
        ) as coverage_csv:
            coverage_csv.write("absolute_time,edges_covered,crashing_edges_covered\n")
            for coverage_time, edges_covered, failing_covered in self.coverage_through_time:
                coverage_csv.write(f"{coverage_time},{edges_covered},{failing_covered}\n")
        log("Generating a coverage report...")
        # Create an coverage report
        self.cov.erase()
        self.cov.start()
        for saved_input in self.saved_inputs:
            self.module_under_test.test_one_input(saved_input.data)
        self.cov.stop()
        self.cov.html_report(
            directory=os.path.join(self.output_dir, "html_coverage_report")
        )

    @abstractmethod
    def fuzz(self, search_time: int):
        """
        Fuzz the test_one_input function defined in `self.module_to_fuzz`
        for time `search_time`.
        """
        return NotImplemented


class RandomFuzzer(Fuzzer):
    """
    A random fuzzer.
    """

    def generate_input(self) -> bytes:
        """
        Produce a new byte-level input.

        """
        input_len = random.randint(1, 1000)
        byte_seq = [random.randint(0, 255) for _ in range(input_len)]
        return bytes(byte_seq)

    def fuzz(self, search_time: int):
        """
        Fuzz the test_one_input function defined in `self.module_to_fuzz`
        for time `search_time`.
        """
        start_time = time.time()
        while time.time() - start_time < search_time:
            new_input = self.generate_input()
            has_error, input_cov, exec_time = self.exec_with_coverage(new_input)
            self.save_if_has_new_coverage(new_input, has_error, input_cov, exec_time)
        self.save_data()


class CoverageGuidedFuzzer(Fuzzer):
    """
    A coverage-guided fuzzer.
    """

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
        # Set up the initital inputs to populate `self.saved_inputs`
        for input_data in initial_inputs:
            has_error, input_cov, exec_time = self.exec_with_coverage(input_data)
            self.save_if_has_new_coverage(input_data, has_error, input_cov, exec_time)

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

    def mutate_input(self, input_data: bytes) -> bytes:
        """
        Produce a new byte-level input by mutating `input_data`.

        Note: this function should not alter the original `input_data` object.
        """
        mutated_data = [i for i in input_data]
        if len(input_data) == 0:
            mutation_type = "insert"
        else:
            mutation_type = random.choice(["overwrite", "delete", "insert"])
        if mutation_type == "overwrite":
            mutate_position = random.randint(0, len(input_data) - 1)
            mutate_len = random.randint(1, len(input_data) - mutate_position)
            for i in range(mutate_position, mutate_len + mutate_position):
                mutated_data[i] = random.randint(0, 255)
        elif mutation_type == "delete":
            mutate_start = random.randint(0, len(input_data) - 1)
            mutate_end = random.randint(0, len(input_data) - 1)
            mutated_data = mutated_data[:mutate_start] + mutated_data[mutate_end + 1 :]
        else:
            mutate_position = random.randint(0, len(input_data))
            mutate_len = random.randint(1, 10)
            new_data = [random.randint(0, 255) for _ in range(mutate_len)]
            mutated_data = (
                mutated_data[:mutate_position]
                + new_data
                + mutated_data[mutate_position + 1 :]
            )
        return bytes(mutated_data)

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
                        has_error, input_cov, exec_time = self.exec_with_coverage(
                            mutated_input
                        )
                        self.save_if_has_new_coverage(
                            mutated_input, has_error, input_cov, exec_time
                        )
                    saved_input.times_mutated += 1
        self.save_data()

class GrimoireFuzzer(Fuzzer):
    """
    A coverage-guided fuzzer.
    """

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
        # Set up the initital inputs to populate `self.saved_inputs`
        for input_data in initial_inputs:
            has_error, input_cov, exec_time = self.exec_with_coverage(input_data)
            self.save_if_has_new_coverage(input_data, has_error, input_cov, exec_time)

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

    def mutate_input(self, input_data: bytes) -> bytes:
        """
        Produce a new byte-level input by mutating `input_data`.

        Note: this function should not alter the original `input_data` object.
        """
        # n ← havoc_amount(input.performance())
        # 3 for i ← 0 to n do
        #     4 if input.is_generalized() then
        #         5 input_extension(input, generalized)
        #         6 recursive_replacement(input, generalized)
        #     string_replacement(content, strings)
        # return bytes(mutated_data)
        pass

    def random_generalized():
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
        pass

    def send_to_fuzzer(input):
        """
        implies that the fuzzer executes
        the target application with the mutated input. 
        It expects concrete inputs. Thus, mutations working
        on generalized inputs
        first replace all remaining  by an empty string
        """
        pass

    def input_extension(input, all_generalized):
        """
        we extend an generalized input by placing another randomly
        chosen generalized input, slice, token or string before and
        after the given one.
        """
        # 1 rand ← random_generalized(generalized_inputs)
        # 2 send_to_fuzzer(concat(input.content(), rand.content()))
        # 3 send_to_fuzzer(concat(rand.content(),input.content()))
        pass

    def recursive_replacement(input, generalized):
        # 1 input ← pad_with_gaps(input)
        # 2 for i ← 0 to random_power_of_two() do
        #     3 rand ← random_generalized(generalized_inputs)
        #     4 input ← replace_random_gap(input, rand)
        # 5 send_to_fuzzer(input.content())
        pass

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
                        has_error, input_cov, exec_time = self.exec_with_coverage(
                            mutated_input
                        )
                        self.save_if_has_new_coverage(
                            mutated_input, has_error, input_cov, exec_time
                        )
                        
                    saved_input.times_mutated += 1
        self.save_data()

"""
queue = [saved_input1, saved_input2, saved_input3, generalized_input1, generalized_input2, ...]
"""

def _read_input_dir(input_dir):
    """
    Read the data from the files in `input_dir` into an input set to seed coverage-guided fuzzing.
    """
    if not os.path.isdir(input_dir):
        raise ValueError(f"{input_dir} does not exist, cannot retrieve seed inputs")
    inputs = set()
    for filename in os.listdir(input_dir):
        full_name = os.path.join(input_dir, filename)
        if os.path.isfile(full_name):
            input_data = open(full_name, "rb").read()
            inputs.add(input_data)
    if len(inputs) == 0:
        raise ValueError(f"{input_dir} does not contain any readable files.")
    return inputs


def fuzz_main(args):
    """
    Sets up output/input directories, and delegates the fuzzing to a Fuzzer object.
    """
    log("Setting up fuzzing session...")
    # Set up output directory
    output_dir_name = args.output_dir
    if os.path.isdir(output_dir_name):
        raise ValueError(f"{output_dir_name} already exists, not overwriting")
    os.mkdir(output_dir_name)

    # Get the module under test
    module_under_test = importlib.import_module(args.module_to_fuzz)
    if not hasattr(module_under_test, "test_one_input") or not callable(
        module_under_test.test_one_input
    ):
        raise ValueError(
            f"No function named test_one_input in module {module_under_test}"
        )
    test_file_name = inspect.getfile(module_under_test)
    cov = coverage.Coverage(
        branch=True, data_file=os.path.join(output_dir_name, ".coverage")
    )

    if args.fuzzer == "RANDOM":
        fuzzer = RandomFuzzer(module_under_test, test_file_name, cov, args.output_dir)
    elif args.fuzzer == "COVERAGE":
        if args.input_dir is not None:
            inputs = _read_input_dir(args.input_dir)
        else:
            inputs = None
        fuzzer = CoverageGuidedFuzzer(
            module_under_test, test_file_name, cov, args.output_dir, inputs
        )
    elif args.fuzzer == "GRIMOIRE":
        if args.input_dir is not None:
            inputs = _read_input_dir(args.input_dir)
        else:
            inputs = None
        fuzzer = GrimoireFuzzer(
            module_under_test, test_file_name, cov, args.output_dir, inputs
        )

    # Run all the fuzzing
    log("Starting fuzzing session.")
    fuzzer.fuzz(args.time)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        add_help=False,
        description="Fuzz the `test_one_input` function in a given module. Tracks coverage of the given module achieved by fuzzing.",
    )
    parser.add_argument(
        "module_to_fuzz",
        type=str,
        help="the module to fuzz. Must contain function named `test_one_input`. Base directory for module must be on your PYTHONPATH",
    )
    parser.add_argument(
        "output_dir", type=str, help="directory in which to put output results"
    )

    parser.add_argument(
        "--fuzzer",
        type=str,
        choices=["RANDOM", "COVERAGE", "GRIMOIRE"],
        help="Which type of fuzzer to run",
        default="RANDOM",
    )
    parser.add_argument(
        "--input_dir",
        type=str,
        help="directory containing inputs to start coverage-guided fuzzing",
    )
    parser.add_argument(
        "--time", type=int, default=60, help="Search time for which to run fuzzing"
    )
    args = parser.parse_args()
    fuzz_main(args)
