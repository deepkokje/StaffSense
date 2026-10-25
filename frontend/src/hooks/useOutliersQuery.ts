import { keepPreviousData, useQuery } from "@tanstack/react-query";

import { fetchOutliers } from "../api/insights";
import type { OutliersQuery } from "../api/types";
import { queryKeys } from "../lib/queryKeys";

export function useOutliersQuery(query: OutliersQuery) {
  return useQuery({
    queryKey: [...queryKeys.outliers, query],
    queryFn: ({ signal }) => fetchOutliers(query, signal),
    placeholderData: keepPreviousData,
  });
}
