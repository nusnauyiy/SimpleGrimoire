import random
import time

from models.Fuzzer import Fuzzer


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
