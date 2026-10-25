from datetime import date, datetime

import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Employee, FxRate, SalaryHistory
from app.repositories.employee_repository import EmployeeRepository
from app.services.employee_service import (
    create_employee,
    delete_employee,
    get_employee,
    update_employee,
)
from app.services.errors import (
    DuplicateEmail,
    EmployeeNotFound,
    HasDirectReports,
    InvalidManager,
    MissingFxRate,
    UnsupportedChange,
)
from tests.conftest import make_employee
from tests.employee_write_factories import employee_input


def fixed_clock() -> datetime:
    return datetime(2026, 10, 25, 9, 30)


@pytest.fixture
def repository(session: Session) -> EmployeeRepository:
    session.add_all([
        FxRate(currency="USD", usd_rate_e6=1_000_000),
        FxRate(currency="INR", usd_rate_e6=12_000),
    ])
    session.commit()
    return EmployeeRepository(session)


def test_create_converts_inr_salary(repository: EmployeeRepository) -> None:
    employee = create_employee(repository, employee_input(currency="INR", country="IN"))
    # 10000 paise = INR 100; 100 * USD 0.012 = USD 1.20 = 120 cents.
    assert employee.salary_usd_minor == 120
    assert employee.last_raise_date is None


def test_create_rejects_case_insensitive_duplicate(
    repository: EmployeeRepository, session: Session,
) -> None:
    session.add(make_employee(email="NEW@staff.example"))
    session.commit()
    with pytest.raises(DuplicateEmail):
        create_employee(repository, employee_input())


def test_create_rejects_missing_fx(repository: EmployeeRepository) -> None:
    with pytest.raises(MissingFxRate):
        create_employee(repository, employee_input(currency="EUR"))


def test_create_rejects_unknown_manager(repository: EmployeeRepository) -> None:
    with pytest.raises(InvalidManager):
        create_employee(repository, employee_input(manager_id=999))


def test_update_changes_fields_recomputes_usd_and_sets_raise_date(
    repository: EmployeeRepository, session: Session,
) -> None:
    employee = create_employee(repository, employee_input())
    employee.last_raise_date = date(2021, 2, 3)
    session.commit()
    updated = update_employee(
        repository, employee.id, employee_input(name="Renamed", salary_minor=20000),
        fixed_clock,
    )
    assert updated.name == "Renamed"
    assert updated.salary_usd_minor == 20000
    assert updated.last_raise_date == fixed_clock().date()
    assert session.scalar(select(func.count()).select_from(SalaryHistory)) == 1


def test_update_keeps_own_email_but_rejects_another(
    repository: EmployeeRepository,
) -> None:
    employee = create_employee(repository, employee_input())
    create_employee(repository, employee_input(email="other@staff.example"))
    update_employee(repository, employee.id, employee_input(), fixed_clock)
    with pytest.raises(DuplicateEmail):
        update_employee(
            repository, employee.id, employee_input(email="OTHER@staff.example"), fixed_clock,
        )


def test_update_rejects_currency_change(repository: EmployeeRepository) -> None:
    employee = create_employee(repository, employee_input())
    with pytest.raises(UnsupportedChange, match="changing currency is not supported"):
        update_employee(repository, employee.id, employee_input(currency="INR"), fixed_clock)


def test_update_rejects_cycle_and_self_manager(repository: EmployeeRepository) -> None:
    first = create_employee(repository, employee_input())
    second = create_employee(
        repository, employee_input(email="second@staff.example", manager_id=first.id),
    )
    for manager in (first.id, second.id):
        with pytest.raises(InvalidManager):
            update_employee(repository, first.id, employee_input(manager_id=manager), fixed_clock)


def test_delete_removes_employee_and_history(
    repository: EmployeeRepository, session: Session,
) -> None:
    employee = create_employee(repository, employee_input())
    employee_id = employee.id
    session.add(SalaryHistory(
        employee_id=employee_id, old_salary_minor=9000, new_salary_minor=10000,
        currency="USD", changed_at=datetime(2020, 1, 1),
    ))
    session.commit()
    delete_employee(repository, employee_id)
    assert session.get(Employee, employee_id) is None
    assert session.scalar(select(func.count()).select_from(SalaryHistory)) == 0


def test_delete_rejects_manager_without_deleting_anything(
    repository: EmployeeRepository, session: Session,
) -> None:
    manager = create_employee(repository, employee_input())
    create_employee(
        repository, employee_input(email="report@staff.example", manager_id=manager.id),
    )
    with pytest.raises(HasDirectReports):
        delete_employee(repository, manager.id)
    assert session.scalar(select(func.count()).select_from(Employee)) == 2


def test_failed_create_rolls_back_flushed_employee(
    repository: EmployeeRepository, session: Session,
) -> None:
    class FailingRepository(EmployeeRepository):
        def add(self, employee: Employee) -> None:
            super().add(employee)
            raise RuntimeError("forced write failure")

    with pytest.raises(RuntimeError, match="forced write failure"):
        create_employee(FailingRepository(session), employee_input())
    assert session.scalar(select(func.count()).select_from(Employee)) == 0


def test_failed_delete_restores_history_and_employee(
    repository: EmployeeRepository, session: Session,
) -> None:
    employee = create_employee(repository, employee_input())
    employee_id = employee.id
    session.add(SalaryHistory(
        employee_id=employee_id, old_salary_minor=9000, new_salary_minor=10000,
        currency="USD", changed_at=datetime(2020, 1, 1),
    ))
    session.commit()

    class FailingRepository(EmployeeRepository):
        def delete(self, employee: Employee) -> None:
            super().delete(employee)
            raise RuntimeError("forced delete failure")

    with pytest.raises(RuntimeError, match="forced delete failure"):
        delete_employee(FailingRepository(session), employee_id)
    assert session.get(Employee, employee_id) is not None
    assert session.scalar(select(func.count()).select_from(SalaryHistory)) == 1


@pytest.mark.parametrize("operation", ["get", "update", "delete"])
def test_unknown_employee_raises_not_found(
    repository: EmployeeRepository, operation: str,
) -> None:
    with pytest.raises(EmployeeNotFound):
        if operation == "get":
            get_employee(repository, 999)
        elif operation == "update":
            update_employee(repository, 999, employee_input(), fixed_clock)
        else:
            delete_employee(repository, 999)
