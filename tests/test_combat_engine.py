import unittest
from unittest.mock import Mock
from backend.rules.combat_engine import CombatEngine

class TestCombatEngine(unittest.TestCase):
    def setUp(self):
        self.mock_dice_engine = Mock()
        self.combat_engine = CombatEngine(self.mock_dice_engine)

    def test_successful_hit(self):
        # Setup mock behavior
        self.mock_dice_engine.roll.side_effect = [
            {'total': 15, 'rolls': [13], 'modifier': 2}, # Attack roll
            {'total': 6, 'rolls': [6], 'modifier': 0}    # Damage roll
        ]

        attacker = {"bonus_to_hit": 2, "attack_mod": 2}
        defender = {"ac": 14}

        result = self.combat_engine.resolve_attack(attacker, defender)

        self.assertTrue(result["hit"])
        self.assertEqual(result["attack_roll"], 15)
        self.assertEqual(result["defender_ac"], 14)
        self.assertEqual(result["damage"], 6)

        # Verify mock calls
        self.assertEqual(self.mock_dice_engine.roll.call_count, 2)
        self.mock_dice_engine.roll.assert_any_call("1d20+2")
        self.mock_dice_engine.roll.assert_any_call("1d8")

    def test_miss(self):
        # Setup mock behavior for miss
        self.mock_dice_engine.roll.return_value = {'total': 10, 'rolls': [8], 'modifier': 2}

        attacker = {"bonus_to_hit": 2, "attack_mod": 2}
        defender = {"ac": 14}

        result = self.combat_engine.resolve_attack(attacker, defender)

        self.assertFalse(result["hit"])
        self.assertEqual(result["attack_roll"], 10)
        self.assertEqual(result["defender_ac"], 14)
        self.assertEqual(result["damage"], 0)

        # Verify mock was only called once
        self.mock_dice_engine.roll.assert_called_once_with("1d20+2")

    def test_default_values(self):
        # Setup mock behavior
        self.mock_dice_engine.roll.side_effect = [
            {'total': 12, 'rolls': [12], 'modifier': 0}, # Attack roll
            {'total': 4, 'rolls': [4], 'modifier': 0}    # Damage roll
        ]

        # Empty dicts should trigger default values
        attacker = {}
        defender = {}

        result = self.combat_engine.resolve_attack(attacker, defender)

        self.assertTrue(result["hit"]) # 12 >= 10 (default AC)
        self.assertEqual(result["attack_roll"], 12)
        self.assertEqual(result["defender_ac"], 10)
        self.assertEqual(result["damage"], 4)

        self.assertEqual(self.mock_dice_engine.roll.call_count, 2)
        self.mock_dice_engine.roll.assert_any_call("1d20+0")
        self.mock_dice_engine.roll.assert_any_call("1d8")

if __name__ == '__main__':
    unittest.main()
