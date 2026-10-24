from random import Random

from app.seeding import apply_planted_patterns, build_salary_bands, generate_employees
from app.services.benchmarks import compute_benchmarks

SEED = 42
EMPLOYEE_COUNT = 2_000


def test_seeded_data_has_sufficient_and_insufficient_peer_groups() -> None:
    rng = Random(SEED)
    bands = build_salary_bands()
    employees = generate_employees(EMPLOYEE_COUNT, rng, SEED, bands)
    apply_planted_patterns(employees, bands, rng)
    active_rows = [employee for employee in employees if employee.status in ("ACTIVE", "ON_LEAVE")]
    benchmarks = compute_benchmarks(active_rows)
    assert any(item.insufficient_data for item in benchmarks)
    assert any(not item.insufficient_data for item in benchmarks)
