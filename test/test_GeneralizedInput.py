import unittest

from models.Blank import Blank
from models.GeneralizedInput import GeneralizedInput


class GeneralizedInputTest(unittest.TestCase):
    def test_GeneralizedInput_get_bytes(self):
        generalized_input = GeneralizedInput([b"hello world"])
        self.assertEqual(b"hello world", generalized_input.get_bytes())

        generalized_input = GeneralizedInput([b"hello", Blank(), b"world"])
        self.assertEqual(b"helloworld", generalized_input.get_bytes())

        generalized_input = GeneralizedInput([Blank(), b"hello", Blank(), b"world", Blank()])
        self.assertEqual(b"helloworld", generalized_input.get_bytes())

    def test_GeneralizedInput_merge_adjacent_gaps(self):
        # no merge
        generalized_input = GeneralizedInput([b"hello", Blank(), b"world"])
        expected = GeneralizedInput([b"hello", Blank(), b"world"])
        generalized_input.merge_adjacent_gaps()
        self.assertEqual(expected, generalized_input)

        # one merge
        generalized_input = GeneralizedInput([b"hello", Blank(), Blank(), b"world"])
        expected = GeneralizedInput([b"hello", Blank(), b"world"])
        generalized_input.merge_adjacent_gaps()
        self.assertEqual(expected, generalized_input)

        # three blanks
        generalized_input = GeneralizedInput([b"hello", Blank(), Blank(), b"world", ])
        expected = GeneralizedInput([b"hello", Blank(), b"world"])
        generalized_input.merge_adjacent_gaps()
        self.assertEqual(expected, generalized_input)

if __name__ == '__main__':
    unittest.main()
