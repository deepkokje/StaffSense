from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db import get_session
from app.repositories.insight_repository import InsightRepository
from app.schemas.insights import BenchmarksResponse, PeerGroupBenchmarkOut
from app.services.benchmarks import list_benchmarks

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
