import { keepPreviousData, useQuery, useQueryClient } from "@tanstack/react-query";

import { fetchEmployees } from "../api/employees";
import type { EmployeePage, EmployeeQuery } from "../api/types";

const EMPLOYEES_QUERY_KEY = "employees";

function isEmployeePage(value: unknown): value is EmployeePage {
  return (
    typeof value === "object" &&
    value !== null &&
    "items" in value &&
    Array.isArray(value.items) &&
    "total" in value &&
    typeof value.total === "number"
  );
}

export function useEmployeesQuery(query: EmployeeQuery) {
  const queryClient = useQueryClient();
  const queryResult = useQuery({
    queryKey: [EMPLOYEES_QUERY_KEY, query],
    queryFn: ({ signal }) => fetchEmployees(query, signal),
    placeholderData: keepPreviousData,
  });
  const mostRecentCachedData = queryClient
    .getQueryCache()
    .findAll({ queryKey: [EMPLOYEES_QUERY_KEY] })
    .filter((cachedQuery) => cachedQuery.state.data !== undefined)
    .sort(
      (firstQuery, secondQuery) =>
        secondQuery.state.dataUpdatedAt - firstQuery.state.dataUpdatedAt,
    )[0]?.state.data;
  const mostRecentCachedPage = isEmployeePage(mostRecentCachedData)
    ? mostRecentCachedData
    : undefined;

  return {
    ...queryResult,
    displayData: queryResult.data ?? mostRecentCachedPage,
  };
}
