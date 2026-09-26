def page_bounds(page: int, page_size: int) -> tuple[int, int]:
    if page < 1 or page_size < 1:
        raise ValueError("page and page_size must be positive")
    start = (page - 1) * page_size
    # BUG: inclusive end incorrectly used as Python slice stop.
    return start, start + page_size - 1
