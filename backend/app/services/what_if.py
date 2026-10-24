from collections.abc import Iterable, Mapping
from dataclasses import dataclass

from app.money import FxRate, Money
from app.services.band_compliance import BandStatus, BandValues, classify
from app.services.benchmarks import BenchmarkSalaryRow
from app.services.peer_groups import PeerGroupKey
from app.services.statistics import round_half_even_div

MIN_RAISE_BP = 1
MAX_RAISE_BP = 5_000
BASIS_POINTS_SCALE = 10_000


@dataclass(frozen=True)
class CountryCost:
    country: str
    currency: str
    employees_affected: int
    cost_local_minor: int
    cost_usd_minor: int


@dataclass(frozen=True)
class BandMinCostReport:
    total_cost_usd_minor: int
    employees_affected: int
    by_country: list[CountryCost]


@dataclass(frozen=True)
class RaiseCostReport:
    employees_affected: int
    total_cost_usd_minor: int
    current_payroll_usd_minor: int
    new_payroll_usd_minor: int
    by_country: list[CountryCost]


@dataclass
class _CountryTotals:
    currency: str
    employees_affected: int = 0
    cost_local_minor: int = 0
    payroll_local_minor: int = 0


def _add_employee(
    totals: dict[str, _CountryTotals],
    row: BenchmarkSalaryRow,
    cost: int,
) -> None:
    country = totals.setdefault(row.country, _CountryTotals(row.currency))
    if country.currency != row.currency:
        raise ValueError(f"Country {row.country} must have exactly one currency.")
    country.employees_affected += 1
    country.cost_local_minor += cost
    country.payroll_local_minor += row.salary_minor


def _to_usd(amount: int, currency: str, fx_rates: Mapping[str, int]) -> int:
    if currency not in fx_rates:
        raise ValueError(f"Missing FX rate for {currency}.")
    return Money(amount, currency).to_usd(FxRate(fx_rates[currency])).amount_minor


def _country_costs(
    totals: Mapping[str, _CountryTotals],
    fx_rates: Mapping[str, int],
) -> list[CountryCost]:
    # Convert each country's local sum once to avoid employee-level FX rounding drift.
    costs = [
        CountryCost(
            country=country,
            currency=values.currency,
            employees_affected=values.employees_affected,
            cost_local_minor=values.cost_local_minor,
            cost_usd_minor=_to_usd(values.cost_local_minor, values.currency, fx_rates),
        )
        for country, values in totals.items()
    ]
    return sorted(costs, key=lambda cost: (-cost.cost_usd_minor, cost.country))


def cost_to_reach_band_min(
    rows: Iterable[BenchmarkSalaryRow],
    bands_by_key: Mapping[PeerGroupKey, BandValues],
    fx_rates: Mapping[str, int],
) -> BandMinCostReport:
    totals: dict[str, _CountryTotals] = {}
    for row in rows:
        band = bands_by_key.get(PeerGroupKey(row.title, row.level, row.country))
        if band is None:
            continue
        if band.currency != row.currency:
            raise ValueError(f"Band currency does not match employee currency in {row.country}.")
        if classify(row.salary_minor, band.min_minor, band.max_minor) == BandStatus.BELOW_MIN:
            _add_employee(totals, row, band.min_minor - row.salary_minor)
    by_country = _country_costs(totals, fx_rates)
    return BandMinCostReport(
        total_cost_usd_minor=sum(cost.cost_usd_minor for cost in by_country),
        employees_affected=sum(cost.employees_affected for cost in by_country),
        by_country=by_country,
    )


def cost_of_raise(
    rows: Iterable[BenchmarkSalaryRow],
    raise_bp: int,
    fx_rates: Mapping[str, int],
) -> RaiseCostReport:
    if not MIN_RAISE_BP <= raise_bp <= MAX_RAISE_BP:
        raise ValueError(f"raise_bp must be between {MIN_RAISE_BP} and {MAX_RAISE_BP}.")
    totals: dict[str, _CountryTotals] = {}
    for row in rows:
        cost = round_half_even_div(row.salary_minor * raise_bp, BASIS_POINTS_SCALE)
        _add_employee(totals, row, cost)
    by_country = _country_costs(totals, fx_rates)
    total_cost = sum(cost.cost_usd_minor for cost in by_country)
    current_payroll = sum(
        _to_usd(values.payroll_local_minor, values.currency, fx_rates) for values in totals.values()
    )
    return RaiseCostReport(
        employees_affected=sum(cost.employees_affected for cost in by_country),
        total_cost_usd_minor=total_cost,
        current_payroll_usd_minor=current_payroll,
        new_payroll_usd_minor=current_payroll + total_cost,
        by_country=by_country,
    )
