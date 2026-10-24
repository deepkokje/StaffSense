import random

import pytest
from sqlalchemy import Engine, func, select
from sqlalchemy.orm import Session

from app.models import Employee, FxRate, SalaryBand, SalaryHistory
from app.seeding import FX_RATES, apply_planted_patterns, build_salary_bands, generate_employees
from app.seeding.employee_generator import generate_salary_history
from app.seeding.loader import load_seed_data


def test_loader_inserts_data_and_requires_reset_for_existing_employees(
    engine: Engine,
) -> None:
    bands = build_salary_bands()
    rng = random.Random(42)
    employees = generate_employees(500, rng, 42, bands)
    apply_planted_patterns(employees, bands, rng)
    history = generate_salary_history(employees)

    with Session(engine) as session:
        load_seed_data(session, FX_RATES, bands, employees, history)
        assert session.scalar(select(func.count()).select_from(Employee)) == 500
        assert session.scalar(select(func.count()).select_from(FxRate)) == len(FX_RATES)
        assert session.scalar(select(func.count()).select_from(SalaryBand)) == len(bands)
        assert session.scalar(select(func.count()).select_from(SalaryHistory)) == len(history)

        with pytest.raises(RuntimeError, match="already contains rows"):
            load_seed_data(session, FX_RATES, bands, employees, history)

        load_seed_data(session, FX_RATES, bands, employees, history, reset=True)
        assert session.scalar(select(func.count()).select_from(Employee)) == 500
