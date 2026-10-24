import { keepPreviousData, useQuery } from "@tanstack/react-query";

import { fetchBringToBandMin } from "../api/insights";
import type { BringToBandMinQuery } from "../api/types";

export function useBringToBandMinQuery(query: BringToBandMinQuery) {
  return useQuery({
    queryKey: ["bring-to-band-min", query],
    queryFn: ({ signal }) => fetchBringToBandMin(query, signal),
    placeholderData: keepPreviousData,
  });
}
