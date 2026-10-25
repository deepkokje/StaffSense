import { keepPreviousData, useQuery } from "@tanstack/react-query";

import { fetchBringToBandMin } from "../api/insights";
import type { BringToBandMinQuery } from "../api/types";
import { queryKeys } from "../lib/queryKeys";

export function useBringToBandMinQuery(query: BringToBandMinQuery) {
  return useQuery({
    queryKey: [...queryKeys.bringToBandMin, query],
    queryFn: ({ signal }) => fetchBringToBandMin(query, signal),
    placeholderData: keepPreviousData,
  });
}
