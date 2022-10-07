import importlib
import unittest
import coverage
from unittest.mock import Mock
from typing import Set, Tuple
from benchmarks import quicksort
import os

from fuzzer import GrimoireFuzzer

class GrimoireFuzzerTest(unittest.TestCase):
    def setUp(self) -> None:
        cov = coverage.Coverage(
        branch=True, data_file = os.path.join("output.coverage")
    )
        self.fuzzer = GrimoireFuzzer(quicksort, "filename", cov, "outputdirs", None)

    def test_generalize(self):
        values = {"ab": (False, Set(), 1), "cd": (False, Set(Tuple(1, 2)), 1)}
        def side_effect(arg):
            return values[arg]
        mock = Mock(side_effect=side_effect)
        self.fuzzer.exec_with_coverage = mock
        self.fuzzer.generalize("abcd", Set(Tuple(1, 2)))
        self.assertEqual(self.fuzzer.generalized, [])

if __name__ == '__main__':
    unittest.main()
