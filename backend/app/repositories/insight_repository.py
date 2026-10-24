from collections.abc import Sequence
from typing import NamedTuple

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Employee, EmploymentStatus, SalaryBand
from app.services.peer_groups import PeerGroupKey

ELIGIBLE_SALARY_STATUSES = (EmploymentStatus.ACTIVE, EmploymentStatus.ON_LEAVE)


class SalaryRow(NamedTuple):
    employee_id: int
    title: str
    level: int
    country: str
    currency: str
    salary_minor: int
    name: str
    department: str


class BandRow(NamedTuple):
    currency: str
    min_minor: int
    mid_minor: int
    max_minor: int


class InsightRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def active_salary_rows(
        self,
        countries: Sequence[str] | None = None,
        titles: Sequence[str] | None = None,
        levels: Sequence[int] | None = None,
        departments: Sequence[str] | None = None,
    ) -> list[SalaryRow]:
        statement = select(
            Employee.id,
            Employee.title,
            Employee.level,
            Employee.country,
            Employee.currency,
            Employee.salary_minor,
            Employee.name,
            Employee.department,
        ).where(Employee.status.in_(ELIGIBLE_SALARY_STATUSES))
        if countries:
            statement = statement.where(Employee.country.in_(countries))
        if titles:
            statement = statement.where(Employee.title.in_(titles))
        if levels:
            statement = statement.where(Employee.level.in_(levels))
        if departments:
            statement = statement.where(Employee.department.in_(departments))
        return [SalaryRow(*row) for row in self._session.execute(statement)]

    def salary_bands(self) -> dict[PeerGroupKey, BandRow]:
        statement = select(
            SalaryBand.title,
            SalaryBand.level,
            SalaryBand.country,
            SalaryBand.currency,
            SalaryBand.min_minor,
            SalaryBand.mid_minor,
            SalaryBand.max_minor,
        )
        rows = self._session.execute(statement)
        return {
            PeerGroupKey(title, level, country): BandRow(currency, minimum, midpoint, maximum)
            for title, level, country, currency, minimum, midpoint, maximum in rows
        }
