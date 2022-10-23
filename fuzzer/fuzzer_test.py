import importlib
import unittest
import coverage
from unittest.mock import Mock
from typing import Set, Tuple
import os

from grimoire_fuzzer import GeneralizedInput, GrimoireFuzzer, Blank

class GrimoireFuzzerTest(unittest.TestCase):
    def setUp(self) -> None:
        # cov = coverage.Coverage(
        # branch=True, data_file = os.path.join("output.coverage")
        # )
        # module_under_test = importlib.import_module("benchmarks.quicksort")
        # self.fuzzer = GrimoireFuzzer(module_under_test, "filename", cov, "outputdirs", None)
        pass

    # def test_generalize(self):
    #     values = {"ab": (False, Set(), 1), "cd": (False, Set(Tuple(1, 2)), 1)}
    #     def side_effect(arg):
    #         return values[arg]
    #     mock = Mock(side_effect=side_effect)
    #     self.fuzzer.exec_with_coverage = mock
    #     self.fuzzer.generalize("abcd", Set(Tuple(1, 2)))
    #     self.assertEqual(self.fuzzer.generalized, [])

    def test_GeneralizedInput_get_bytes(self):
        generalized_input = GeneralizedInput([b"hello world"])
        self.assertEqual(b"hello world", generalized_input.get_bytes())

        generalized_input = GeneralizedInput([b"hello", Blank(), b"world"])
        self.assertEqual(b"helloworld", generalized_input.get_bytes())

        generalized_input = GeneralizedInput([Blank(), b"hello", Blank(), b"world", Blank()])
        self.assertEqual(b"helloworld", generalized_input.get_bytes())
    
    def test_GrimoireFuzzer_random_slice(self):


if __name__ == '__main__':
    unittest.main()
