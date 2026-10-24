import pytest
from sqlalchemy.orm import Session

from app.models import EmploymentStatus
from app.repositories.insight_repository import InsightRepository, SalaryRow
from tests.conftest import make_employee


@pytest.fixture
def repository(session: Session) -> InsightRepository:
    session.add_all(
        [
            make_employee(email="active@example.com", title="Engineer", level=2),
            make_employee(
                email="leave@example.com",
                title="Designer",
                level=3,
                country="JP",
                currency="JPY",
                status=EmploymentStatus.ON_LEAVE,
            ),
            make_employee(email="terminated@example.com", status=EmploymentStatus.TERMINATED),
        ]
    )
    session.commit()
    return InsightRepository(session)


def test_only_active_and_on_leave_employees_are_selected(repository: InsightRepository) -> None:
    rows = repository.active_salary_rows()
    assert len(rows) == 2
    assert {row.employee_id for row in rows} == {1, 2}
    assert all(isinstance(row, SalaryRow) for row in rows)


@pytest.mark.parametrize(
    "countries,titles,levels,expected",
    [
        (["JP"], None, None, [2]),
        (None, ["Engineer"], None, [1]),
        (None, None, [3], [2]),
        (["US", "JP"], ["Designer"], [3], [2]),
        (["US"], ["Designer"], [3], []),
    ],
)
def test_filters_apply_individually_and_combine_with_and(
    repository: InsightRepository,
    countries: list[str] | None,
    titles: list[str] | None,
    levels: list[int] | None,
    expected: list[int],
) -> None:
    assert [
        row.employee_id for row in repository.active_salary_rows(countries, titles, levels)
    ] == expected
