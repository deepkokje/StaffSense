from sqlalchemy import CheckConstraint, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class FxRate(Base):
    __tablename__ = "fx_rates"
    __table_args__ = (
        CheckConstraint("usd_rate_e6 > 0", name="ck_fx_rates_usd_rate_positive"),
        CheckConstraint("length(currency) = 3", name="ck_fx_rates_currency_length"),
    )

    currency: Mapped[str] = mapped_column(String(3), primary_key=True)
    usd_rate_e6: Mapped[int] = mapped_column(Integer, nullable=False)
