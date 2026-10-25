from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SalaryHistoryEntryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    old_salary_minor: int
    new_salary_minor: int
    currency: str
    changed_at: datetime
    change_minor: int
    change_bp: int | None


class SalaryHistoryResponse(BaseModel):
    items: list[SalaryHistoryEntryOut]
