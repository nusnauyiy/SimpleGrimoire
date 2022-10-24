import coverage
import random
import time
from typing import Set

from models.SavedInput import SavedInput
from models.Fuzzer import Fuzzer


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
            mutated_data = mutated_data[:mutate_start] + mutated_data[mutate_end + 1:]
        else:
            mutate_position = random.randint(0, len(input_data))
            mutate_len = random.randint(1, 10)
            new_data = [random.randint(0, 255) for _ in range(mutate_len)]
            mutated_data = (
                    mutated_data[:mutate_position]
                    + new_data
                    + mutated_data[mutate_position + 1:]
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
