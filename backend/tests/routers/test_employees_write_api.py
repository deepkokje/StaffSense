import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import FxRate
from tests.employee_write_factories import employee_input


@pytest.fixture
def write_client(api_client: TestClient, session: Session) -> TestClient:
    session.add(FxRate(currency="USD", usd_rate_e6=1_000_000))
    session.commit()
    return api_client


def test_create_read_update_delete_employee(write_client: TestClient) -> None:
    payload = employee_input(name="  New Employee  ", email=" NEW@staff.example ").model_dump(
        mode="json",
    )
    response = write_client.post("/employees", json=payload)
    assert response.status_code == 201
    employee = response.json()
    assert employee["name"] == "New Employee"
    assert employee["email"] == "new@staff.example"
    assert type(employee["salary_minor"]) is int
    assert type(employee["salary_usd_minor"]) is int
    employee_id = employee["id"]
    assert write_client.get(f"/employees/{employee_id}").json() == employee
    assert write_client.get("/employees", params={"q": "new@staff.example"}).json()["total"] == 1
    payload["name"] = "Edited Employee"
    response = write_client.put(f"/employees/{employee_id}", json=payload)
    assert response.status_code == 200
    assert write_client.get(f"/employees/{employee_id}").json()["name"] == "Edited Employee"
    assert write_client.delete(f"/employees/{employee_id}").status_code == 204
    assert write_client.get(f"/employees/{employee_id}").status_code == 404


@pytest.mark.parametrize(
    "invalid",
    [
        {"name": "   "}, {"level": 0}, {"level": 7}, {"salary_minor": 0},
        {"salary_minor": True}, {"salary_minor": "100"},
        {"email": "invalid"}, {"email": "a@@domain.example"}, {"currency": "XYZ"},
        {"country": "us"}, {"extra": "forbidden"}, {"salary_usd_minor": 1},
        {"last_raise_date": "2020-01-01"},
    ],
)
def test_create_rejects_invalid_input(
    write_client: TestClient, invalid: dict[str, object],
) -> None:
    payload = employee_input().model_dump(mode="json")
    payload.update(invalid)
    assert write_client.post("/employees", json=payload).status_code == 422


def test_duplicate_email_returns_conflict(write_client: TestClient) -> None:
    payload = employee_input().model_dump(mode="json")
    assert write_client.post("/employees", json=payload).status_code == 201
    payload["email"] = "NEW@staff.example"
    assert write_client.post("/employees", json=payload).status_code == 409


def test_unknown_update_and_delete_return_not_found(write_client: TestClient) -> None:
    assert write_client.put(
        "/employees/99999", json=employee_input().model_dump(mode="json"),
    ).status_code == 404
    assert write_client.delete("/employees/99999").status_code == 404


def test_delete_with_reports_returns_conflict(write_client: TestClient) -> None:
    manager = write_client.post(
        "/employees", json=employee_input().model_dump(mode="json"),
    ).json()
    write_client.post("/employees", json=employee_input(
        email="report@staff.example", manager_id=manager["id"],
    ).model_dump(mode="json"))
    response = write_client.delete(f"/employees/{manager['id']}")
    assert response.status_code == 409
    assert response.json()["detail"] == "employee has direct reports; reassign them first"
