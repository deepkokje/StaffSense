import { getJson } from "./client";
import type { BenchmarksQuery, BenchmarksResponse } from "./types";

const BENCHMARKS_ENDPOINT = "/insights/benchmarks";

export function fetchBenchmarks(
  query: BenchmarksQuery,
  signal?: AbortSignal,
): Promise<BenchmarksResponse> {
  return getJson<BenchmarksResponse>(BENCHMARKS_ENDPOINT, { ...query }, signal);
}
