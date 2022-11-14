import time
from typing import Tuple, Set

from models.GeneralizedInput import GeneralizedInput
from util.util import bytes_to_str


class SavedInput:
    """
    A class to store an input and other useful information associated to the input.

    You may add any extra fields you need. You do not need to use all existing fields.
    """

    def __init__(
        self, input_data: bytes, edge_coverage: Set[Tuple[int, int]], runtime: float, generalized: GeneralizedInput = None
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
        self.generalized = generalized

    def to_map(self):
        return {
            "data": bytes_to_str(self.data),
            "generalized": self.generalized.to_map() if self.generalized is not None else {}
        }
