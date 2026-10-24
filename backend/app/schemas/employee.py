from datetime import date

from pydantic import BaseModel, ConfigDict

from app.models.enums import EmploymentStatus, EmploymentType, Gender


class EmployeeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    title: str
    level: int
    department: str
    country: str
    currency: str
    salary_minor: int
    salary_usd_minor: int
    gender: Gender
    employment_type: EmploymentType
    hire_date: date
    last_raise_date: date | None
    status: EmploymentStatus
    manager_id: int | None


class EmployeePage(BaseModel):
    items: list[EmployeeOut]
    total: int
    page: int
    page_size: int
    total_pages: int
