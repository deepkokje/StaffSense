from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.config import settings
from app.db import get_session
from app.dependencies import Clock, get_clock
from app.models.enums import EmploymentStatus, Gender
from app.repositories.employee_repository import EmployeeRepository
from app.schemas.employee import EmployeeInput, EmployeeOut, EmployeePage
from app.schemas.salary_history import SalaryHistoryEntryOut, SalaryHistoryResponse
from app.services import employee_service
from app.services.employee_query import (
    InvalidEmployeeFiltersError,
    SortDirection,
    SortField,
    build_employee_filters,
    list_employees,
)
from app.services.errors import (
    DuplicateEmail,
    EmployeeError,
    EmployeeNotFound,
    HasDirectReports,
    InvalidManager,
    MissingFxRate,
    UnsupportedChange,
)

router = APIRouter()
ERROR_STATUS_CODES = {
    EmployeeNotFound: 404,
    DuplicateEmail: 409,
    InvalidManager: 422,
    UnsupportedChange: 422,
    HasDirectReports: 409,
    MissingFxRate: 422,
}


async def employee_error_handler(request: Request, error: EmployeeError) -> JSONResponse:
    return JSONResponse(
        status_code=ERROR_STATUS_CODES[type(error)], content={"detail": str(error)},
    )


@router.get("/employees/{employee_id}", response_model=EmployeeOut)
def get_employee(
    employee_id: int, session: Annotated[Session, Depends(get_session)],
) -> EmployeeOut:
    return EmployeeOut.model_validate(
        employee_service.get_employee(EmployeeRepository(session), employee_id),
    )


@router.post("/employees", response_model=EmployeeOut, status_code=201)
def create_employee(
    data: EmployeeInput, session: Annotated[Session, Depends(get_session)],
) -> EmployeeOut:
    return EmployeeOut.model_validate(
        employee_service.create_employee(EmployeeRepository(session), data),
    )


@router.put("/employees/{employee_id}", response_model=EmployeeOut)
def update_employee(
    employee_id: int, data: EmployeeInput,
    session: Annotated[Session, Depends(get_session)],
    clock: Annotated[Clock, Depends(get_clock)],
) -> EmployeeOut:
    return EmployeeOut.model_validate(
        employee_service.update_employee(EmployeeRepository(session), employee_id, data, clock),
    )


@router.get("/employees/{employee_id}/salary-history", response_model=SalaryHistoryResponse)
def get_salary_history(
    employee_id: int, session: Annotated[Session, Depends(get_session)],
) -> SalaryHistoryResponse:
    changes = employee_service.list_salary_history(EmployeeRepository(session), employee_id)
    return SalaryHistoryResponse(
        items=[SalaryHistoryEntryOut.model_validate(change) for change in changes],
    )


@router.delete("/employees/{employee_id}", status_code=204)
def delete_employee(
    employee_id: int, session: Annotated[Session, Depends(get_session)],
) -> Response:
    employee_service.delete_employee(EmployeeRepository(session), employee_id)
    return Response(status_code=204)


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
