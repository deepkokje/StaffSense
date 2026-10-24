import { keepPreviousData, useQuery } from "@tanstack/react-query";

import { fetchBenchmarks } from "../api/insights";
import type { BenchmarksQuery } from "../api/types";

const BENCHMARKS_QUERY_KEY = "benchmarks";

export function useBenchmarksQuery(query: BenchmarksQuery) {
  return useQuery({
    queryKey: [BENCHMARKS_QUERY_KEY, query],
    queryFn: ({ signal }) => fetchBenchmarks(query, signal),
    placeholderData: keepPreviousData,
  });
}
