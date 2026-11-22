import unittest

from slug import slugify


class SlugTests(unittest.TestCase):
    def test_ascii(self):
        self.assertEqual(slugify("  Hello,   world! "), "hello-world")

    def test_turkish(self):
        self.assertEqual(slugify("İstanbul, Çağrı ve Işık!"), "istanbul-cagri-ve-isik")
