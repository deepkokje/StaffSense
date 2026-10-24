from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.config import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE
from app.db import get_session
from app.repositories.insight_repository import InsightRepository
from app.schemas.insights import (
    BandsResponse,
    BenchmarksResponse,
    OutliersResponse,
    PeerGroupBenchmarkOut,
)
from app.services.attention import BandStatusFilter, list_band_compliance, list_outliers
from app.services.benchmarks import list_benchmarks
from app.services.outliers import OutlierDirection
from app.services.pagination import FIRST_PAGE, MIN_PAGE_SIZE

MIN_EMPLOYEE_LEVEL = 1
MAX_EMPLOYEE_LEVEL = 6
EmployeeLevel = Annotated[int, Query(ge=MIN_EMPLOYEE_LEVEL, le=MAX_EMPLOYEE_LEVEL)]

router = APIRouter(prefix="/insights", tags=["Insights"])


@router.get("/benchmarks", response_model=BenchmarksResponse)
def get_benchmarks(
    session: Annotated[Session, Depends(get_session)],
    country: Annotated[list[str] | None, Query()] = None,
    title: Annotated[list[str] | None, Query()] = None,
    level: Annotated[list[EmployeeLevel] | None, Query()] = None,
    include_insufficient: bool = True,
) -> BenchmarksResponse:
    benchmarks = list_benchmarks(
        InsightRepository(session),
        country,
        title,
        level,
        include_insufficient,
    )
    return BenchmarksResponse(
        items=[PeerGroupBenchmarkOut.model_validate(benchmark) for benchmark in benchmarks],
    )


@router.get("/bands", response_model=BandsResponse)
def get_bands(
    session: Annotated[Session, Depends(get_session)],
    country: Annotated[list[str] | None, Query()] = None,
    department: Annotated[list[str] | None, Query()] = None,
    title: Annotated[list[str] | None, Query()] = None,
    level: Annotated[list[EmployeeLevel] | None, Query()] = None,
    status: BandStatusFilter | None = None,
    page: Annotated[int, Query(ge=FIRST_PAGE)] = FIRST_PAGE,
    page_size: Annotated[int, Query(ge=MIN_PAGE_SIZE, le=MAX_PAGE_SIZE)] = DEFAULT_PAGE_SIZE,
) -> BandsResponse:
    return BandsResponse.model_validate(
        list_band_compliance(
            InsightRepository(session),
            countries=country,
            departments=department,
            titles=title,
            levels=level,
            status=status,
            page=page,
            page_size=page_size,
        )
    )


@router.get("/outliers", response_model=OutliersResponse)
def get_outliers(
    session: Annotated[Session, Depends(get_session)],
    country: Annotated[list[str] | None, Query()] = None,
    title: Annotated[list[str] | None, Query()] = None,
    level: Annotated[list[EmployeeLevel] | None, Query()] = None,
    direction: OutlierDirection | None = None,
    page: Annotated[int, Query(ge=FIRST_PAGE)] = FIRST_PAGE,
    page_size: Annotated[int, Query(ge=MIN_PAGE_SIZE, le=MAX_PAGE_SIZE)] = DEFAULT_PAGE_SIZE,
) -> OutliersResponse:
    return OutliersResponse.model_validate(
        list_outliers(
            InsightRepository(session),
            countries=country,
            titles=title,
            levels=level,
            direction=direction,
            page=page,
            page_size=page_size,
        )
    )
