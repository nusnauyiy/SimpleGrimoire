import unittest

from util.splitting_rules import *


class SplittingRulesTest(unittest.TestCase):
    def setUp(self):
        pass

    def test_find_next_char(self):
        #             0    1    2    3                  4    5    6    7    8    9    10   11                   12              13   14   15   16
        input_data = ["h", "e", "l", Blank.get_blank(), "l", "o", "(", "w", "o", "r", ")", Blank.get_blank(), Blank.get_blank(), "l", "d", ")", "!"]
        expected = 11
        actual = find_next_char(input_data, 0, ")")
        self.assertEqual(expected, actual)

        expected = 16
        actual = find_next_char(input_data, 11, ")")
        self.assertEqual(expected, actual)

    def test_find_closures(self):
        #             0    1    2    3                  4    5    6    7    8    9    10   11                   12              13   14   15   16
        input_data = ["h", "e", "l", Blank.get_blank(), "l", "o", "(", "w", "o", "r", ")", Blank.get_blank(), Blank.get_blank(), "l", "d", ")", "!"]
        expected = (6, [16, 11])  # ends are exclusive (one index after the closing char)
        actual = find_closures(input_data, 0, "(", ")")
        # find_gaps_in_closures(input_data, old_node, default_info, find_closures, "(", ")")
        self.assertEqual(expected, actual)

    def test_find_gaps(self):
        def candidate_check(input_bytes: bytes) -> bool:
            valid_candidates = [b"hello,my,", b"my,world"]
            return input_bytes in valid_candidates

        #            |     first split (True)                       |second (False)|              third (True)                                      |
        input_data = ["h", "e", "l", Blank.get_blank(), "l", "o", ",", "m", "y", ",", "w", "o", "r", Blank.get_blank(), Blank.get_blank(), "l", "d"]
        cumulative = True
        expected = [Blank.get_blank(removed=b"hello,"), "m", "y", ",", "w", "o", "r", Blank.get_blank(), "l", "d"]
        result = find_gaps(input_data.copy(), Blank.DELETE, candidate_check, find_next_char, ",", cumulative)
        self.assertEqual(expected, result)

        cumulative = False
        expected = [Blank.get_blank(removed=b"hello,"), "m", "y", ",", Blank.get_blank(removed=b"world")]
        result = find_gaps(input_data.copy(), Blank.DELETE, candidate_check, find_next_char, ",", cumulative)
        self.assertEqual(expected, result)

    def test_find_gaps_in_closures(self):
        #             0    1    2    3                  4    5    6    7    8    9    10   11                   12              13   14   15   16
        input_data = ["h", "e", "l", Blank.get_blank(), "l", "o", "(", "w", "o", "r", ")", Blank.get_blank(), Blank.get_blank(), "l", "d", ")", "!"]

        def candidate_check(input_bytes: bytes) -> bool:
            valid_candidates = [b"hello!", b"hellold)!"]
            return input_bytes in valid_candidates

        cumulative = True
        expected = ["h", "e", "l", Blank.get_blank(), "l", "o", Blank.get_blank(removed=b"(wor)ld)"), "!"]
        result = find_gaps_in_closures(input_data.copy(), Blank.DELETE, candidate_check, find_closures, "(", ")", cumulative)
        self.assertEqual(expected, result)

        cumulative = False
        result = find_gaps_in_closures(input_data.copy(), Blank.DELETE, candidate_check, find_closures, "(", ")", cumulative)
        self.assertEqual(expected, result)


    def test_find_gaps_in_closures_2(self):
        #             0    1    2    3    4    5    6    7    8    9    10   11   12   13   14   15
        input_data = ["(", "h", "e", "l", "l", "o", ")", "(", "w", "o", "r", ")", "l", "d", ")", "!"]
        def candidate_check(input_bytes: bytes) -> bool:
            valid_candidates = [b"(hello)!", b"(wor)ld)!"]
            return input_bytes in valid_candidates

        cumulative = True
        expected = [Blank.get_blank(removed=b"(hello)"), "(", "w", "o", "r", ")", "l", "d", ")", "!"]
        result = find_gaps_in_closures(input_data.copy(), Blank.DELETE, candidate_check, find_closures, "(", ")", cumulative)
        print(f"{GeneralizedInput(expected).pretty_print()} {GeneralizedInput(result).pretty_print()}")
        self.assertEqual(expected, result)

        cumulative = False
        expected = [Blank.get_blank(removed=b"(hello)(wor)ld)"), "!"]
        result = find_gaps_in_closures(input_data.copy(), Blank.DELETE, candidate_check, find_closures, "(", ")", cumulative)
        self.assertEqual(expected, result)

if __name__ == '__main__':
    unittest.main()
