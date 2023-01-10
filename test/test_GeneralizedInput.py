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

    def test_GeneralizedInput_merge_adjacent_gaps_and_bytes(self):
        # no merge
        generalized_input = GeneralizedInput([b"hello", Blank(), b"world"])
        expected = GeneralizedInput([b"hello", Blank(), b"world"])
        generalized_input.merge_adjacent_gaps_and_bytes()
        self.assertEqual(expected, generalized_input)

        # one merge
        generalized_input = GeneralizedInput([b"hello", Blank(), Blank(), b"world"])
        expected = GeneralizedInput([b"hello", Blank(), b"world"])
        generalized_input.merge_adjacent_gaps_and_bytes()
        self.assertEqual(expected, generalized_input)

        # three blanks
        generalized_input = GeneralizedInput([b"hello", Blank(), Blank(), b"world", ])
        expected = GeneralizedInput([b"hello", Blank(), b"world"])
        generalized_input.merge_adjacent_gaps_and_bytes()
        self.assertEqual(expected, generalized_input)

        # no merge
        generalized_input = GeneralizedInput([b"hello", Blank(), b"world", b"!!"])
        expected = GeneralizedInput([b"hello", Blank(), b"world!!"])
        generalized_input.merge_adjacent_gaps_and_bytes()
        self.assertEqual(expected, generalized_input)

        # merge two blanks with removed text
        generalized_input = GeneralizedInput([b"hello", Blank(b" there"), Blank(b"!! "), b"world"])
        expected = GeneralizedInput([b"hello", Blank(b" there!! "), b"world"])
        generalized_input.merge_adjacent_gaps_and_bytes()
        self.assertEqual(expected, generalized_input)

    def test_GeneralizedInput_to_exploded_input(self):
        generalized_input = GeneralizedInput([b"Hello"])
        expected = ["H", "e", "l", "l", "o"]
        actual = generalized_input.to_exploded_input()
        self.assertEqual(expected, actual)

    def test_GeneralizedInput_init_exploded_input(self):
        generalized_input = GeneralizedInput(["H", "e", "l", "l", "o", Blank(), "w", "o", "r", "l", "d"], True)
        expected = [b"Hello", Blank(), b"world"]
        self.assertEqual(expected, generalized_input.input)


if __name__ == '__main__':
    unittest.main()
