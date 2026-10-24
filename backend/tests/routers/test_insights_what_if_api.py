import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Employee, FxRate
from tests.conftest import ATTENTION_TITLE

BAND_ENDPOINT = "/insights/what-if/bring-to-band-min"
RAISE_ENDPOINT = "/insights/what-if/raise"


@pytest.fixture
def what_if_client(attention_client: TestClient, session: Session) -> TestClient:
    session.add_all(
        [
            FxRate(currency="USD", usd_rate_e6=1_000_000),
            FxRate(currency="GBP", usd_rate_e6=1_270_000),
            FxRate(currency="INR", usd_rate_e6=12_000),
        ]
    )
    session.commit()
    return attention_client


def test_band_minimum_cost_response_has_integer_totals_and_country_breakdown(
    what_if_client: TestClient,
) -> None:
    response = what_if_client.get(BAND_ENDPOINT, params={"title": ATTENTION_TITLE})
    assert response.status_code == 200
    assert response.json() == {
        "employees_affected": 1,
        "total_cost_usd_minor": 100,
        "by_country": [
            {
                "country": "US",
                "currency": "USD",
                "employees_affected": 1,
                "cost_local_minor": 100,
                "cost_usd_minor": 100,
            }
        ],
    }


def test_raise_response_includes_current_and_new_payroll(what_if_client: TestClient) -> None:
    response = what_if_client.get(
        RAISE_ENDPOINT,
        params={
            "department": "Data",
            "country": "US",
            "raise_bp": 500,
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        "employees_affected": 1,
        "total_cost_usd_minor": 65,
        "current_payroll_usd_minor": 1_300,
        "new_payroll_usd_minor": 1_365,
        "by_country": [
            {
                "country": "US",
                "currency": "USD",
                "employees_affected": 1,
                "cost_local_minor": 65,
                "cost_usd_minor": 65,
            }
        ],
    }


def test_band_filters_combine_and_repeatable_countries_use_or(what_if_client: TestClient) -> None:
    response = what_if_client.get(
        BAND_ENDPOINT,
        params=[
            ("country", "US"),
            ("country", "GB"),
            ("title", ATTENTION_TITLE),
            ("level", "3"),
            ("department", "Engineering"),
        ],
    )
    assert response.json()["employees_affected"] == 1
    assert (
        what_if_client.get(
            BAND_ENDPOINT,
            params={
                "title": ATTENTION_TITLE,
                "department": "Data",
            },
        ).json()["employees_affected"]
        == 0
    )
    assert (
        what_if_client.get(
            BAND_ENDPOINT,
            params={
                "title": ATTENTION_TITLE,
                "level": 2,
            },
        ).json()["employees_affected"]
        == 0
    )


def test_unknown_department_returns_zero_employees_and_costs(what_if_client: TestClient) -> None:
    assert what_if_client.get(
        RAISE_ENDPOINT,
        params={
            "department": "Unknown",
            "raise_bp": 500,
        },
    ).json() == {
        "employees_affected": 0,
        "total_cost_usd_minor": 0,
        "current_payroll_usd_minor": 0,
        "new_payroll_usd_minor": 0,
        "by_country": [],
    }


def test_department_raise_excludes_terminated_employees(what_if_client: TestClient) -> None:
    data = what_if_client.get(
        RAISE_ENDPOINT,
        params={"department": "Engineering", "country": "US", "raise_bp": 500},
    ).json()
    # Ten existing odd-number employees sum to 100*10000; six attention salaries sum to 6150.
    # Their raises sum to 50000 + 35+40+50+50+60+72 (72.5 ties to even).
    assert data["employees_affected"] == 16
    assert data["current_payroll_usd_minor"] == 1_006_150
    assert data["total_cost_usd_minor"] == 50_307


@pytest.mark.parametrize(
    "params",
    [
        {"department": "Engineering", "raise_bp": 0},
        {"department": "Engineering", "raise_bp": 5_001},
        {"raise_bp": 500},
        {"department": "Engineering"},
    ],
)
def test_invalid_or_missing_raise_parameters_return_422(
    what_if_client: TestClient,
    params: dict[str, object],
) -> None:
    assert what_if_client.get(RAISE_ENDPOINT, params=params).status_code == 422


@pytest.mark.parametrize("level", [0, 7])
def test_invalid_band_min_level_returns_422(what_if_client: TestClient, level: int) -> None:
    assert what_if_client.get(BAND_ENDPOINT, params={"level": level}).status_code == 422


def test_what_if_calculations_do_not_write_salaries(
    what_if_client: TestClient,
    session: Session,
) -> None:
    before = list(
        session.execute(select(Employee.id, Employee.salary_minor, Employee.salary_usd_minor))
    )
    what_if_client.get(BAND_ENDPOINT, params={"title": ATTENTION_TITLE})
    what_if_client.get(RAISE_ENDPOINT, params={"department": "Engineering", "raise_bp": 500})
    session.expire_all()
    after = list(
        session.execute(select(Employee.id, Employee.salary_minor, Employee.salary_usd_minor))
    )
    assert after == before


def test_all_numeric_what_if_fields_are_integers(what_if_client: TestClient) -> None:
    responses = [
        what_if_client.get(BAND_ENDPOINT, params={"title": ATTENTION_TITLE}).json(),
        what_if_client.get(
            RAISE_ENDPOINT,
            params={
                "department": "Data",
                "country": "US",
                "raise_bp": 500,
            },
        ).json(),
    ]
    for data in responses:
        assert all(type(value) is int for key, value in data.items() if key != "by_country")
        for country in data["by_country"]:
            assert all(
                type(value) is int
                for key, value in country.items()
                if key not in ("country", "currency")
            )
