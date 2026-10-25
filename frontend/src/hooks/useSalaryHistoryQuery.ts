import { useQuery } from "@tanstack/react-query";

import { fetchSalaryHistory } from "../api/employees";
import { queryKeys } from "../lib/queryKeys";

export function useSalaryHistoryQuery(employeeId: number | undefined) {
  return useQuery({
    queryKey: [...queryKeys.salaryHistory, employeeId],
    queryFn: ({ signal }) => {
      if (employeeId === undefined) {
        throw new Error("Select an employee to load salary history.");
      }
      return fetchSalaryHistory(employeeId, signal);
    },
    enabled: employeeId !== undefined,
  });
}
