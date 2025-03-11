import re
from decimal import ROUND_HALF_UP, Decimal


def gen_slug(name: str) -> str:
    return re.sub(r"[ _]+", "-", re.sub(r"[^\w -]+", "", name)).lower()


def format_decimal(value: Decimal, decimals: int = 2) -> str:
    quantize_str = "0." + "0" * decimals
    quantized = value.quantize(Decimal(quantize_str), rounding=ROUND_HALF_UP)
    return str(quantized)
