import { keepPreviousData, useQuery } from "@tanstack/react-query";

import { fetchBenchmarks } from "../api/insights";
import type { BenchmarksQuery } from "../api/types";
import { queryKeys } from "../lib/queryKeys";

export function useBenchmarksQuery(query: BenchmarksQuery) {
  return useQuery({
    queryKey: [...queryKeys.benchmarks, query],
    queryFn: ({ signal }) => fetchBenchmarks(query, signal),
    placeholderData: keepPreviousData,
  });
}
