import random
import re
from typing import Dict, List, Any

class DiceEngine:
    def __init__(self, seed=None):
        if seed:
            random.seed(seed)
    
    def roll(self, notation: str) -> Dict[str, Any]:
        """Roll dice: 1d20+5, 2d6-1, etc."""
        notation = notation.strip().replace(" ", "")
        
        match = re.match(r'(\d+)d(\d+)(?:([+-])(\d+))?', notation)
        if not match:
            raise ValueError(f"Invalid notation: {notation}")
        
        num_dice = int(match.group(1))
        die_size = int(match.group(2))
        modifier_sign = match.group(3) or '+'
        modifier = int(match.group(4)) if match.group(4) else 0
        
        if num_dice > 100 or die_size > 1000:
            raise ValueError("Limits exceeded")
        
        rolls = [random.randint(1, die_size) for _ in range(num_dice)]
        total = sum(rolls)
        
        if modifier_sign == '+':
            total += modifier
        else:
            total -= modifier
        
        formula = f"{num_dice}d{die_size}"
        if modifier != 0:
            formula += f"{modifier_sign}{modifier}"
        
        return {
            "total": total,
            "rolls": rolls,
            "formula": formula,
            "notation": notation
        }
