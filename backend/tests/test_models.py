from datetime import datetime

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Employee, SalaryBand, SalaryHistory
from tests.conftest import make_employee


def test_employee_can_be_inserted_and_read_back(session: Session) -> None:
    employee = make_employee()
    session.add(employee)
    session.commit()

    loaded = session.get(Employee, employee.id)

    assert loaded is not None
    assert loaded.email == "ada@example.com"
    assert loaded.salary_minor == 12_000_000


def test_employee_email_must_be_unique(session: Session) -> None:
    session.add_all([make_employee(), make_employee(name="Grace Hopper")])

    with pytest.raises(IntegrityError):
        session.commit()


def test_employee_salary_cannot_be_negative(session: Session) -> None:
    session.add(make_employee(salary_minor=-1))

    with pytest.raises(IntegrityError):
        session.commit()


@pytest.mark.parametrize("level", [0, 7])
def test_employee_level_must_be_between_one_and_six(session: Session, level: int) -> None:
    session.add(make_employee(level=level))

    with pytest.raises(IntegrityError):
        session.commit()


@pytest.mark.parametrize(
    ("minimum", "midpoint", "maximum"),
    [(300, 200, 400), (100, 400, 300)],
)
def test_salary_band_requires_ordered_amounts(
    session: Session,
    minimum: int,
    midpoint: int,
    maximum: int,
) -> None:
    session.add(
        SalaryBand(
            title="Engineer",
            level=3,
            country="US",
            currency="USD",
            min_minor=minimum,
            mid_minor=midpoint,
            max_minor=maximum,
        )
    )

    with pytest.raises(IntegrityError):
        session.commit()


def test_salary_band_key_must_be_unique(session: Session) -> None:
    band_values = {
        "title": "Engineer",
        "level": 3,
        "country": "US",
        "currency": "USD",
        "min_minor": 10_000,
        "mid_minor": 20_000,
        "max_minor": 30_000,
    }
    session.add_all([SalaryBand(**band_values), SalaryBand(**band_values)])

    with pytest.raises(IntegrityError):
        session.commit()


def test_salary_history_requires_existing_employee(session: Session) -> None:
    session.add(
        SalaryHistory(
            employee_id=999,
            old_salary_minor=10_000,
            new_salary_minor=12_000,
            currency="USD",
            changed_at=datetime(2024, 1, 1),
        )
    )

    with pytest.raises(IntegrityError):
        session.commit()


def test_employee_manager_can_reference_another_employee(session: Session) -> None:
    manager = make_employee()
    session.add(manager)
    session.flush()
    report = make_employee(
        name="Grace Hopper",
        email="grace@example.com",
        manager_id=manager.id,
    )
    session.add(report)
    session.commit()

    assert report.manager_id == manager.id
    loaded_report = session.get(Employee, report.id)
    assert loaded_report is not None
    assert loaded_report.manager_id == manager.id
