"""Tests for INR formatting."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from utils.formatting import format_inr, format_number


def test_format_inr():
    assert format_inr(1250000) == "Rs 1,250,000.00"
    assert format_inr(0) == "Rs 0.00"
    assert "Rs" in format_inr(99.5)


def test_format_number():
    assert format_number(1500) == "1,500"
    assert format_number(3.5) == "3.50"
