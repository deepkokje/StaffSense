import { useCallback, useState } from "react";

import type { EmployeeStatus, Gender, SortDirection, SortField } from "../api/types";

export interface EmployeeFiltersState {
  country: string[];
  department: string[];
  level: number[];
  status: EmployeeStatus[];
  gender: Gender | undefined;
}

export interface EmployeeTableState {
  page: number;
  pageSize: number;
  search: string;
  filters: EmployeeFiltersState;
  sortBy: SortField;
  sortDir: SortDirection;
}

const INITIAL_PAGE = 1;
const INITIAL_PAGE_SIZE = 25;
const INITIAL_SORT_FIELD: SortField = "name";
const INITIAL_SORT_DIRECTION: SortDirection = "asc";

const EMPTY_FILTERS: EmployeeFiltersState = {
  country: [],
  department: [],
  level: [],
  status: [],
  gender: undefined,
};

function haveFiltersChanged(
  currentFilters: EmployeeFiltersState,
  nextFilters: EmployeeFiltersState,
): boolean {
  return (
    currentFilters.country !== nextFilters.country ||
    currentFilters.department !== nextFilters.department ||
    currentFilters.level !== nextFilters.level ||
    currentFilters.status !== nextFilters.status ||
    currentFilters.gender !== nextFilters.gender
  );
}

export function useEmployeeTableState() {
  const [state, setState] = useState<EmployeeTableState>({
    page: INITIAL_PAGE,
    pageSize: INITIAL_PAGE_SIZE,
    search: "",
    filters: EMPTY_FILTERS,
    sortBy: INITIAL_SORT_FIELD,
    sortDir: INITIAL_SORT_DIRECTION,
  });

  const setPage = useCallback((page: number) => {
    setState((current) => ({ ...current, page }));
  }, []);

  const setPageSize = useCallback((pageSize: number) => {
    setState((current) => ({ ...current, page: INITIAL_PAGE, pageSize }));
  }, []);

  const setSearch = useCallback((search: string) => {
    setState((current) =>
      current.search === search
        ? current
        : { ...current, page: INITIAL_PAGE, search },
    );
  }, []);

  const setFilters = useCallback((filters: EmployeeFiltersState) => {
    setState((current) =>
      haveFiltersChanged(current.filters, filters)
        ? { ...current, page: INITIAL_PAGE, filters }
        : current,
    );
  }, []);

  const setSort = useCallback((sortBy: SortField, sortDir: SortDirection) => {
    setState((current) =>
      current.sortBy === sortBy && current.sortDir === sortDir
        ? current
        : { ...current, page: INITIAL_PAGE, sortBy, sortDir },
    );
  }, []);

  const clearFilters = useCallback(() => {
    setState((current) => ({
      ...current,
      page: INITIAL_PAGE,
      search: "",
      filters: { ...EMPTY_FILTERS },
    }));
  }, []);

  return {
    ...state,
    setPage,
    setPageSize,
    setSearch,
    setFilters,
    setSort,
    clearFilters,
  };
}
