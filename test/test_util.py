import unittest
from models.Blank import Blank
from models.GeneralizedInput import GeneralizedInput
from util.util import random_slice, random


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



if __name__ == '__main__':
    unittest.main()
