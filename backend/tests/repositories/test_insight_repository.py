import pytest
from sqlalchemy.orm import Session

from app.models import EmploymentStatus, FxRate, SalaryBand
from app.repositories.insight_repository import InsightRepository, SalaryRow
from app.services.peer_groups import PeerGroupKey
from tests.conftest import make_employee


def test_fx_rates_returns_currency_to_integer_rate_mapping(session: Session) -> None:
    session.add_all(
        [FxRate(currency="USD", usd_rate_e6=1_000_000), FxRate(currency="INR", usd_rate_e6=12_000)]
    )
    session.commit()
    assert InsightRepository(session).fx_rates() == {"USD": 1_000_000, "INR": 12_000}


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
    assert all(row.name == "Ada Lovelace" and row.department == "Engineering" for row in rows)


def test_department_filter_is_applied_with_other_filters(repository: InsightRepository) -> None:
    assert len(repository.active_salary_rows(departments=["Engineering"])) == 2
    assert repository.active_salary_rows(departments=["Data"]) == []
    assert (
        len(
            repository.active_salary_rows(
                countries=["JP"],
                departments=["Engineering"],
            )
        )
        == 1
    )


def test_salary_bands_are_lightweight_and_keyed_by_title_level_country(session: Session) -> None:
    session.add(
        SalaryBand(
            title="Engineer",
            level=3,
            country="US",
            currency="USD",
            min_minor=800,
            mid_minor=1_000,
            max_minor=1_200,
        )
    )
    session.commit()
    bands = InsightRepository(session).salary_bands()
    assert list(bands) == [PeerGroupKey("Engineer", 3, "US")]
    assert tuple(bands[PeerGroupKey("Engineer", 3, "US")]) == ("USD", 800, 1_000, 1_200)


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
