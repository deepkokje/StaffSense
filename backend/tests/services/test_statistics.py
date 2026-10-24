import pytest

from app.services.statistics import median, percentile, round_half_even_div


@pytest.mark.parametrize("percent, expected", [(0, 10), (25, 18), (50, 25), (75, 32), (100, 40)])
def test_percentiles_interpolate_with_half_even_rounding(percent: int, expected: int) -> None:
    # Rank = percent * 3 / 100; p25 = 10 + 10*75/100 = 17.5 -> 18.
    # p50 = 20 + 10*50/100 = 25; p75 = 30 + 10*25/100 = 32.5 -> 32.
    assert percentile([10, 20, 30, 40], percent) == expected


@pytest.mark.parametrize("percent", [0, 25, 50, 75, 100])
def test_single_value_is_every_percentile(percent: int) -> None:
    assert percentile([17], percent) == 17


def test_median_handles_odd_even_and_duplicate_values() -> None:
    assert median([10, 20, 30]) == 20
    # (10 + 15) / 2 = 12.5 -> 12, the even integer.
    assert median([10, 15]) == 12
    assert percentile([10, 10, 10, 10], 75) == 10


@pytest.mark.parametrize("values, percent", [([], 50), ([10], -1), ([10], 101)])
def test_invalid_percentile_inputs_raise(values: list[int], percent: int) -> None:
    with pytest.raises(ValueError):
        percentile(values, percent)


@pytest.mark.parametrize("numerator, expected", [(25, 2), (35, 4), (-25, -2), (-35, -4)])
def test_half_even_division_rounds_ties_to_even(numerator: int, expected: int) -> None:
    assert round_half_even_div(numerator, 10) == expected


def test_half_even_division_requires_positive_denominator() -> None:
    with pytest.raises(ValueError):
        round_half_even_div(10, 0)
