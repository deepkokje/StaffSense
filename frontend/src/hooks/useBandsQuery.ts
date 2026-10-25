import { keepPreviousData, useQuery } from "@tanstack/react-query";

import { fetchBands } from "../api/insights";
import type { BandsQuery } from "../api/types";
import { queryKeys } from "../lib/queryKeys";

export function useBandsQuery(query: BandsQuery) {
  return useQuery({
    queryKey: [...queryKeys.bands, query],
    queryFn: ({ signal }) => fetchBands(query, signal),
    placeholderData: keepPreviousData,
  });
}
