import unittest

from util.splitting_rules import *


class SplittingRulesTest(unittest.TestCase):
    def setUp(self):
        self.chunk_sizes = [256, 128, 64, 32, 2, 1]

    def _test_split_overlapping_chunk_size(self, input_bytes: bytes, start: int):
        for chunk_size in self.chunk_sizes:
            split_fn = split_overlapping_chunk_size(chunk_size)

            expected = len(input_bytes)
            if start + chunk_size < len(input_bytes):
                expected = start + chunk_size

            actual = split_fn(input_bytes, start)
            self.assertEqual(expected, actual)

    def test_split_overlapping_chunk_size(self):
        self._test_split_overlapping_chunk_size(b"hello", 0)
        self._test_split_overlapping_chunk_size(b"hello", 1)
        self._test_split_overlapping_chunk_size(b"hello", 4)
        self._test_split_overlapping_chunk_size(b"a" * 1000, 0)
        self._test_split_overlapping_chunk_size(b"a" * 1000, 800)

    def test_find_next_char(self):
        #             0    1    2    3        4    5    6    7    8    9    10   11       12       13   14   15   16
        input_data = ["h", "e", "l", Blank(), "l", "o", "(", "w", "o", "r", ")", Blank(), Blank(), "l", "d", ")", "!"]
        expected = 11
        actual = find_next_char(input_data, 0, ")")
        self.assertEqual(expected, actual)

        expected = 16
        actual = find_next_char(input_data, 11, ")")
        self.assertEqual(expected, actual)

    def test_find_closures(self):
        #             0    1    2    3        4    5    6    7    8    9    10   11       12       13   14   15   16
        input_data = ["h", "e", "l", Blank(), "l", "o", "(", "w", "o", "r", ")", Blank(), Blank(), "l", "d", ")", "!"]
        expected = (6, [16, 11])  # ends are exclusive (one index after the closing char)
        actual = find_closures(input_data, 0, "(", ")")
        # find_gaps_in_closures(input_data, old_node, default_info, find_closures, "(", ")")
        self.assertEqual(expected, actual)

    def test_find_gaps(self):
        def generator() -> bool:
            results = [
                True,
                False,
                True
            ]
            for result in results:
                yield result
        #            |     first split (True)              |second (False)|              third (True)               |
        input_data = ["h", "e", "l", Blank(), "l", "o", ",", "m", "y", ",", "w", "o", "r", Blank(), Blank(), "l", "d"]
        gen = generator()

        def candidate_check(input_bytes: bytes) -> bool:
            return next(gen)

        expected = [Blank(b"hello,"), "m", "y", ",", Blank(b"world")]
        result = find_gaps(input_data, candidate_check, find_next_char, ",")
        self.assertEqual(expected, result)

    def test_find_gaps_in_closures(self):
        def generator() -> bool:
            results = [
                True,
                False,
                True,
                False
            ]
            for result in results:
                yield result

        #             0    1    2    3        4    5    6    7    8    9    10   11       12       13   14   15   16
        input_data = ["h", "e", "l", Blank(), "l", "o", "(", "w", "o", "r", ")", Blank(), Blank(), "l", "d", ")", "!"]
        gen = generator()

        def candidate_check(input_bytes: bytes) -> bool:
            return next(gen)

        expected = ["h", "e", "l", Blank(), "l", "o", Blank(b"(wor)ld)"), "!"]
        result = find_gaps_in_closures(input_data, candidate_check, find_closures, "(", ")")
        self.assertEqual(expected, result)


if __name__ == '__main__':
    unittest.main()
