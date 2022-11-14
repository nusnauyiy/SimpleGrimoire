import random
import unittest
from typing import List

from models.Blank import Blank
from models.GeneralizedInput import GeneralizedInput
from util.grimoire_util import random_slice, random_generalized, generic_generalized
from util.util import find_all_overlapping_substr, find_all_nonoverlapping_substr, replace_all_instances, \
    replace_random_instance, find_random_substring


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
            # print(f"rand: {rand}")
            self.assertTrue(rand in all_possible)

    def test_find_all_overlapping_substr(self):
        input_bytes = b"ababababa"
        pattern = b"aba"
        expected = [(0, 3), (2, 5), (4, 7), (6, 9)]
        actual = find_all_overlapping_substr(input_bytes, pattern)
        self.assertTrue(expected == actual)

    def test_find_all_nonoverlapping_substr(self):
        input_bytes = b"ababababa"
        pattern = b"aba"
        expected = [(0, 3), (4, 7)]
        actual = find_all_nonoverlapping_substr(input_bytes, pattern)
        self.assertEqual(expected, actual)

        input_bytes = b"()("
        pattern = b"("
        expected = [(0, 1), (2, 3)]
        actual = find_all_nonoverlapping_substr(input_bytes, pattern)
        self.assertEqual(expected, actual)

    def test_find_random_substring(self):
        input_bytes = b"abcdef"
        strings = [b'a', b'c', b'z']
        expected_possibilities = {b'a', b'c'}
        for i in range(10):
            actual = find_random_substring(input_bytes, strings)
            # print(f"actual: {actual}")
            self.assertTrue(actual in expected_possibilities)

        strings = [b'z']
        actual = find_random_substring(input_bytes, strings)
        self.assertEqual(None, actual)

    def test_replace_random_instance(self):
        # not the most robust test but should catch most cases
        input_bytes = b"ababababa"
        pattern = b"aba"
        replace_bytes = b"c"
        expected_possibilities = {
            b"cbababa",
            b"ababcba"
        }
        for i in range(10):
            actual = replace_random_instance(input_bytes, pattern, replace_bytes)
            # print(f"actual: {actual}")
            self.assertTrue(actual in expected_possibilities)

    def test_replace_all_instances(self):
        input_bytes = b"ababababa"
        pattern = b"aba"
        replace_bytes = b"c"
        expected = b"cbcba"
        actual = replace_all_instances(input_bytes, pattern, replace_bytes)
        self.assertEqual(expected, actual)

    def test_generic_generalized(self):
        def generator() -> bool:
            results = [True, False, True, False, True, False]
            for result in results:
                yield result

        input_data = b"hello world"
        gen = generator()

        def candidate_check(input_bytes: bytes) -> bool:
            return next(gen)

        result = generic_generalized(input_data, candidate_check).input
        self.assertTrue(isinstance(result[0], Blank)) # eyyyyy :D
        self.assertTrue(isinstance(result[2], Blank))
        self.assertTrue(isinstance(result[4], Blank))
        self.assertEqual(result[1], b"ll")
        self.assertEqual(result[3], b"wo")
        self.assertEqual(result[5], b"d")

        pass


if __name__ == '__main__':
    unittest.main()
