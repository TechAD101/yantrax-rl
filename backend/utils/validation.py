import re
from flask import abort

# Allow A-Z, 0-9, dot, hyphen. Max 20 chars.
SYMBOL_PATTERN = re.compile(r'^[A-Z0-9.\-]{1,20}$')

def validate_symbol(symbol: str) -> str:
    """
    Validates the stock symbol to prevent injection attacks.
    Allows uppercase letters, numbers, dots, and hyphens.
    Max length 20.
    """
    if not symbol:
        abort(400, description="Symbol cannot be empty")

    s = symbol.upper()

    if not SYMBOL_PATTERN.match(s):
        abort(400, description=f"Invalid symbol format: {s}")

    return s
