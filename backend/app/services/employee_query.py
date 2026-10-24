from collections.abc import Sequence
from dataclasses import dataclass
from enum import Enum
from typing import Protocol, TypeVar

from app.models.enums import EmploymentStatus, Gender
from app.schemas.employee import EmployeeOut, EmployeePage

PAGE_NUMBER_MINIMUM = 1
PAGE_SIZE_MINIMUM = 1
PAGE_COUNT_OFFSET = 1
MINIMUM_EMPLOYEE_LEVEL = 1
MAXIMUM_EMPLOYEE_LEVEL = 6


class InvalidEmployeeFiltersError(ValueError):
    pass


class SortField(str, Enum):
    NAME = "name"
    TITLE = "title"
    DEPARTMENT = "department"
    COUNTRY = "country"
    LEVEL = "level"
    SALARY_USD_MINOR = "salary_usd_minor"
    HIRE_DATE = "hire_date"


class SortDirection(str, Enum):
    ASC = "asc"
    DESC = "desc"


@dataclass(frozen=True)
class EmployeeFilters:
    q: str | None = None
    country: tuple[str, ...] = ()
    department: tuple[str, ...] = ()
    title: tuple[str, ...] = ()
    level: tuple[int, ...] = ()
    status: tuple[str, ...] = ()
    gender: tuple[str, ...] = ()
    min_salary_usd_minor: int | None = None
    max_salary_usd_minor: int | None = None
    sort_by: SortField = SortField.NAME
    sort_dir: SortDirection = SortDirection.ASC


def build_employee_filters(
    *,
    q: str | None = None,
    country: Sequence[str] | None = None,
    department: Sequence[str] | None = None,
    title: Sequence[str] | None = None,
    level: Sequence[int] | None = None,
    status: Sequence[EmploymentStatus] | None = None,
    gender: Sequence[Gender] | None = None,
    min_salary_usd_minor: int | None = None,
    max_salary_usd_minor: int | None = None,
    sort_by: SortField = SortField.NAME,
    sort_dir: SortDirection = SortDirection.ASC,
) -> EmployeeFilters:
    if level and any(
        item < MINIMUM_EMPLOYEE_LEVEL or item > MAXIMUM_EMPLOYEE_LEVEL for item in level
    ):
        raise InvalidEmployeeFiltersError("Each level must be between 1 and 6.")
    if (
        min_salary_usd_minor is not None
        and max_salary_usd_minor is not None
        and min_salary_usd_minor > max_salary_usd_minor
    ):
        raise InvalidEmployeeFiltersError(
            "min_salary_usd_minor must be less than or equal to max_salary_usd_minor."
        )
    return EmployeeFilters(
        q=q,
        country=tuple(country or ()),
        department=tuple(department or ()),
        title=tuple(title or ()),
        level=tuple(level or ()),
        status=tuple(item.value for item in status or ()),
        gender=tuple(item.value for item in gender or ()),
        min_salary_usd_minor=min_salary_usd_minor,
        max_salary_usd_minor=max_salary_usd_minor,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )


EmployeeResult = TypeVar("EmployeeResult", covariant=True)


class EmployeeSearchRepository(Protocol[EmployeeResult]):
    def search(
        self,
        filters: EmployeeFilters,
        offset: int,
        limit: int,
    ) -> Sequence[EmployeeResult]: ...

    def count(self, filters: EmployeeFilters) -> int: ...


def build_page_info(total: int, page: int, page_size: int) -> int:
    if page < PAGE_NUMBER_MINIMUM or page_size < PAGE_SIZE_MINIMUM:
        raise ValueError("Page and page_size must be positive.")
    return (total + page_size - PAGE_COUNT_OFFSET) // page_size if total else 0


def list_employees(
    repository: EmployeeSearchRepository[object],
    filters: EmployeeFilters,
    page: int,
    page_size: int,
) -> EmployeePage:
    total = repository.count(filters)
    total_pages = build_page_info(total, page, page_size)
    offset = (page - PAGE_NUMBER_MINIMUM) * page_size
    employees = repository.search(filters, offset=offset, limit=page_size)
    return EmployeePage(
        items=[EmployeeOut.model_validate(employee) for employee in employees],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )
