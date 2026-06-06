import pytest
from backend.rules.dice_engine import DiceEngine

def test_dice_engine_deterministic():
    # Using a fixed seed should produce the same results
    engine1 = DiceEngine(seed=42)
    result1 = engine1.roll("1d20")

    engine2 = DiceEngine(seed=42)
    result2 = engine2.roll("1d20")

    assert result1["rolls"] == result2["rolls"]
    assert result1["total"] == result2["total"]

def test_basic_roll():
    engine = DiceEngine(seed=42)
    result = engine.roll("1d20")

    assert "total" in result
    assert "rolls" in result
    assert "formula" in result
    assert "notation" in result

    assert len(result["rolls"]) == 1
    assert 1 <= result["total"] <= 20
    assert result["formula"] == "1d20"
    assert result["notation"] == "1d20"

def test_roll_with_positive_modifier():
    engine = DiceEngine(seed=42)
    result = engine.roll("2d6+5")

    assert len(result["rolls"]) == 2
    assert result["total"] == sum(result["rolls"]) + 5
    assert result["formula"] == "2d6+5"
    assert result["notation"] == "2d6+5"

def test_roll_with_negative_modifier():
    engine = DiceEngine(seed=42)
    result = engine.roll("3d8-2")

    assert len(result["rolls"]) == 3
    assert result["total"] == sum(result["rolls"]) - 2
    assert result["formula"] == "3d8-2"
    assert result["notation"] == "3d8-2"

def test_whitespace_tolerance():
    engine = DiceEngine(seed=42)
    result = engine.roll("  2 d 6 +  1 ")

    assert len(result["rolls"]) == 2
    assert result["total"] == sum(result["rolls"]) + 1
    assert result["formula"] == "2d6+1"
    assert result["notation"] == "2d6+1"  # Note: The engine strips spaces

def test_invalid_notation():
    engine = DiceEngine()

    with pytest.raises(ValueError, match="Invalid notation"):
        engine.roll("invalid")

    with pytest.raises(ValueError, match="Invalid notation"):
        engine.roll("d20")

    with pytest.raises(ValueError, match="Invalid notation"):
        engine.roll("1d")

    with pytest.raises(ValueError, match="Invalid notation"):
        engine.roll("1x20")

def test_exceeding_limits():
    engine = DiceEngine()

    with pytest.raises(ValueError, match="Limits exceeded"):
        engine.roll("101d20")

    with pytest.raises(ValueError, match="Limits exceeded"):
        engine.roll("1d1001")
