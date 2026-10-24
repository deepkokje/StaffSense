import { getJson } from "./client";
import type {
  BandsQuery, BandsResponse, BenchmarksQuery, BenchmarksResponse,
  OutliersQuery, OutliersResponse,
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
