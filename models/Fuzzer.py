from abc import ABC, abstractmethod
from typing import Callable, Tuple, List, Set, Union
import coverage
import time
import os

from models.SavedInput import SavedInput
from util.util import log


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
