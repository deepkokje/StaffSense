import { keepPreviousData, useQuery } from "@tanstack/react-query";

import { fetchRaiseCost } from "../api/insights";
import type { RaiseCostQuery } from "../api/types";
import { queryKeys } from "../lib/queryKeys";

export function useRaiseCostQuery(query: RaiseCostQuery | undefined, enabled: boolean) {
  return useQuery({
    queryKey: [...queryKeys.raiseCost, query],
    queryFn: ({ signal }) => {
      if (query === undefined) {
        throw new Error("A submitted scenario is required to calculate raise cost.");
      }
      return fetchRaiseCost(query, signal);
    },
    enabled: enabled && query !== undefined,
    placeholderData: keepPreviousData,
  });
}
