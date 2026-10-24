import pytest

from app.money import FX_RATE_SCALE
from app.repositories.insight_repository import BandRow
from app.services.peer_groups import PeerGroupKey
from app.services.what_if import cost_of_raise, cost_to_reach_band_min
from tests.insight_factories import band_row, salary_row

USD_RATES = {"USD": FX_RATE_SCALE}
US_KEY = PeerGroupKey("Engineer", 3, "US")


def test_employees_in_band_or_exactly_at_minimum_have_no_cost() -> None:
    report = cost_to_reach_band_min(
        [salary_row(1, 1_000), salary_row(2, 800)],
        {US_KEY: band_row()},
        USD_RATES,
    )
    assert report.total_cost_usd_minor == 0
    assert report.employees_affected == 0
    assert report.by_country == []


def test_usd_employee_one_hundred_below_minimum_costs_one_hundred() -> None:
    report = cost_to_reach_band_min([salary_row(1, 700)], {US_KEY: band_row()}, USD_RATES)
    assert report.total_cost_usd_minor == 100
    assert report.employees_affected == 1
    assert report.by_country[0].cost_local_minor == 100


def test_employee_without_band_is_skipped_without_requiring_fx() -> None:
    report = cost_to_reach_band_min([salary_row()], {}, {})
    assert report.employees_affected == report.total_cost_usd_minor == 0


@pytest.mark.parametrize(
    "country,currency,minimum,rate,expected",
    [("IN", "INR", 10_000, 12_000, 120), ("JP", "JPY", 1_000, 6_500, 650)],
)
def test_local_band_gap_converts_using_currency_exponent(
    country: str,
    currency: str,
    minimum: int,
    rate: int,
    expected: int,
) -> None:
    # INR 10000 minor = INR 100; 100 * .012 USD = USD 1.20 = 120 minor.
    # JPY 1000 minor = JPY 1000; 1000 * .0065 USD = USD 6.50 = 650 minor.
    report = cost_to_reach_band_min(
        [salary_row(salary_minor=0, country=country, currency=currency)],
        {PeerGroupKey("Engineer", 3, country): BandRow(currency, minimum, minimum, minimum)},
        {currency: rate},
    )
    assert report.total_cost_usd_minor == expected
    assert report.by_country[0].cost_local_minor == minimum


def test_band_cost_converts_country_sum_once_to_avoid_rounding_drift() -> None:
    rows = [salary_row(index, 0, country="JP", currency="JPY") for index in (1, 2)]
    # Each JPY 1 converts to USD .65 minor -> 1, but JPY 2 -> 1.3 -> 1.
    report = cost_to_reach_band_min(
        rows,
        {PeerGroupKey("Engineer", 3, "JP"): BandRow("JPY", 1, 1, 1)},
        {"JPY": 6_500},
    )
    assert report.by_country[0].cost_local_minor == 2
    assert report.total_cost_usd_minor == 1
    assert report.employees_affected == 2


def test_raise_cost_rounds_each_local_raise_then_adds_to_current_payroll() -> None:
    # 1000 * 500/10000 = 50; 2001 * 500/10000 = 100.05 -> 100.
    report = cost_of_raise([salary_row(1, 1_000), salary_row(2, 2_001)], 500, USD_RATES)
    assert report.employees_affected == 2
    assert report.total_cost_usd_minor == 150
    assert report.current_payroll_usd_minor == 3_001
    assert report.new_payroll_usd_minor == 3_151
    assert (
        report.new_payroll_usd_minor
        == report.current_payroll_usd_minor + report.total_cost_usd_minor
    )


def test_raise_cost_and_current_payroll_convert_country_totals_once() -> None:
    # JPY salaries 2,2 at 50% raise give raises 1,1. Cost 2*.65 = 1.3 -> 1.
    # Current payroll 4*.65 = 2.6 -> 3; new payroll is 3+1=4, not a fresh FX conversion.
    report = cost_of_raise(
        [salary_row(index, 2, country="JP", currency="JPY") for index in (1, 2)],
        5_000,
        {"JPY": 6_500},
    )
    assert report.total_cost_usd_minor == 1
    assert report.current_payroll_usd_minor == 3
    assert report.new_payroll_usd_minor == 4


def test_raise_local_half_ties_round_to_even() -> None:
    # At 50%, local raises 1*1/2=.5 -> 0 and 3*1/2=1.5 -> 2.
    report = cost_of_raise([salary_row(1, 1), salary_row(2, 3)], 5_000, USD_RATES)
    assert report.total_cost_usd_minor == 2


@pytest.mark.parametrize("raise_bp", [0, 5_001])
def test_raise_basis_points_outside_range_raise_value_error(raise_bp: int) -> None:
    with pytest.raises(ValueError, match="raise_bp"):
        cost_of_raise([], raise_bp, {})


def test_missing_fx_rate_raises_value_error_for_both_scenarios() -> None:
    with pytest.raises(ValueError, match="USD"):
        cost_of_raise([salary_row()], 500, {})
    with pytest.raises(ValueError, match="USD"):
        cost_to_reach_band_min([salary_row(salary_minor=700)], {US_KEY: band_row()}, {})


def test_country_costs_are_sorted_by_descending_usd_cost_then_country() -> None:
    rows = [
        salary_row(1, 100, country="US"),
        salary_row(2, 200, country="GB"),
        salary_row(3, 200, country="CA"),
    ]
    rates = {"USD": FX_RATE_SCALE}
    report = cost_of_raise(rows, 5_000, rates)
    assert [row.country for row in report.by_country] == ["CA", "GB", "US"]
    bands = {PeerGroupKey("Engineer", 3, country): band_row() for country in ("US", "GB", "CA")}
    band_report = cost_to_reach_band_min(rows, bands, rates)
    assert [row.country for row in band_report.by_country] == ["US", "CA", "GB"]
    assert band_report.total_cost_usd_minor == sum(
        row.cost_usd_minor for row in band_report.by_country
    )


def test_empty_raise_selection_returns_all_zero_totals() -> None:
    report = cost_of_raise([], 500, {})
    assert report.employees_affected == report.total_cost_usd_minor == 0
    assert report.current_payroll_usd_minor == report.new_payroll_usd_minor == 0
    assert report.by_country == []


def test_currency_mismatches_are_rejected_instead_of_combined() -> None:
    with pytest.raises(ValueError, match="currency"):
        cost_to_reach_band_min(
            [salary_row(salary_minor=700, currency="EUR")],
            {US_KEY: band_row()},
            USD_RATES,
        )
    with pytest.raises(ValueError, match="currency"):
        cost_of_raise([salary_row(1), salary_row(2, currency="EUR")], 500, USD_RATES)
