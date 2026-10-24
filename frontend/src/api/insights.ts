import { getJson } from "./client";
import type {
  BandsQuery, BandsResponse, BenchmarksQuery, BenchmarksResponse,
  OutliersQuery, OutliersResponse,
  BandMinCostReport, BringToBandMinQuery, RaiseCostQuery, RaiseCostReport,
} from "./types";

const BENCHMARKS_ENDPOINT = "/insights/benchmarks";

export function fetchBenchmarks(
  query: BenchmarksQuery,
  signal?: AbortSignal,
): Promise<BenchmarksResponse> {
  return getJson<BenchmarksResponse>(BENCHMARKS_ENDPOINT, { ...query }, signal);
}

export function fetchBands(query: BandsQuery, signal?: AbortSignal): Promise<BandsResponse> {
  return getJson<BandsResponse>("/insights/bands", { ...query }, signal);
}

export function fetchOutliers(
  query: OutliersQuery,
  signal?: AbortSignal,
): Promise<OutliersResponse> {
  return getJson<OutliersResponse>("/insights/outliers", { ...query }, signal);
}

export function fetchBringToBandMin(
  query: BringToBandMinQuery,
  signal?: AbortSignal,
): Promise<BandMinCostReport> {
  return getJson<BandMinCostReport>("/insights/what-if/bring-to-band-min", { ...query }, signal);
}

export function fetchRaiseCost(
  query: RaiseCostQuery,
  signal?: AbortSignal,
): Promise<RaiseCostReport> {
  return getJson<RaiseCostReport>("/insights/what-if/raise", { ...query }, signal);
}
