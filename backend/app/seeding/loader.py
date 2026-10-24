from collections.abc import Sequence
from dataclasses import asdict
from typing import Any

from sqlalchemy import bindparam, func, insert, select, update
from sqlalchemy.orm import Session

from app.models import Base, Employee, FxRate, SalaryBand, SalaryHistory
from app.seeding.band_builder import SalaryBandData
from app.seeding.employee_generator import EmployeeSeed, SalaryHistorySeed

BATCH_SIZE = 1_000


def _chunks[T](values: Sequence[T], chunk_size: int) -> list[Sequence[T]]:
    return [values[start : start + chunk_size] for start in range(0, len(values), chunk_size)]


def _insert_rows(
    session: Session,
    model: type[Any],
    rows: Sequence[dict[str, Any]],
) -> None:
    for chunk in _chunks(rows, BATCH_SIZE):
        session.execute(insert(model), list(chunk))


def _employee_rows(employees: Sequence[EmployeeSeed]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for employee in employees:
        row = asdict(employee)
        row["manager_id"] = None
        rows.append(row)
    return rows


def _set_employee_managers(session: Session, employees: Sequence[EmployeeSeed]) -> None:
    manager_updates = [
        {"employee_id": employee.id, "manager_id": employee.manager_id}
        for employee in employees
        if employee.manager_id is not None
    ]
    manager_update_statement = (
        update(Employee.__table__)
        .where(Employee.__table__.c.id == bindparam("employee_id"))
        .values(manager_id=bindparam("manager_id"))
    )
    for chunk in _chunks(manager_updates, BATCH_SIZE):
        session.connection().execute(manager_update_statement, list(chunk))


def _employee_count(session: Session) -> int:
    return session.scalar(select(func.count()).select_from(Employee)) or 0


def load_seed_data(
    session: Session,
    fx_rates: dict[str, int],
    bands: Sequence[SalaryBandData],
    employees: Sequence[EmployeeSeed],
    history: Sequence[SalaryHistorySeed],
    reset: bool = False,
) -> None:
    transaction = session.begin_nested() if session.in_transaction() else session.begin()
    with transaction:
        if reset:
            connection = session.connection()
            Base.metadata.drop_all(bind=connection)
            Base.metadata.create_all(bind=connection)
        else:
            Base.metadata.create_all(bind=session.connection())
            if _employee_count(session):
                raise RuntimeError(
                    "Employees table already contains rows; use reset=True to reload"
                )

        _insert_rows(
            session,
            FxRate,
            [{"currency": currency, "usd_rate_e6": rate} for currency, rate in fx_rates.items()],
        )
        _insert_rows(session, SalaryBand, list(bands))
        _insert_rows(session, Employee, _employee_rows(employees))
        _set_employee_managers(session, employees)
        _insert_rows(session, SalaryHistory, [asdict(row) for row in history])
