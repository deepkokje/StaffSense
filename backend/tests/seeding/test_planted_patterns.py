from collections import defaultdict

from app.seeding.band_builder import SalaryBandData
from app.seeding.employee_generator import EmployeeSeed
from app.seeding.reference_data import GENDER_GAP_TITLES, SEED_REFERENCE_DATE
from tests.seeding.conftest import SeedDataset

PERMILLE_SCALE = 1_000
STALE_RAISE_THRESHOLD_DAYS = 2 * 365
FEMALE_GAP_MIN_PERMILLE = 50
FEMALE_GAP_MAX_PERMILLE = 90
BELOW_BAND_MIN_SHARE_PERMILLE = 20
BELOW_BAND_MAX_SHARE_PERMILLE = 40
ABOVE_BAND_MIN_SHARE_PERMILLE = 10
ABOVE_BAND_MAX_SHARE_PERMILLE = 30
STALE_RAISE_MIN_SHARE_PERMILLE = 60
STALE_RAISE_MAX_SHARE_PERMILLE = 100
COMPRESSION_MIN_FACTOR_PERMILLE = 1_100
COMPRESSION_MAX_FACTOR_PERMILLE = 1_140


def _band_by_key(dataset: SeedDataset) -> dict[tuple[str, int, str], SalaryBandData]:
    return {
        (band["title"], band["level"], band["country"]): band for band in dataset.bands
    }


def _peer_groups(
    employees: list[EmployeeSeed],
) -> dict[tuple[str, int, str], list[EmployeeSeed]]:
    groups: dict[tuple[str, int, str], list[EmployeeSeed]] = defaultdict(list)
    for employee in employees:
        groups[(employee.title, employee.level, employee.country)].append(employee)
    return groups


def _integer_mean(values: list[int]) -> int:
    return sum(values) // len(values)


def test_planted_gender_gap_and_raw_gap_exceed_adjusted_gap(
    seeded_dataset: SeedDataset,
) -> None:
    employees = seeded_dataset.employees
    planted = [employee for employee in employees if employee.title in GENDER_GAP_TITLES]
    bands = _band_by_key(seeded_dataset)
    normalized_female_permille = [
        employee.salary_minor
        * PERMILLE_SCALE
        // bands[(employee.title, employee.level, employee.country)]["mid_minor"]
        for employee in planted
        if employee.gender == "FEMALE"
    ]
    normalized_male_permille = [
        employee.salary_minor
        * PERMILLE_SCALE
        // bands[(employee.title, employee.level, employee.country)]["mid_minor"]
        for employee in planted
        if employee.gender == "MALE"
    ]
    adjusted_gap_permille = PERMILLE_SCALE - (
        _integer_mean(normalized_female_permille) * PERMILLE_SCALE
        // _integer_mean(normalized_male_permille)
    )
    female_usd_average = _integer_mean([
        employee.salary_usd_minor for employee in employees if employee.gender == "FEMALE"
    ])
    male_usd_average = _integer_mean([
        employee.salary_usd_minor for employee in employees if employee.gender == "MALE"
    ])
    raw_gap_permille = PERMILLE_SCALE - (
        female_usd_average * PERMILLE_SCALE // male_usd_average
    )

    assert FEMALE_GAP_MIN_PERMILLE <= adjusted_gap_permille <= FEMALE_GAP_MAX_PERMILLE
    assert raw_gap_permille > adjusted_gap_permille


def test_band_violation_shares_are_within_expected_ranges(seeded_dataset: SeedDataset) -> None:
    employees = seeded_dataset.employees
    bands = _band_by_key(seeded_dataset)
    below_count = sum(
        employee.salary_minor
        < bands[(employee.title, employee.level, employee.country)]["min_minor"]
        for employee in employees
    )
    above_count = sum(
        employee.salary_minor
        > bands[(employee.title, employee.level, employee.country)]["max_minor"]
        for employee in employees
    )

    assert BELOW_BAND_MIN_SHARE_PERMILLE <= below_count * PERMILLE_SCALE // len(employees)
    assert below_count * PERMILLE_SCALE // len(employees) <= BELOW_BAND_MAX_SHARE_PERMILLE
    assert ABOVE_BAND_MIN_SHARE_PERMILLE <= above_count * PERMILLE_SCALE // len(employees)
    assert above_count * PERMILLE_SCALE // len(employees) <= ABOVE_BAND_MAX_SHARE_PERMILLE


def test_inversions_compression_small_groups_and_stale_raises_are_planted(
    seeded_dataset: SeedDataset,
) -> None:
    employees = seeded_dataset.employees
    employee_by_id = {employee.id: employee for employee in employees}
    inverted_count = sum(
        employee.salary_usd_minor > employee_by_id[employee.manager_id].salary_usd_minor
        for employee in employees
        if employee.manager_id is not None
    )
    groups = _peer_groups(employees)
    compressed_group_count = 0
    for group in groups.values():
        if len(group) < 8:
            continue
        most_recent = sorted(group, key=lambda employee: employee.hire_date, reverse=True)[:2]
        remaining_salaries = [
            employee.salary_minor for employee in group if employee not in most_recent
        ]
        remaining_median = sorted(remaining_salaries)[len(remaining_salaries) // 2]
        if all(
            COMPRESSION_MIN_FACTOR_PERMILLE
            <= employee.salary_minor * PERMILLE_SCALE // remaining_median
            <= COMPRESSION_MAX_FACTOR_PERMILLE
            for employee in most_recent
        ):
            compressed_group_count += 1
    small_group_count = sum(len(group) < 5 for group in groups.values())
    stale_raise_count = sum(
        employee.last_raise_date is not None
        and (SEED_REFERENCE_DATE - employee.last_raise_date).days > STALE_RAISE_THRESHOLD_DAYS
        for employee in employees
    )

    assert inverted_count >= 10
    assert compressed_group_count >= 2
    assert small_group_count >= 5
    stale_share_permille = stale_raise_count * PERMILLE_SCALE // len(employees)
    assert STALE_RAISE_MIN_SHARE_PERMILLE <= stale_share_permille
    assert stale_share_permille <= STALE_RAISE_MAX_SHARE_PERMILLE
