from paginator import page_bounds


def get_page(items: list, page: int, page_size: int) -> list:
    start, stop = page_bounds(page, page_size)
    return items[start:stop]
