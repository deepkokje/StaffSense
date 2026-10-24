import { keepPreviousData, useQuery } from "@tanstack/react-query";

import { fetchOutliers } from "../api/insights";
import type { OutliersQuery } from "../api/types";

export function useOutliersQuery(query: OutliersQuery) {
  return useQuery({
    queryKey: ["outliers", query],
    queryFn: ({ signal }) => fetchOutliers(query, signal),
    placeholderData: keepPreviousData,
  });
}
