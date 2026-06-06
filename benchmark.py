import timeit
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "backend")))

from rules.dice_engine import DiceEngine

def run_benchmark():
    setup = """
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "backend")))
from rules.dice_engine import DiceEngine
engine = DiceEngine()
"""
    stmt = "engine.roll('2d20+5')"

    number = 100000

    time_taken = timeit.timeit(stmt, setup=setup, number=number)
    print(f"Time taken for {number} rolls: {time_taken:.4f} seconds")

if __name__ == "__main__":
    run_benchmark()
