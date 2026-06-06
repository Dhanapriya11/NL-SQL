"""Display formatting helpers (Indian Rupees, numbers)."""

from __future__ import annotations

from config.constants import CURRENCY_LABEL


def format_inr(amount: float | int | None) -> str:
    """Format amount as Indian Rupees (Rs)."""
    if amount is None:
        return f"{CURRENCY_LABEL} 0"
    return f"{CURRENCY_LABEL} {float(amount):,.2f}"


def format_number(value: float | int | None) -> str:
    """Format plain numbers with thousands separator."""
    if value is None:
        return "0"
    if isinstance(value, int) or (isinstance(value, float) and value == int(value)):
        return f"{int(value):,}"
    return f"{float(value):,.2f}"
