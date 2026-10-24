from pydantic import BaseModel, ConfigDict


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
