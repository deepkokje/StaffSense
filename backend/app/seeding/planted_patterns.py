import random
from datetime import timedelta

from app.money import FxRate, Money
from app.seeding.band_builder import SalaryBandData
from app.seeding.employee_generator import EmployeeSeed
from app.seeding.reference_data import (
    FX_RATES,
    GENDER_GAP_TITLES,
    SEED_REFERENCE_DATE,
)

GENDER_GAP_FACTOR_PERMILLE = 930
GENDER_GAP_TITLES_COUNT = 3
BELOW_BAND_SHARE_PERMILLE = 30
BELOW_BAND_MIN_FACTOR_PERMILLE = 900
BELOW_BAND_MAX_FACTOR_PERMILLE = 980
ABOVE_BAND_SHARE_PERMILLE = 20
ABOVE_BAND_MIN_FACTOR_PERMILLE = 1_020
ABOVE_BAND_MAX_FACTOR_PERMILLE = 1_150
OUTLIER_SHARE_PERMILLE = 10
OUTLIER_LOW_FACTOR_PERMILLE = 700
OUTLIER_HIGH_FACTOR_PERMILLE = 1_300
OUTLIER_HIGH_PROBABILITY_PERMILLE = 500
COMPRESSION_GROUP_COUNT = 2
COMPRESSION_MIN_GROUP_SIZE = 8
COMPRESSION_RECENT_HIRE_COUNT = 2
COMPRESSION_FACTOR_PERMILLE = 1_120
INVERSION_SHARE_PERMILLE = 10
INVERSION_INCREMENT_MINOR = 1
STALE_RAISE_SHARE_PERMILLE = 80
STALE_RAISE_MIN_MONTHS = 25
STALE_RAISE_MAX_MONTHS = 72
PERMILLE_SCALE = 1_000
MONTH_DAYS_APPROXIMATION = 30


def _salary_bands_by_key(
    bands: list[SalaryBandData],
) -> dict[tuple[str, int, str], SalaryBandData]:
    return {(band["title"], band["level"], band["country"]): band for band in bands}


def _update_salary(employee: EmployeeSeed, salary_minor: int) -> None:
    employee.salary_minor = max(1, salary_minor)
    employee.salary_usd_minor = Money(employee.salary_minor, employee.currency).to_usd(
        FxRate(FX_RATES[employee.currency])
    ).amount_minor


def _sample_count(population: int, share_permille: int) -> int:
    return population * share_permille // PERMILLE_SCALE


def _integer_median(values: list[int]) -> int:
    ordered = sorted(values)
    midpoint = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[midpoint]
    return (ordered[midpoint - 1] + ordered[midpoint]) // 2


def _peer_groups(
    employees: list[EmployeeSeed],
) -> dict[tuple[str, int, str], list[EmployeeSeed]]:
    groups: dict[tuple[str, int, str], list[EmployeeSeed]] = {}
    for employee in employees:
        groups.setdefault(
            (employee.title, employee.level, employee.country),
            [],
        ).append(employee)
    return groups


def apply_gender_gap(employees: list[EmployeeSeed], rng: random.Random) -> None:
    """Feeds the adjusted gender pay-gap insight in the selected titles."""
    selected_titles = set(rng.sample(GENDER_GAP_TITLES, k=GENDER_GAP_TITLES_COUNT))
    for employee in employees:
        if employee.title in selected_titles and employee.gender == "FEMALE":
            _update_salary(
                employee,
                employee.salary_minor * GENDER_GAP_FACTOR_PERMILLE // PERMILLE_SCALE,
            )


def apply_below_band(
    employees: list[EmployeeSeed],
    bands: list[SalaryBandData],
    rng: random.Random,
) -> None:
    """Feeds the below-band compensation insight."""
    band_by_key = _salary_bands_by_key(bands)
    count = _sample_count(len(employees), BELOW_BAND_SHARE_PERMILLE)
    for employee in rng.sample(employees, k=count):
        band = band_by_key[(employee.title, employee.level, employee.country)]
        factor = rng.randint(BELOW_BAND_MIN_FACTOR_PERMILLE, BELOW_BAND_MAX_FACTOR_PERMILLE)
        _update_salary(employee, band["min_minor"] * factor // PERMILLE_SCALE)


def apply_above_band(
    employees: list[EmployeeSeed],
    bands: list[SalaryBandData],
    rng: random.Random,
) -> None:
    """Feeds the above-band compensation insight."""
    band_by_key = _salary_bands_by_key(bands)
    count = _sample_count(len(employees), ABOVE_BAND_SHARE_PERMILLE)
    for employee in rng.sample(employees, k=count):
        band = band_by_key[(employee.title, employee.level, employee.country)]
        factor = rng.randint(ABOVE_BAND_MIN_FACTOR_PERMILLE, ABOVE_BAND_MAX_FACTOR_PERMILLE)
        _update_salary(employee, band["max_minor"] * factor // PERMILLE_SCALE)


def apply_outliers(employees: list[EmployeeSeed], rng: random.Random) -> None:
    """Feeds the peer-group salary outlier insight."""
    groups = _peer_groups(employees)
    count = _sample_count(len(employees), OUTLIER_SHARE_PERMILLE)
    for employee in rng.sample(employees, k=count):
        group = groups[(employee.title, employee.level, employee.country)]
        peer_median = _integer_median([item.salary_minor for item in group])
        is_high_outlier = rng.randrange(PERMILLE_SCALE) < OUTLIER_HIGH_PROBABILITY_PERMILLE
        factor = OUTLIER_HIGH_FACTOR_PERMILLE if is_high_outlier else OUTLIER_LOW_FACTOR_PERMILLE
        _update_salary(employee, peer_median * factor // PERMILLE_SCALE)


def apply_compression(employees: list[EmployeeSeed], rng: random.Random) -> None:
    """Feeds the salary-compression insight within established peer groups."""
    eligible_groups = [
        group
        for group in _peer_groups(employees).values()
        if len(group) >= COMPRESSION_MIN_GROUP_SIZE
    ]
    if len(eligible_groups) < COMPRESSION_GROUP_COUNT:
        return
    for group in rng.sample(eligible_groups, k=COMPRESSION_GROUP_COUNT):
        peer_median = _integer_median([item.salary_minor for item in group])
        most_recent = sorted(group, key=lambda employee: employee.hire_date, reverse=True)[
            :COMPRESSION_RECENT_HIRE_COUNT
        ]
        for employee in most_recent:
            _update_salary(
                employee,
                peer_median * COMPRESSION_FACTOR_PERMILLE // PERMILLE_SCALE,
            )


def apply_inversion(employees: list[EmployeeSeed], rng: random.Random) -> None:
    """Feeds the manager-pay inversion insight."""
    employee_by_id = {employee.id: employee for employee in employees}
    eligible = [employee for employee in employees if employee.manager_id is not None]
    count = _sample_count(len(eligible), INVERSION_SHARE_PERMILLE)
    selected = sorted(
        rng.sample(eligible, k=count),
        key=lambda employee: employee.level,
        reverse=True,
    )
    for employee in selected:
        manager = employee_by_id[employee.manager_id]
        if manager.currency == employee.currency:
            _update_salary(employee, manager.salary_minor + INVERSION_INCREMENT_MINOR)


def apply_stale_raises(employees: list[EmployeeSeed], rng: random.Random) -> None:
    """Feeds the stale-raise insight by assigning old raise dates to eligible employees."""
    stale_threshold_days = STALE_RAISE_MIN_MONTHS * MONTH_DAYS_APPROXIMATION
    eligible = [
        employee
        for employee in employees
        if (SEED_REFERENCE_DATE - employee.hire_date).days > stale_threshold_days
    ]
    count = _sample_count(len(employees), STALE_RAISE_SHARE_PERMILLE)
    count = min(count, len(eligible))
    for employee in rng.sample(eligible, k=count):
        earliest_months = min(
            STALE_RAISE_MAX_MONTHS,
            (SEED_REFERENCE_DATE - employee.hire_date).days // MONTH_DAYS_APPROXIMATION,
        )
        months_ago = rng.randint(STALE_RAISE_MIN_MONTHS, earliest_months)
        employee.last_raise_date = SEED_REFERENCE_DATE - timedelta(
            days=months_ago * MONTH_DAYS_APPROXIMATION
        )


def apply_planted_patterns(
    employees: list[EmployeeSeed],
    bands: list[SalaryBandData],
    rng: random.Random,
) -> None:
    apply_gender_gap(employees, rng)
    apply_below_band(employees, bands, rng)
    apply_above_band(employees, bands, rng)
    apply_outliers(employees, rng)
    apply_compression(employees, rng)
    apply_inversion(employees, rng)
    apply_stale_raises(employees, rng)
