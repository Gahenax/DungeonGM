from typing import Dict, Any

class CombatEngine:
    def __init__(self, dice_engine):
        self.dice_engine = dice_engine
        self.current_round = 1
    
    def resolve_attack(
        self,
        attacker: Dict[str, Any],
        defender: Dict[str, Any],
        damage_dice: str = "1d8"
    ) -> Dict[str, Any]:
        to_hit_bonus = attacker.get('bonus_to_hit', 0)
        attack_roll = self.dice_engine.roll(f"1d20+{to_hit_bonus}")
        
        defender_ac = defender.get('ac', 10)
        hit = attack_roll['total'] >= defender_ac
        
        damage = 0
        if hit:
            damage_roll = self.dice_engine.roll(damage_dice)
            damage = damage_roll['total']
        
        return {
            "hit": hit,
            "attack_roll": attack_roll['total'],
            "defender_ac": defender_ac,
            "damage": damage
        }
