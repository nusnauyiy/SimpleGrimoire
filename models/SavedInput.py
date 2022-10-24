import time
from typing import Callable, Tuple, List, Set, Union


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
