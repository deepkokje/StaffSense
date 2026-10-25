from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import SalaryHistory
from app.services.salary_history import SalaryChange


class SalaryHistoryRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, employee_id: int, change: SalaryChange) -> None:
        self._session.add(SalaryHistory(
            employee_id=employee_id,
            old_salary_minor=change.old_salary_minor,
            new_salary_minor=change.new_salary_minor,
            currency=change.currency,
            changed_at=change.changed_at,
        ))

    def list_for_employee(self, employee_id: int) -> list[SalaryHistory]:
        statement = (
            select(SalaryHistory)
            .where(SalaryHistory.employee_id == employee_id)
            .order_by(SalaryHistory.changed_at.desc(), SalaryHistory.id.desc())
        )
        return list(self._session.scalars(statement))
