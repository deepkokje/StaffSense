import { useState } from "react";

import type { AttentionPageQuery } from "../api/types";
import { FIRST_PAGE } from "../constants/attention";

export function useAttentionTableState<T extends AttentionPageQuery>(initialQuery: T) {
  const [query, setQuery] = useState(initialQuery);

  function updateFilters(updates: Partial<T>) {
    setQuery((current) => ({ ...current, ...updates, page: FIRST_PAGE }));
  }

  function changePage(page: number, pageSize: number) {
    setQuery((current) => ({
      ...current,
      page: current.page_size === pageSize ? page : FIRST_PAGE,
      page_size: pageSize,
    }));
  }

  return { query, updateFilters, changePage };
}
