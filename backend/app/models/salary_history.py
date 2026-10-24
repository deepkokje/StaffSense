from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class SalaryHistory(Base):
    __tablename__ = "salary_history"
    __table_args__ = (
        CheckConstraint("old_salary_minor >= 0", name="ck_salary_history_old_nonnegative"),
        CheckConstraint("new_salary_minor >= 0", name="ck_salary_history_new_nonnegative"),
        CheckConstraint("length(currency) = 3", name="ck_salary_history_currency_length"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    employee_id: Mapped[int] = mapped_column(
        ForeignKey("employees.id"),
        nullable=False,
        index=True,
    )
    old_salary_minor: Mapped[int] = mapped_column(Integer, nullable=False)
    new_salary_minor: Mapped[int] = mapped_column(Integer, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    changed_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
