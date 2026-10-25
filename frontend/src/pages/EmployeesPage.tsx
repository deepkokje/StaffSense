import { useState } from "react";
import { Alert, Button, Space, Typography } from "antd";

import type { EmployeeOut, EmployeeQuery } from "../api/types";
import EmployeeFilters from "../components/EmployeeFilters";
import EmployeeFormDrawer from "../components/EmployeeFormDrawer";
import EmployeeTable from "../components/EmployeeTable";
import ErrorBanner from "../components/ErrorBanner";
import SalaryHistoryDrawer from "../components/SalaryHistoryDrawer";
import { useDebouncedValue } from "../hooks/useDebouncedValue";
import { useEmployeeTableState } from "../hooks/useEmployeeTableState";
import { useEmployeesQuery } from "../hooks/useEmployeesQuery";
import { useDeleteEmployee } from "../hooks/useEmployeeMutations";

const PAGE_TITLE = "Employees";

export default function EmployeesPage() {
  const [drawer, setDrawer] = useState<{ employee?: EmployeeOut } | null>(null);
  const [historyEmployee, setHistoryEmployee] = useState<EmployeeOut>();
  const deleteMutation = useDeleteEmployee();
  const tableState = useEmployeeTableState();
  const debouncedSearch = useDebouncedValue(tableState.search);
  const query: EmployeeQuery = {
    page: tableState.page,
    page_size: tableState.pageSize,
    q: debouncedSearch || undefined,
    country: tableState.filters.country.length ? tableState.filters.country : undefined,
    department: tableState.filters.department.length
      ? tableState.filters.department
      : undefined,
    level: tableState.filters.level.length ? tableState.filters.level : undefined,
    status: tableState.filters.status.length ? tableState.filters.status : undefined,
    gender: tableState.filters.gender ? [tableState.filters.gender] : undefined,
    sort_by: tableState.sortBy,
    sort_dir: tableState.sortDir,
  };
  const employeeQuery = useEmployeesQuery(query);
  const errorMessage =
    employeeQuery.error instanceof Error
      ? employeeQuery.error.message
      : "An unexpected error occurred.";

  return (
    <Space direction="vertical" size="large" style={{ width: "100%" }}>
      <Typography.Title level={1}>{PAGE_TITLE}</Typography.Title>
      <Button type="primary" onClick={() => setDrawer({})}>Add employee</Button>
      <EmployeeFilters
        filters={tableState.filters}
        onClearFilters={tableState.clearFilters}
        onFiltersChange={tableState.setFilters}
        onSearchChange={tableState.setSearch}
        search={tableState.search}
      />
      {employeeQuery.isError && (
        <ErrorBanner
          message={errorMessage}
          onRetry={() => void employeeQuery.refetch()}
          retrying={employeeQuery.isFetching}
        />
      )}
      {!employeeQuery.isError && !employeeQuery.data && (
        <Alert message="Loading employees..." type="info" />
      )}
      <EmployeeTable
        data={employeeQuery.displayData}
        isPlaceholderData={employeeQuery.isPlaceholderData}
        loading={employeeQuery.isFetching}
        onClearFilters={tableState.clearFilters}
        onPageChange={(page, pageSize) => {
          if (pageSize !== tableState.pageSize) {
            tableState.setPageSize(pageSize);
          } else {
            tableState.setPage(page);
          }
        }}
        onSortChange={tableState.setSort}
        page={tableState.page}
        pageSize={tableState.pageSize}
        sortBy={tableState.sortBy}
        sortDir={tableState.sortDir}
        onEdit={(employee) => setDrawer({ employee })}
        onDelete={(employee) => deleteMutation.mutate(employee.id)}
        deleting={deleteMutation.isPending}
        onViewHistory={setHistoryEmployee}
      />
      {drawer && (
        <EmployeeFormDrawer employee={drawer.employee} onClose={() => setDrawer(null)} />
      )}
      <SalaryHistoryDrawer employee={historyEmployee} onClose={() => setHistoryEmployee(undefined)} />
    </Space>
  );
}
