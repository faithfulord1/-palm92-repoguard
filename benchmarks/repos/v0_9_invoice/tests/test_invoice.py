from decimal import Decimal
from invoice import invoice_total


def test_quantity_discount_round_once_per_line():
    assert invoice_total([{"price": "0.05", "quantity": 3, "discount_percent": 10}]) == Decimal("0.14")


def test_multiple_lines():
    lines = [
        {"price": "0.05", "quantity": 3, "discount_percent": 10},
        {"price": "1.00", "quantity": 2, "discount_percent": 25},
    ]
    assert invoice_total(lines) == Decimal("1.64")


def test_empty_invoice():
    assert invoice_total([]) == Decimal("0")
