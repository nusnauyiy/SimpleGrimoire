import unittest

from util.splitting_rules import split_overlapping_chunksize


class SplittingRulesTest(unittest.TestCase):
    def setUp(self):
        self.chunk_sizes = [256, 128, 64, 32, 2, 1]

    def _test_split_overlapping_chunksize(self, input_bytes: bytes, start: int):
        for chunk_size in self.chunk_sizes:
            split_fn = split_overlapping_chunksize(chunk_size)

            expected = len(input_bytes)
            if start + chunk_size < len(input_bytes):
                expected = start + chunk_size

            actual = split_fn(input_bytes, start)
            self.assertEqual(expected, actual)

    def test_split_overlapping_chunksize(self):
        self._test_split_overlapping_chunksize(b"hello", 0)
        self._test_split_overlapping_chunksize(b"hello", 1)
        self._test_split_overlapping_chunksize(b"hello", 4)
        self._test_split_overlapping_chunksize(b"a" * 1000, 0)
        self._test_split_overlapping_chunksize(b"a" * 1000, 800)



if __name__ == '__main__':
    unittest.main()