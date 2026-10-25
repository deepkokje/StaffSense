from collections.abc import Iterator
from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.dependencies import get_clock
from app.main import app
from app.models import FxRate, SalaryHistory
from tests.employee_write_factories import employee_input

FIXED_TIME = datetime(2026, 10, 25, 9, 30, tzinfo=UTC)


@pytest.fixture
def history_client(api_client: TestClient, session: Session) -> Iterator[TestClient]:
    session.add(FxRate(currency="USD", usd_rate_e6=1_000_000))
    session.commit()
    app.dependency_overrides[get_clock] = lambda: lambda: FIXED_TIME
    try:
        yield api_client
    finally:
        app.dependency_overrides.pop(get_clock, None)


def test_unknown_employee_returns_404(history_client: TestClient) -> None:
    assert history_client.get("/employees/99999/salary-history").status_code == 404


def test_known_employee_without_history_returns_empty(history_client: TestClient) -> None:
    response = history_client.get("/employees/1/salary-history")
    assert response.status_code == 200
    assert response.json() == {"items": []}


def test_put_records_history_and_name_only_or_identical_saves_do_not(
    history_client: TestClient,
) -> None:
    data = employee_input(salary_minor=1000).model_dump(mode="json")
    employee_id = history_client.post("/employees", json=data).json()["id"]
    data["salary_minor"] = 1100
    response = history_client.put(f"/employees/{employee_id}", json=data)
    assert response.status_code == 200
    assert response.json()["last_raise_date"] == "2026-10-25"
    history = history_client.get(f"/employees/{employee_id}/salary-history")
    assert history.status_code == 200
    entry = history.json()["items"][0]
    assert set(entry) == {
        "old_salary_minor", "new_salary_minor", "currency", "changed_at",
        "change_minor", "change_bp",
    }
    assert entry["old_salary_minor"] == 1000
    assert entry["new_salary_minor"] == 1100
    assert entry["change_minor"] == 100
    assert entry["change_bp"] == 1000
    assert entry["changed_at"].startswith("2026-10-25T09:30:00")
    assert entry["currency"] == "USD"
    for field in ("old_salary_minor", "new_salary_minor", "change_minor", "change_bp"):
        assert type(entry[field]) is int
    data["name"] = "New name"
    assert history_client.put(f"/employees/{employee_id}", json=data).status_code == 200
    assert history_client.put(f"/employees/{employee_id}", json=data).status_code == 200
    assert len(history_client.get(f"/employees/{employee_id}/salary-history").json()["items"]) == 1
    data["currency"] = "INR"
    rejected = history_client.put(f"/employees/{employee_id}", json=data)
    assert rejected.status_code == 422
    assert rejected.json()["detail"] == "changing currency is not supported"


def test_seed_style_rows_are_newest_first_with_stable_ties_and_null_zero_percentage(
    history_client: TestClient, session: Session,
) -> None:
    for old, new, when in [
        (0, 500, datetime(2020, 1, 1)),
        (500, 550, datetime(2021, 1, 1)),
        (550, 500, datetime(2021, 1, 1)),
    ]:
        session.add(SalaryHistory(
            employee_id=1, old_salary_minor=old, new_salary_minor=new,
            currency="USD", changed_at=when,
        ))
    session.commit()
    items = history_client.get("/employees/1/salary-history").json()["items"]
    assert [item["new_salary_minor"] for item in items] == [500, 550, 500]
    assert items[0]["change_minor"] == -50
    assert items[2]["change_bp"] is None
