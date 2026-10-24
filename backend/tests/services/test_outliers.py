import pytest

from app.services.outliers import OutlierDirection, deviation_permille, find_outliers
from tests.insight_factories import salary_row


def test_group_of_four_is_not_evaluated() -> None:
    assert (
        find_outliers(
            [
                salary_row(index, value)
                for index, value in enumerate([10, 1_000, 1_000, 1_000], start=1)
            ]
        )
        == []
    )


def test_group_of_five_flags_strictly_more_than_twenty_percent() -> None:
    rows = [
        salary_row(index, value)
        for index, value in enumerate([799, 1_000, 1_000, 1_200, 1_201], start=1)
    ]
    result = find_outliers(rows)
    # Median = 1000. (799-1000)*1000/1000=-201; 1200 => 200; 1201 => 201.
    assert [(row.employee_id, row.deviation_permille, row.direction) for row in result] == [
        (1, -201, OutlierDirection.BELOW),
        (5, 201, OutlierDirection.ABOVE),
    ]
    assert all(row.group_median_minor == 1_000 and row.group_headcount == 5 for row in result)


def test_even_group_uses_half_even_median_and_absolute_deviation_order() -> None:
    rows = [
        salary_row(index, value)
        for index, value in enumerate([100, 800, 1_000, 1_001, 1_200, 1_500], start=1)
    ]
    result = find_outliers(rows)
    # (1000+1001)/2=1000.5 -> 1000; deviations -900 and +500.
    assert [(row.employee_id, row.deviation_permille) for row in result] == [(1, -900), (6, 500)]
    assert all(row.group_median_minor == 1_000 for row in result)


def test_deviation_rounds_signed_half_ties_to_even() -> None:
    # (17-16)*1000/16 = 62.5 -> 62; (13-16)*1000/16 = -187.5 -> -188.
    assert deviation_permille(17, 16) == 62
    assert deviation_permille(13, 16) == -188


def test_zero_median_is_rejected() -> None:
    with pytest.raises(ValueError):
        deviation_permille(1, 0)


def test_exact_twenty_percent_deviations_in_both_directions_are_not_flagged() -> None:
    rows = [
        salary_row(index, value)
        for index, value in enumerate([800, 1_000, 1_000, 1_000, 1_200], start=1)
    ]
    assert find_outliers(rows) == []


def test_equal_absolute_deviations_are_ordered_by_id_not_input_order() -> None:
    rows = [
        salary_row(index, value)
        for index, value in enumerate([799, 1_000, 1_000, 1_000, 1_201], start=1)
    ]
    assert [row.employee_id for row in find_outliers(list(reversed(rows)))] == [1, 5]


def test_outliers_do_not_mix_currencies_or_separate_peer_groups() -> None:
    rows = [salary_row(index, 1_000) for index in range(1, 6)]
    with pytest.raises(ValueError, match="currency"):
        find_outliers([*rows, salary_row(6, currency="EUR")])
    assert find_outliers([*rows, salary_row(6, 1, country="GB", currency="GBP")]) == []
