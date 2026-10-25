from datetime import date

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.enums import EmploymentStatus, EmploymentType, Gender
from app.money import CURRENCY_EXPONENTS

MIN_LEVEL = 1
MAX_LEVEL = 6
MAX_NAME_LENGTH = 200
MAX_EMAIL_LENGTH = 320
MAX_TITLE_LENGTH = 200
MAX_DEPARTMENT_LENGTH = 100


class EmployeeInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    name: str = Field(min_length=1, max_length=MAX_NAME_LENGTH)
    email: str = Field(min_length=1, max_length=MAX_EMAIL_LENGTH)
    title: str = Field(min_length=1, max_length=MAX_TITLE_LENGTH)
    department: str = Field(min_length=1, max_length=MAX_DEPARTMENT_LENGTH)
    country: str = Field(pattern=r"^[A-Z]{2}$")
    currency: str = Field(pattern=r"^[A-Z]{3}$")
    salary_minor: int = Field(gt=0, strict=True)
    level: int = Field(ge=MIN_LEVEL, le=MAX_LEVEL, strict=True)
    gender: Gender
    employment_type: EmploymentType
    status: EmploymentStatus
    hire_date: date
    manager_id: int | None = Field(default=None, gt=0, strict=True)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        email = value.lower()
        parts = email.split("@")
        if len(parts) != 2 or not all(parts) or any(char.isspace() for char in email):
            raise ValueError("email must have one @ and a valid domain")
        domain = parts[1]
        if "." not in domain or any(not part for part in domain.split(".")):
            raise ValueError("email domain must contain a dot")
        return email

    @field_validator("currency")
    @classmethod
    def validate_currency(cls, value: str) -> str:
        if value not in CURRENCY_EXPONENTS:
            raise ValueError(f"unsupported currency: {value}")
        return value


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
