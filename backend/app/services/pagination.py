from collections.abc import Sequence

FIRST_PAGE = 1
MIN_PAGE_SIZE = 1


def paginate[T](items: Sequence[T], page: int, page_size: int) -> tuple[list[T], int]:
    if page < FIRST_PAGE or page_size < MIN_PAGE_SIZE:
        raise ValueError("Page and page_size must be positive.")
    offset = (page - FIRST_PAGE) * page_size
    return list(items[offset : offset + page_size]), len(items)
