import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.rules.dice_engine import DiceEngine

class TestDiceEngine(unittest.TestCase):
    def setUp(self):
        self.engine = DiceEngine()

    def test_invalid_notation(self):
        invalid_notations = ["invalid", "d20", "20", "1d", "abc"]
        for notation in invalid_notations:
            with self.subTest(notation=notation):
                with self.assertRaises(ValueError):
                    self.engine.roll(notation)

if __name__ == '__main__':
    unittest.main()
