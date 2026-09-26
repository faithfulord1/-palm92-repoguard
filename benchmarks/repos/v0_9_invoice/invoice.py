from decimal import Decimal
from pricing import discounted_unit, round_currency


def invoice_total(lines: list[dict]) -> Decimal:
    """Each line: {price: decimal string, quantity: int, discount_percent: int}."""
    total = Decimal("0")
    for line in lines:
        # BUG: rounds a discounted unit before multiplying quantity.
        total += round_currency(discounted_unit(line["price"], line["discount_percent"])) * line["quantity"]
    return total
