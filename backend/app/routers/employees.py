from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.config import settings
from app.db import get_session
from app.models.enums import EmploymentStatus, Gender
from app.repositories.employee_repository import EmployeeRepository
from app.schemas.employee import EmployeePage
from app.services.employee_query import (
    InvalidEmployeeFiltersError,
    SortDirection,
    SortField,
    build_employee_filters,
    list_employees,
)

router = APIRouter()


@router.get("/employees", response_model=EmployeePage)
def get_employees(
    session: Annotated[Session, Depends(get_session)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[
        int,
        Query(ge=1, le=settings.max_page_size),
    ] = settings.default_page_size,
    q: str | None = None,
    country: Annotated[list[str] | None, Query()] = None,
    department: Annotated[list[str] | None, Query()] = None,
    title: Annotated[list[str] | None, Query()] = None,
    level: Annotated[list[int] | None, Query()] = None,
    status: Annotated[list[EmploymentStatus] | None, Query()] = None,
    gender: Annotated[list[Gender] | None, Query()] = None,
    min_salary_usd_minor: Annotated[int | None, Query(ge=0)] = None,
    max_salary_usd_minor: Annotated[int | None, Query(ge=0)] = None,
    sort_by: SortField = SortField.NAME,
    sort_dir: SortDirection = SortDirection.ASC,
) -> EmployeePage:
    try:
        filters = build_employee_filters(
            q=q,
            country=country,
            department=department,
            title=title,
            level=level,
            status=status,
            gender=gender,
            min_salary_usd_minor=min_salary_usd_minor,
            max_salary_usd_minor=max_salary_usd_minor,
            sort_by=sort_by,
            sort_dir=sort_dir,
        )
    except InvalidEmployeeFiltersError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    return list_employees(
        EmployeeRepository(session),
        filters,
        page=page,
        page_size=page_size,
    )
