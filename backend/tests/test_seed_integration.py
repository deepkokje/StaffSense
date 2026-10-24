from random import Random

from app.repositories.insight_repository import BandRow, SalaryRow
from app.seeding import apply_planted_patterns, build_salary_bands, generate_employees
from app.services.band_compliance import evaluate_bands
from app.services.benchmarks import compute_benchmarks
from app.services.outliers import find_outliers
from app.services.peer_groups import PeerGroupKey

SEED = 42
EMPLOYEE_COUNT = 3_000


def test_seeded_data_has_sufficient_and_insufficient_peer_groups() -> None:
    rng = Random(SEED)
    bands = build_salary_bands()
    employees = generate_employees(EMPLOYEE_COUNT, rng, SEED, bands)
    apply_planted_patterns(employees, bands, rng)
    active_rows = [employee for employee in employees if employee.status in ("ACTIVE", "ON_LEAVE")]
    benchmarks = compute_benchmarks(active_rows)
    assert any(item.insufficient_data for item in benchmarks)
    assert any(not item.insufficient_data for item in benchmarks)
    rows = [
        SalaryRow(
            employee.id,
            employee.title,
            employee.level,
            employee.country,
            employee.currency,
            employee.salary_minor,
            employee.name,
            employee.department,
        )
        for employee in active_rows
    ]
    bands_by_key = {
        PeerGroupKey(band["title"], band["level"], band["country"]): BandRow(
            band["currency"],
            band["min_minor"],
            band["mid_minor"],
            band["max_minor"],
        )
        for band in bands
    }
    report = evaluate_bands(rows, bands_by_key)
    assert report.summary.below_min > 0
    assert report.summary.above_max > 0
    assert len(find_outliers(rows)) > 0
