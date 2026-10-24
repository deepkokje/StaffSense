from sqlalchemy import CheckConstraint, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class SalaryBand(Base):
    __tablename__ = "salary_bands"
    __table_args__ = (
        UniqueConstraint("title", "level", "country", name="uq_salary_bands_title_level_country"),
        CheckConstraint(
            "min_minor >= 0 AND min_minor <= mid_minor AND mid_minor <= max_minor",
            name="ck_salary_bands_ordered_nonnegative",
        ),
        CheckConstraint("level BETWEEN 1 AND 6", name="ck_salary_bands_level_range"),
        CheckConstraint("length(country) = 2", name="ck_salary_bands_country_length"),
        CheckConstraint("length(currency) = 3", name="ck_salary_bands_currency_length"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    level: Mapped[int] = mapped_column(Integer, nullable=False)
    country: Mapped[str] = mapped_column(String(2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    min_minor: Mapped[int] = mapped_column(Integer, nullable=False)
    mid_minor: Mapped[int] = mapped_column(Integer, nullable=False)
    max_minor: Mapped[int] = mapped_column(Integer, nullable=False)
