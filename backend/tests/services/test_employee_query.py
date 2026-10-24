from dataclasses import dataclass

from app.services.employee_query import (
    EmployeeFilters,
    SortDirection,
    SortField,
    build_page_info,
    list_employees,
)


@dataclass
class FakeEmployee:
    id: int
    name: str
    email: str
    title: str
    level: int
    department: str
    country: str
    currency: str
    salary_minor: int
    salary_usd_minor: int
    gender: str
    employment_type: str
    hire_date: str
    last_raise_date: None
    status: str
    manager_id: None


class FakeRepository:
    def __init__(self) -> None:
        self.offset: int | None = None
        self.limit: int | None = None

    def count(self, filters: EmployeeFilters) -> int:
        return 25

    def search(
        self,
        filters: EmployeeFilters,
        offset: int,
        limit: int,
    ) -> list[FakeEmployee]:
        self.offset = offset
        self.limit = limit
        return []


def test_build_page_info_handles_empty_exact_and_remainder_totals() -> None:
    assert build_page_info(total=0, page=1, page_size=10) == 0
    assert build_page_info(total=20, page=1, page_size=10) == 2
    assert build_page_info(total=21, page=1, page_size=10) == 3


def test_list_employees_passes_page_offset_and_limit() -> None:
    repository = FakeRepository()
    page = list_employees(
        repository,
        EmployeeFilters(sort_by=SortField.NAME, sort_dir=SortDirection.ASC),
        page=3,
        page_size=10,
    )

    assert repository.offset == 20
    assert repository.limit == 10
    assert page.total == 25
    assert page.total_pages == 3
