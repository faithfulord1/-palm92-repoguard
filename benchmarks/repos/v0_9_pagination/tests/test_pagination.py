import pytest
from service import get_page


def test_no_overlap():
    items = list(range(7))
    assert get_page(items, 1, 3) == [0, 1, 2]
    assert get_page(items, 2, 3) == [3, 4, 5]
    assert get_page(items, 3, 3) == [6]


def test_empty():
    assert get_page([], 1, 3) == []


@pytest.mark.parametrize("page,size", [(0, 2), (1, 0), (-1, 3)])
def test_invalid(page, size):
    with pytest.raises(ValueError):
        get_page([1, 2], page, size)
