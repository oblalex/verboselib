import unittest

from verboselib.helpers import to_language, to_locale


class HelpersTestCase(unittest.TestCase):

  def test_to_locale(self):
    self.assertEqual(to_locale("en-us"), "en_US")
    self.assertEqual(to_locale("sr-lat"), "sr_Lat")

  def test_to_language(self):
    self.assertEqual(to_language("EN"), "en")
    self.assertEqual(to_language("en_US"), "en-us")
    self.assertEqual(to_language("sr_Lat"), "sr-lat")
