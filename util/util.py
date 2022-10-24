import random
import time
from typing import List

from models.Blank import Blank
from models.GeneralizedInput import GeneralizedInput


def log(*args, **kwargs):
    """Log the fuzzing results"""
    current_time = time.strftime("%H:%M:%S", time.localtime())
    print(f"[{current_time}]", *args, **kwargs)


"""
GRIMOIRE-specific helpers
"""


def random_slice(generalized: List[GeneralizedInput]) -> GeneralizedInput:
    """
    select a substring between two arbitrary blanks in a generalized input
    """
    chosen = random.choice(generalized).input
    blank_indices = [i for i in range(len(chosen)) if isinstance(chosen[i], Blank)]
    blank_indices.extend([-1, len(chosen)])  # consider the beginning and end of the string a blank
    boundaries = random.sample(blank_indices, 2)
    start = min(boundaries)
    end = max(boundaries)
    return GeneralizedInput(chosen[start + 1:end])  # does not include start and end blanks
