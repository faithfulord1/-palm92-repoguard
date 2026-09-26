from decimal import Decimal, ROUND_HALF_UP


def discounted_unit(price: str, discount_percent: int) -> Decimal:
    """Return the discounted unit price without rounding."""
    return Decimal(price) * (Decimal(100 - discount_percent) / Decimal(100))


def round_currency(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
