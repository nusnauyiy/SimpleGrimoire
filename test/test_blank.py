import unittest

from models import Blank
from models.Blank import Blank, DeleteBlank, ReplaceBlank, ReplaceClass


class BlankTest(unittest.TestCase):

    def test_get_blank_delete(self):
        output = Blank.get_blank()
        self.assertTrue(isinstance(output, Blank))
        self.assertTrue(isinstance(output, DeleteBlank))
        output = Blank.get_blank(blank_type=Blank.REPLACE)
        self.assertTrue(isinstance(output, Blank))
        self.assertTrue(isinstance(output, ReplaceBlank))

    def test_append_byte(self):
        test_blank_1 = Blank.get_blank(removed=b"hello")
        test_blank_1.append(b"world")
        self.assertEqual(test_blank_1, Blank.get_blank(removed=b"helloworld"))

    def test_append_str(self):
        test_blank_1 = Blank.get_blank(removed=b"hello")
        test_blank_1.append("world")
        self.assertEqual(test_blank_1, Blank.get_blank(removed=b"helloworld"))

    def test_append_str(self):
        test_blank_1 = Blank.get_blank(removed=b"hello")
        test_blank_1.append(Blank.get_blank(removed=b"world"))
        self.assertEqual(test_blank_1, Blank.get_blank(removed=b"helloworld"))


class ReplaceClassTest(unittest.TestCase):
    # manually check this
    def test_generate(self):
        for replace_class in ReplaceClass:
            ans = ReplaceClass.generate(replace_class)
            print(f"replace class: {replace_class.name}")
            print(f"generated: {ans}")


class ReplaceBlankTest(unittest.TestCase):
    def setUp(self):
        pass
