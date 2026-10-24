import pytest

from app.services.band_compliance import (
    BandStatus,
    BandSummary,
    classify,
    compa_ratio_permille,
    evaluate_bands,
)
from app.services.peer_groups import PeerGroupKey
from tests.insight_factories import band_row, salary_row

KEY = PeerGroupKey("Engineer", 3, "US")


@pytest.mark.parametrize("salary, expected", [(900, 900), (1_000, 1_000), (1_234, 1_234)])
def test_compa_ratio_is_integer_permille(salary: int, expected: int) -> None:
    # salary * 1000 / midpoint 1000 = salary.
    assert compa_ratio_permille(salary, 1_000) == expected


def test_compa_ratio_uses_half_even_rounding() -> None:
    # 1*1000/16 = 62.5 -> 62; 3*1000/16 = 187.5 -> 188.
    assert compa_ratio_permille(1, 16) == 62
    assert compa_ratio_permille(3, 16) == 188


def test_compa_ratio_rejects_zero_midpoint() -> None:
    with pytest.raises(ValueError):
        compa_ratio_permille(1_000, 0)


@pytest.mark.parametrize(
    "salary, expected",
    [
        (700, BandStatus.BELOW_MIN),
        (1_450, BandStatus.ABOVE_MAX),
        (800, BandStatus.WITHIN_BAND),
        (1_200, BandStatus.WITHIN_BAND),
    ],
)
def test_classification_includes_both_band_boundaries(salary: int, expected: BandStatus) -> None:
    assert classify(salary, 800, 1_200) == expected


def test_report_counts_all_categories_and_flags_positive_gaps_in_stable_order() -> None:
    rows = [
        salary_row(1, 700),
        salary_row(2, 1_450),
        salary_row(3, 1_450),
        salary_row(4, 800),
        salary_row(5, 1_200),
        salary_row(6, title="No Band"),
    ]
    report = evaluate_bands(rows, {KEY: band_row()})
    assert report.summary == BandSummary(below_min=1, within_band=2, above_max=2, no_band=1)
    # 1450 - 1200 = 250; 800 - 700 = 100. Equal gaps use employee ID.
    assert [(row.employee_id, row.gap_to_band_minor) for row in report.flagged] == [
        (2, 250),
        (3, 250),
        (1, 100),
    ]
    assert report.flagged[0].compa_ratio_permille == 1_450
    assert report.flagged[0].band_mid_minor == 1_000
    assert report.flagged[0].name == "Employee 2"


def test_missing_band_is_counted_but_not_flagged() -> None:
    report = evaluate_bands([salary_row()], {})
    assert report.summary.no_band == 1
    assert report.flagged == []


def test_band_currency_must_match_employee_currency() -> None:
    with pytest.raises(ValueError, match="currency"):
        evaluate_bands([salary_row(currency="EUR")], {KEY: band_row()})
