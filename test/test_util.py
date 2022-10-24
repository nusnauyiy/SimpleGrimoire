import unittest
import random
from typing import List, Set

from models.Blank import Blank
from models.GeneralizedInput import GeneralizedInput
from util.grimoire_util import random_slice, random_generalized


class UtilTest(unittest.TestCase):
    def setUp(self):
        self.input1 = GeneralizedInput([b"hello", b"world"])
        self.input2 = GeneralizedInput([b"hello", Blank(), b"world"])
        self.input3 = GeneralizedInput([b"hello", Blank(), b"world", Blank(), b"bye", Blank(), b"world"])

    def test_random_slice_no_blank(self):
        answer = random_slice([self.input1]).input
        self.assertEqual([b"hello", b"world"], answer)

    def test_random_slice_has_blank(self):
        random.seed(5)
        answer = random_slice([self.input1, self.input2]).input
        self.assertEqual(b"hello", answer[0])
        self.assertTrue(isinstance(answer[1], Blank))
        self.assertEqual(b"world", answer[2])

    def test_random_slice_trimmed(self):
        random.seed(5)
        answer = random_slice([self.input1, self.input3]).input
        self.assertEqual(b"world", answer[0])
        self.assertTrue(isinstance(answer[1], Blank))
        self.assertEqual(b"bye", answer[2])

    def test_random_generalized(self):
        # not the most robust test but should catch most cases
        generalized = [self.input1, self.input2, self.input3]
        strings: List[bytes] = [b"token1", b"token2"]
        generalized_slices: List[GeneralizedInput] = [
            self.input1,
            GeneralizedInput([b"hello"]),
            GeneralizedInput([b"world"]),
            GeneralizedInput([b"bye"]),
            GeneralizedInput([b"hello", Blank(), b"world"]),
            GeneralizedInput([b"world", Blank(), b"bye"]),
            GeneralizedInput([b"bye", Blank(), b"world"]),
            GeneralizedInput([b"hello", Blank(), b"world", Blank(), b"bye"]),
            GeneralizedInput([b"world", Blank(), b"bye", Blank(), b"world"])
        ]
        all_possible = generalized + strings + generalized_slices
        for i in range(30):
            rand = random_generalized(generalized, strings)
            print(f"rand: {rand}")
            self.assertTrue(rand in all_possible)


if __name__ == '__main__':
    unittest.main()
