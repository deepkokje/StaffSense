from datetime import date

from sqlalchemy import CheckConstraint, Enum, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base
from app.models.enums import EmploymentStatus, EmploymentType, Gender


class Employee(Base):
    __tablename__ = "employees"
    __table_args__ = (
        CheckConstraint("salary_minor >= 0", name="ck_employees_salary_minor_nonnegative"),
        CheckConstraint("salary_usd_minor >= 0", name="ck_employees_salary_usd_minor_nonnegative"),
        CheckConstraint("level BETWEEN 1 AND 6", name="ck_employees_level_range"),
        CheckConstraint("length(country) = 2", name="ck_employees_country_length"),
        CheckConstraint("length(currency) = 3", name="ck_employees_currency_length"),
        Index("ix_employees_country", "country"),
        Index("ix_employees_department", "department"),
        Index("ix_employees_title", "title"),
        Index("ix_employees_level", "level"),
        Index("ix_employees_salary_usd_minor", "salary_usd_minor"),
        Index("ix_employees_title_level_country", "title", "level", "country"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    email: Mapped[str] = mapped_column(String(320), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    level: Mapped[int] = mapped_column(Integer, nullable=False)
    department: Mapped[str] = mapped_column(String(100), nullable=False)
    country: Mapped[str] = mapped_column(String(2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    salary_minor: Mapped[int] = mapped_column(Integer, nullable=False)
    salary_usd_minor: Mapped[int] = mapped_column(Integer, nullable=False)
    gender: Mapped[Gender] = mapped_column(
        Enum(
            Gender,
            name="gender",
            native_enum=False,
            values_callable=lambda enum_type: [member.value for member in enum_type],
        ),
        nullable=False,
    )
    manager_id: Mapped[int | None] = mapped_column(ForeignKey("employees.id"), nullable=True)
    employment_type: Mapped[EmploymentType] = mapped_column(
        Enum(
            EmploymentType,
            name="employment_type",
            native_enum=False,
            values_callable=lambda enum_type: [member.value for member in enum_type],
        ),
        nullable=False,
    )
    hire_date: Mapped[date] = mapped_column(nullable=False)
    last_raise_date: Mapped[date | None] = mapped_column(nullable=True)
    status: Mapped[EmploymentStatus] = mapped_column(
        Enum(
            EmploymentStatus,
            name="employment_status",
            native_enum=False,
            values_callable=lambda enum_type: [member.value for member in enum_type],
        ),
        nullable=False,
    )
