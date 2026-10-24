from collections.abc import Iterator
from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine, create_engine, event
from sqlalchemy.engine.interfaces import DBAPIConnection
from sqlalchemy.orm import Session
from sqlalchemy.pool import ConnectionPoolEntry, StaticPool

from app.db import get_session
from app.main import app
from app.models import Base, Employee, EmploymentStatus, EmploymentType, Gender


@pytest.fixture
def engine() -> Iterator[Engine]:
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(test_engine, "connect")
    def enable_foreign_keys(
        connection: DBAPIConnection,
        record: ConnectionPoolEntry,
    ) -> None:
        cursor = connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(bind=test_engine)
    try:
        yield test_engine
    finally:
        Base.metadata.drop_all(bind=test_engine)
        test_engine.dispose()


@pytest.fixture
def session(engine: Engine) -> Iterator[Session]:
    with Session(engine) as test_session:
        yield test_session


@pytest.fixture
def api_client(engine: Engine) -> Iterator[TestClient]:
    def override_get_session() -> Iterator[Session]:
        with Session(engine) as test_session:
            yield test_session

    app.dependency_overrides[get_session] = override_get_session
    with Session(engine) as test_session:
        test_session.add_all(
            [
                make_employee(
                    name=f"API Employee {employee_number:02d}",
                    email=f"api.employee.{employee_number:02d}@example.com",
                    title="Engineer" if employee_number % 2 else "Analyst",
                    level=(employee_number % 6) + 1,
                    department="Engineering" if employee_number % 2 else "Data",
                    country="US" if employee_number % 2 else "IN",
                    currency="USD" if employee_number % 2 else "INR",
                    salary_minor=employee_number * 10_000,
                    salary_usd_minor=employee_number * 10_000,
                    gender=Gender.FEMALE if employee_number % 2 else Gender.MALE,
                    status=EmploymentStatus.ACTIVE
                    if employee_number % 2
                    else EmploymentStatus.ON_LEAVE,
                )
                for employee_number in range(1, 21)
            ]
        )
        test_session.commit()
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.pop(get_session, None)


def make_employee(**overrides: object) -> Employee:
    values: dict[str, object] = {
        "name": "Ada Lovelace",
        "email": "ada@example.com",
        "title": "Engineer",
        "level": 3,
        "department": "Engineering",
        "country": "US",
        "currency": "USD",
        "salary_minor": 12_000_000,
        "salary_usd_minor": 12_000_000,
        "gender": Gender.UNDISCLOSED,
        "employment_type": EmploymentType.FULL_TIME,
        "hire_date": date(2020, 1, 1),
        "status": EmploymentStatus.ACTIVE,
    }
    values.update(overrides)
    return Employee(**values)
