import { useState } from "react";

import type { BenchmarksQuery } from "../api/types";

const INITIAL_PAGE = 1;
const DEFAULT_PAGE_SIZE = 25;
const INITIAL_QUERY: BenchmarksQuery = { include_insufficient: true };

export function useBenchmarkFilters() {
  const [query, setQuery] = useState<BenchmarksQuery>(INITIAL_QUERY);
  const [page, setPage] = useState(INITIAL_PAGE);
  const [pageSize, setPageSize] = useState(DEFAULT_PAGE_SIZE);

  function updateFilters(updates: Partial<BenchmarksQuery>) {
    setQuery((current) => ({ ...current, ...updates }));
    setPage(INITIAL_PAGE);
  }

  function changePage(nextPage: number, nextPageSize: number) {
    setPage(nextPageSize === pageSize ? nextPage : INITIAL_PAGE);
    setPageSize(nextPageSize);
  }

  return { query, page, pageSize, updateFilters, changePage };
}
