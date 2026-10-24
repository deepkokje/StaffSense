from pydantic import BaseModel, ConfigDict

from app.services.band_compliance import BandStatus
from app.services.outliers import OutlierDirection


class PeerGroupKeyOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    title: str
    level: int
    country: str


class BenchmarkStatsOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    min: int
    p25: int
    median: int
    p75: int
    max: int


class PeerGroupBenchmarkOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    key: PeerGroupKeyOut
    currency: str
    headcount: int
    stats: BenchmarkStatsOut | None
    insufficient_data: bool


class BenchmarksResponse(BaseModel):
    items: list[PeerGroupBenchmarkOut]


class BandSummaryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    below_min: int
    within_band: int
    above_max: int
    no_band: int


class FlaggedEmployeeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    employee_id: int
    name: str
    department: str
    title: str
    level: int
    country: str
    currency: str
    salary_minor: int
    band_min_minor: int
    band_mid_minor: int
    band_max_minor: int
    compa_ratio_permille: int
    status: BandStatus
    gap_to_band_minor: int


class BandsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    summary: BandSummaryOut
    items: list[FlaggedEmployeeOut]
    total: int
    page: int
    page_size: int


class OutlierOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    employee_id: int
    name: str
    title: str
    level: int
    country: str
    currency: str
    salary_minor: int
    group_median_minor: int
    group_headcount: int
    deviation_permille: int
    direction: OutlierDirection


class OutliersResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    items: list[OutlierOut]
    total: int
    page: int
    page_size: int
