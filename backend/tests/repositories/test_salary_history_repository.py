from datetime import datetime

from sqlalchemy.orm import Session

from app.repositories.salary_history_repository import SalaryHistoryRepository
from app.services.salary_history import build_salary_change
from tests.conftest import make_employee


def test_history_is_newest_first_with_id_ties_and_employee_isolation(session: Session) -> None:
    first = make_employee()
    second = make_employee(email="other@staff.example")
    session.add_all([first, second])
    session.commit()
    repository = SalaryHistoryRepository(session)
    for employee_id, old, new, changed_at in [
        (first.id, 1000, 1100, datetime(2026, 1, 1)),
        (first.id, 1100, 1200, datetime(2026, 2, 1)),
        (first.id, 1200, 1300, datetime(2026, 2, 1)),
        (second.id, 1000, 1500, datetime(2026, 3, 1)),
    ]:
        change = build_salary_change(old, new, "USD", changed_at)
        assert change is not None
        repository.add(employee_id, change)
    session.commit()
    assert [row.new_salary_minor for row in repository.list_for_employee(first.id)] == [
        1300, 1200, 1100,
    ]
    assert [row.new_salary_minor for row in repository.list_for_employee(second.id)] == [1500]
