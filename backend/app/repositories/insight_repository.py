from collections.abc import Sequence
from typing import NamedTuple

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Employee, EmploymentStatus

BENCHMARK_STATUSES = (EmploymentStatus.ACTIVE, EmploymentStatus.ON_LEAVE)


class SalaryRow(NamedTuple):
    employee_id: int
    title: str
    level: int
    country: str
    currency: str
    salary_minor: int


class InsightRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def active_salary_rows(
        self,
        countries: Sequence[str] | None = None,
        titles: Sequence[str] | None = None,
        levels: Sequence[int] | None = None,
    ) -> list[SalaryRow]:
        statement = select(
            Employee.id,
            Employee.title,
            Employee.level,
            Employee.country,
            Employee.currency,
            Employee.salary_minor,
        ).where(Employee.status.in_(BENCHMARK_STATUSES))
        if countries:
            statement = statement.where(Employee.country.in_(countries))
        if titles:
            statement = statement.where(Employee.title.in_(titles))
        if levels:
            statement = statement.where(Employee.level.in_(levels))
        return [SalaryRow(*row) for row in self._session.execute(statement)]
