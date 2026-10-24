from collections.abc import Iterator
from datetime import date

import pytest
from sqlalchemy import Engine, create_engine, event
from sqlalchemy.engine.interfaces import DBAPIConnection
from sqlalchemy.orm import Session
from sqlalchemy.pool import ConnectionPoolEntry

from app.models import Base, Employee, EmploymentStatus, EmploymentType, Gender


@pytest.fixture
def engine() -> Iterator[Engine]:
    test_engine = create_engine("sqlite://")

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
