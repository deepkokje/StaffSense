from datetime import date

import pytest
from sqlalchemy.orm import Session

from app.models.enums import EmploymentStatus, Gender
from app.repositories.employee_repository import EmployeeRepository
from app.services.employee_query import EmployeeFilters, SortDirection, SortField
from tests.conftest import make_employee

FIRST_EMPLOYEE_ID = 1
SECOND_EMPLOYEE_ID = 2
SPECIAL_EMPLOYEE_ID = 3


@pytest.fixture
def employees(session: Session):
    rows = []
    for index in range(1, 21):
        rows.append(
            make_employee(
                name=f"Employee {index:02d}",
                email=f"employee.{index:02d}@example.com",
                title="Engineer" if index % 2 else "Analyst",
                level=(index % 4) + 1,
                department="Engineering" if index % 2 else "Data",
                country="US" if index % 2 else "IN",
                currency="USD" if index % 2 else "INR",
                salary_minor=index * 10_000,
                salary_usd_minor=index * 10_000,
                gender=Gender.FEMALE if index % 2 else Gender.MALE,
                status=EmploymentStatus.ACTIVE
                if index % 2
                else EmploymentStatus.ON_LEAVE,
                hire_date=date(2020, 1, (index % 28) + 1),
            )
        )
    rows[FIRST_EMPLOYEE_ID - 1].name = "Ada Lovelace"
    rows[SECOND_EMPLOYEE_ID - 1].email = "needle@example.com"
    rows[SPECIAL_EMPLOYEE_ID - 1].name = "Percent%_Person"
    rows[SPECIAL_EMPLOYEE_ID - 1].email = "literal@example.com"
    session.add_all(rows)
    session.commit()
    return rows


def _ids(repository: EmployeeRepository, filters: EmployeeFilters) -> list[int]:
    return [employee.id for employee in repository.search(filters, offset=0, limit=100)]


def test_search_without_filters_returns_all_employees(
    session: Session,
    employees,
) -> None:
    assert len(EmployeeRepository(session).search(EmployeeFilters(), 0, 100)) == 20


@pytest.mark.parametrize(
    ("filters", "expected_count"),
    [
        (EmployeeFilters(country=("US",)), 10),
        (EmployeeFilters(department=("Engineering",)), 10),
        (EmployeeFilters(title=("Analyst",)), 10),
        (EmployeeFilters(level=(1,)), 5),
        (EmployeeFilters(status=("ACTIVE",)), 10),
        (EmployeeFilters(gender=("FEMALE",)), 10),
    ],
)
def test_each_filter_matches_its_field(
    session: Session,
    employees,
    filters: EmployeeFilters,
    expected_count: int,
) -> None:
    repository = EmployeeRepository(session)
    assert len(repository.search(filters, offset=0, limit=100)) == expected_count


def test_repeatable_country_and_level_filters_use_or(
    session: Session,
    employees,
) -> None:
    repository = EmployeeRepository(session)

    assert len(repository.search(EmployeeFilters(country=("US", "IN")), 0, 100)) == 20
    assert len(repository.search(EmployeeFilters(level=(1, 2)), 0, 100)) == 10


def test_different_filters_combine_with_and(session: Session, employees) -> None:
    result = EmployeeRepository(session).search(
        EmployeeFilters(country=("US",), department=("Engineering",), level=(2,)),
        offset=0,
        limit=100,
    )

    assert all(
        employee.country == "US"
        and employee.department == "Engineering"
        and employee.level == 2
        for employee in result
    )


def test_salary_filter_bounds_are_inclusive(session: Session, employees) -> None:
    result = EmployeeRepository(session).search(
        EmployeeFilters(min_salary_usd_minor=20_000, max_salary_usd_minor=40_000),
        offset=0,
        limit=100,
    )

    assert sorted(employee.salary_usd_minor for employee in result) == [
        20_000,
        30_000,
        40_000,
    ]


@pytest.mark.parametrize(
    ("query", "expected_id"),
    [("ADA LOVELACE", FIRST_EMPLOYEE_ID), ("NEEDLE", SECOND_EMPLOYEE_ID)],
)
def test_search_matches_name_and_email_case_insensitively(
    session: Session,
    employees,
    query: str,
    expected_id: int,
) -> None:
    assert _ids(EmployeeRepository(session), EmployeeFilters(q=query)) == [expected_id]


@pytest.mark.parametrize(
    ("query", "expected_id"),
    [("%", SPECIAL_EMPLOYEE_ID), ("_", SPECIAL_EMPLOYEE_ID)],
)
def test_search_treats_like_wildcards_literally(
    session: Session,
    employees,
    query: str,
    expected_id: int,
) -> None:
    assert _ids(EmployeeRepository(session), EmployeeFilters(q=query)) == [expected_id]


@pytest.mark.parametrize("sort_dir", [SortDirection.ASC, SortDirection.DESC])
def test_salary_sorting_supports_ascending_and_descending(
    session: Session,
    employees,
    sort_dir: SortDirection,
) -> None:
    ids = _ids(
        EmployeeRepository(session),
        EmployeeFilters(sort_by=SortField.SALARY_USD_MINOR, sort_dir=sort_dir),
    )

    assert ids == (
        list(range(1, 21)) if sort_dir is SortDirection.ASC else list(range(20, 0, -1))
    )


@pytest.mark.parametrize("sort_dir", [SortDirection.ASC, SortDirection.DESC])
def test_name_sorting_supports_ascending_and_descending(
    session: Session,
    employees,
    sort_dir: SortDirection,
) -> None:
    repository = EmployeeRepository(session)
    result = repository.search(
        EmployeeFilters(sort_by=SortField.NAME, sort_dir=sort_dir),
        offset=0,
        limit=100,
    )

    expected = sorted(result, key=lambda employee: employee.name)
    if sort_dir is SortDirection.DESC:
        expected.reverse()
    assert [employee.name for employee in result] == [employee.name for employee in expected]


def test_equal_sort_values_use_id_as_final_tie_breaker(session: Session, employees) -> None:
    employees[1].salary_usd_minor = employees[0].salary_usd_minor
    session.commit()
    ids = _ids(
        EmployeeRepository(session),
        EmployeeFilters(sort_by=SortField.SALARY_USD_MINOR),
    )

    assert ids[:2] == [FIRST_EMPLOYEE_ID, SECOND_EMPLOYEE_ID]


def test_count_ignores_search_pagination(session: Session, employees) -> None:
    repository = EmployeeRepository(session)
    filters = EmployeeFilters(country=("US",))

    assert repository.count(filters) == 10
    assert len(repository.search(filters, offset=5, limit=2)) == 2
