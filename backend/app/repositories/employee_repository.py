from typing import Any

from sqlalchemy import Select, func, or_, select
from sqlalchemy.orm import Session

from app.models import Employee
from app.services.employee_query import EmployeeFilters, SortDirection, SortField

LIKE_ESCAPE_CHARACTER = "\\"
SEARCH_PATTERN_PREFIX = "%"
SEARCH_PATTERN_SUFFIX = "%"
SORT_COLUMNS = {
    SortField.NAME: Employee.name,
    SortField.TITLE: Employee.title,
    SortField.DEPARTMENT: Employee.department,
    SortField.COUNTRY: Employee.country,
    SortField.LEVEL: Employee.level,
    SortField.SALARY_USD_MINOR: Employee.salary_usd_minor,
    SortField.HIRE_DATE: Employee.hire_date,
}


def _escape_like_value(value: str) -> str:
    escaped_value = value.replace(LIKE_ESCAPE_CHARACTER, LIKE_ESCAPE_CHARACTER * 2)
    escaped_value = escaped_value.replace("%", f"{LIKE_ESCAPE_CHARACTER}%")
    return escaped_value.replace("_", f"{LIKE_ESCAPE_CHARACTER}_")


def _apply_filters(statement: Select[Any], filters: EmployeeFilters) -> Select[Any]:
    if filters.q:
        search_pattern = (
            f"{SEARCH_PATTERN_PREFIX}{_escape_like_value(filters.q)}{SEARCH_PATTERN_SUFFIX}"
        )
        statement = statement.where(
            or_(
                Employee.name.ilike(search_pattern, escape=LIKE_ESCAPE_CHARACTER),
                Employee.email.ilike(search_pattern, escape=LIKE_ESCAPE_CHARACTER),
            )
        )
    if filters.country:
        statement = statement.where(Employee.country.in_(filters.country))
    if filters.department:
        statement = statement.where(Employee.department.in_(filters.department))
    if filters.title:
        statement = statement.where(Employee.title.in_(filters.title))
    if filters.level:
        statement = statement.where(Employee.level.in_(filters.level))
    if filters.status:
        statement = statement.where(Employee.status.in_(filters.status))
    if filters.gender:
        statement = statement.where(Employee.gender.in_(filters.gender))
    if filters.min_salary_usd_minor is not None:
        statement = statement.where(
            Employee.salary_usd_minor >= filters.min_salary_usd_minor
        )
    if filters.max_salary_usd_minor is not None:
        statement = statement.where(
            Employee.salary_usd_minor <= filters.max_salary_usd_minor
        )
    return statement


class EmployeeRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def search(
        self,
        filters: EmployeeFilters,
        offset: int,
        limit: int,
    ) -> list[Employee]:
        statement = _apply_filters(select(Employee), filters)
        sort_column = SORT_COLUMNS[filters.sort_by]
        sort_expression = (
            sort_column.asc()
            if filters.sort_dir is SortDirection.ASC
            else sort_column.desc()
        )
        statement = statement.order_by(sort_expression, Employee.id.asc())
        statement = statement.offset(offset).limit(limit)
        return list(self._session.scalars(statement).all())

    def count(self, filters: EmployeeFilters) -> int:
        statement = _apply_filters(select(func.count()).select_from(Employee), filters)
        return int(self._session.scalar(statement) or 0)
