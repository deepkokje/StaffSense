import pytest

from app.services.pagination import paginate


@pytest.mark.parametrize(
    "page, expected",
    [(1, [1, 2]), (3, [5]), (4, [])],
)
def test_pagination_returns_requested_slice_and_unpaginated_total(
    page: int,
    expected: list[int],
) -> None:
    assert paginate([1, 2, 3, 4, 5], page, 2) == (expected, 5)


@pytest.mark.parametrize("page,page_size", [(0, 2), (1, 0)])
def test_pagination_rejects_nonpositive_parameters(page: int, page_size: int) -> None:
    with pytest.raises(ValueError):
        paginate([], page, page_size)
