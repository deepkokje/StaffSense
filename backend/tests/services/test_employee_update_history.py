from datetime import date, datetime

import pytest
from sqlalchemy.orm import Session

from app.models import FxRate
from app.repositories.employee_repository import EmployeeRepository
from app.repositories.salary_history_repository import SalaryHistoryRepository
from app.services.employee_service import create_employee, update_employee
from app.services.errors import UnsupportedChange
from app.services.salary_history import SalaryChange
from tests.employee_write_factories import employee_input

FIXED_TIME = datetime(2026, 10, 25, 9, 30)
PREVIOUS_RAISE = date(2025, 1, 2)


def fixed_clock() -> datetime:
    return FIXED_TIME


@pytest.fixture
def repository(session: Session) -> EmployeeRepository:
    session.add(FxRate(currency="INR", usd_rate_e6=12000))
    session.commit()
    return EmployeeRepository(session)


def test_salary_change_records_exact_values_and_recomputes_usd(
    repository: EmployeeRepository,
) -> None:
    data = employee_input(currency="INR", country="IN", salary_minor=10000)
    employee = create_employee(repository, data)
    assert repository.salary_history.list_for_employee(employee.id) == []
    update_employee(
        repository, employee.id, data.model_copy(update={"salary_minor": 20000}), fixed_clock,
    )
    rows = repository.salary_history.list_for_employee(employee.id)
    assert len(rows) == 1
    row = rows[0]
    assert (row.old_salary_minor, row.new_salary_minor, row.currency, row.changed_at) == (
        10000, 20000, "INR", FIXED_TIME,
    )
    # INR 200 * USD 0.012 = USD 2.40 = 240 cents.
    assert employee.salary_usd_minor == 240
    assert employee.last_raise_date == FIXED_TIME.date()


@pytest.mark.parametrize("changes", [{"name": "Renamed"}, {}])
def test_unchanged_salary_records_nothing_and_does_not_call_clock(
    repository: EmployeeRepository, changes: dict[str, object],
) -> None:
    data = employee_input(currency="INR")
    employee = create_employee(repository, data)

    def unused_clock() -> datetime:
        raise AssertionError("No salary change should require a timestamp")

    update_employee(repository, employee.id, data.model_copy(update=changes), unused_clock)
    assert repository.salary_history.list_for_employee(employee.id) == []
    assert employee.last_raise_date is None


def test_salary_cut_preserves_last_raise_date(
    repository: EmployeeRepository, session: Session,
) -> None:
    data = employee_input(currency="INR", salary_minor=10000)
    employee = create_employee(repository, data)
    employee.last_raise_date = PREVIOUS_RAISE
    session.commit()
    update_employee(
        repository, employee.id, data.model_copy(update={"salary_minor": 9000}), fixed_clock,
    )
    assert employee.last_raise_date == PREVIOUS_RAISE
    assert len(repository.salary_history.list_for_employee(employee.id)) == 1


def test_currency_change_is_rejected_without_history(repository: EmployeeRepository) -> None:
    data = employee_input(currency="INR")
    employee = create_employee(repository, data)
    with pytest.raises(UnsupportedChange, match="changing currency is not supported"):
        update_employee(
            repository, employee.id, data.model_copy(update={"currency": "USD"}), fixed_clock,
        )
    assert employee.currency == "INR"
    assert repository.salary_history.list_for_employee(employee.id) == []


def test_history_failure_rolls_back_salary_usd_and_raise_date(
    repository: EmployeeRepository, session: Session,
) -> None:
    data = employee_input(currency="INR", salary_minor=10000)
    employee = create_employee(repository, data)
    employee_id = employee.id

    class FailingHistoryRepository(SalaryHistoryRepository):
        def add(self, employee_id: int, change: SalaryChange) -> None:
            super().add(employee_id, change)
            session.flush()
            raise RuntimeError("forced history failure")

    repository.salary_history = FailingHistoryRepository(session)
    with pytest.raises(RuntimeError, match="forced history failure"):
        update_employee(
            repository, employee_id, data.model_copy(update={"salary_minor": 20000}), fixed_clock,
        )
    session.expire_all()
    reloaded = repository.get(employee_id)
    assert reloaded is not None
    assert reloaded.salary_minor == 10000
    assert reloaded.salary_usd_minor == 120
    assert reloaded.last_raise_date is None
    assert repository.salary_history.list_for_employee(employee_id) == []
