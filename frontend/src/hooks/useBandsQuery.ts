import { keepPreviousData, useQuery } from "@tanstack/react-query";

import { fetchBands } from "../api/insights";
import type { BandsQuery } from "../api/types";

export function useBandsQuery(query: BandsQuery) {
  return useQuery({
    queryKey: ["bands", query],
    queryFn: ({ signal }) => fetchBands(query, signal),
    placeholderData: keepPreviousData,
  });
}
