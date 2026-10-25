from random import Random

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.db import get_session
from app.main import app
from app.repositories.insight_repository import BandRow, SalaryRow
from app.seeding import FX_RATES, apply_planted_patterns, build_salary_bands, generate_employees
from app.seeding.loader import load_seed_data
from app.services.band_compliance import evaluate_bands
from app.services.benchmarks import compute_benchmarks
from app.services.outliers import find_outliers
from app.services.peer_groups import PeerGroupKey
from app.services.what_if import cost_to_reach_band_min
from tests.seeding.conftest import generate_dataset

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
    cost = cost_to_reach_band_min(rows, bands_by_key, FX_RATES)
    assert cost.total_cost_usd_minor > 0
    # Cross multiplication checks 1% <= affected/3000 <= 6% without floats.
    assert EMPLOYEE_COUNT <= cost.employees_affected * 100 <= EMPLOYEE_COUNT * 6


def test_seeded_employee_raise_is_returned_by_history_endpoint(session: Session) -> None:
    dataset = generate_dataset(SEED, 100)
    load_seed_data(session, FX_RATES, dataset.bands, dataset.employees, dataset.history)
    session.commit()
    seeded_change = next(
        row for row in dataset.history if row.new_salary_minor > row.old_salary_minor
    )
    app.dependency_overrides[get_session] = lambda: session
    try:
        with TestClient(app) as client:
            response = client.get(f"/employees/{seeded_change.employee_id}/salary-history")
        assert response.status_code == 200
        items = response.json()["items"]
        assert len(items) == 1
        assert items[0]["change_bp"] > 0
        assert items[0]["old_salary_minor"] == seeded_change.old_salary_minor
        assert items[0]["new_salary_minor"] == seeded_change.new_salary_minor
    finally:
        app.dependency_overrides.pop(get_session, None)
