from datetime import datetime

import pytest

from app.services.salary_history import build_salary_change

CHANGED_AT = datetime(2026, 10, 25, 9, 30)


@pytest.mark.parametrize(
    ("old_minor", "new_minor", "change_minor", "change_bp"),
    [
        (1000, 1100, 100, 1000),  # 100 * 10000 / 1000 = 1000 bp.
        (1000, 900, -100, -1000),  # -100 * 10000 / 1000 = -1000 bp.
        (3, 4, 1, 3333),  # 10000 / 3 = 3333 and a remainder; rounds down.
        (32, 33, 1, 312),  # 10000 / 32 = 312 plus one half; even is 312.
        (32, 31, -1, -312),  # Negative half-even ties are symmetric.
        (2, 3, 1, 5000),  # 10000 / 2 = 5000 bp.
        (0, 500, 500, None),  # A percentage relative to zero is undefined.
    ],
)
def test_builds_signed_change_with_half_even_basis_points(
    old_minor: int, new_minor: int, change_minor: int, change_bp: int | None,
) -> None:
    change = build_salary_change(old_minor, new_minor, "USD", CHANGED_AT)
    assert change is not None
    assert change.old_salary_minor == old_minor
    assert change.new_salary_minor == new_minor
    assert change.change_minor == change_minor
    assert change.change_bp == change_bp
    assert change.currency == "USD"
    assert change.changed_at == CHANGED_AT


def test_unchanged_salary_returns_none() -> None:
    assert build_salary_change(1000, 1000, "USD", CHANGED_AT) is None
