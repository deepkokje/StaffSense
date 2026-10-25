import { Button, Empty, Popconfirm, Space, Table, Typography } from "antd";
import type { TableColumnsType, TableProps } from "antd";

import type {
  EmployeeOut,
  EmployeePage,
  SortDirection,
  SortField,
} from "../api/types";
import { formatDate } from "../lib/formatDate";
import { formatMinorUnits } from "../lib/formatMoney";

const PAGE_SIZE_OPTIONS = ["25", "50", "100"];
const DEFAULT_SORT_FIELD: SortField = "name";
const DEFAULT_SORT_DIRECTION: SortDirection = "asc";
const PLACEHOLDER_ROW_CLASS = "employee-row-placeholder";
const SORT_FIELD_VALUES = new Set<string>([
  "name",
  "title",
  "department",
  "country",
  "level",
  "salary_usd_minor",
  "hire_date",
]);

interface EmployeeTableProps {
  data: EmployeePage | undefined;
  page: number;
  pageSize: number;
  sortBy: SortField;
  sortDir: SortDirection;
  loading: boolean;
  isPlaceholderData: boolean;
  onPageChange: (page: number, pageSize: number) => void;
  onSortChange: (field: SortField, direction: SortDirection) => void;
  onClearFilters: () => void;
  onEdit?: (employee: EmployeeOut) => void;
  onDelete?: (employee: EmployeeOut) => void;
  onViewHistory?: (employee: EmployeeOut) => void;
  deleting?: boolean;
}

type EmployeeColumn = NonNullable<TableColumnsType<EmployeeOut>[number]>;
type TableSorter = Parameters<NonNullable<TableProps<EmployeeOut>["onChange"]>>[2];

function getSortOrder(
  field: SortField,
  sortBy: SortField,
  sortDir: SortDirection,
): "ascend" | "descend" | null {
  if (field !== sortBy) {
    return null;
  }
  return sortDir === "asc" ? "ascend" : "descend";
}

function createSortableColumn(
  title: string,
  field: SortField,
  sortBy: SortField,
  sortDir: SortDirection,
): EmployeeColumn {
  return {
    title,
    dataIndex: field,
    key: field,
    sorter: true,
    sortOrder: getSortOrder(field, sortBy, sortDir),
  };
}

function createColumns(
  sortBy: SortField,
  sortDir: SortDirection,
  onEdit?: (employee: EmployeeOut) => void,
  onDelete?: (employee: EmployeeOut) => void,
  deleting?: boolean,
  onViewHistory?: (employee: EmployeeOut) => void,
): TableColumnsType<EmployeeOut> {
  return [
    {
      ...createSortableColumn("Name", "name", sortBy, sortDir),
      render: (_value: unknown, employee: EmployeeOut) => employee.name,
    },
    createSortableColumn("Title", "title", sortBy, sortDir),
    createSortableColumn("Department", "department", sortBy, sortDir),
    createSortableColumn("Country", "country", sortBy, sortDir),
    createSortableColumn("Level", "level", sortBy, sortDir),
    {
      title: "Salary (local)",
      dataIndex: "salary_minor",
      key: "salary_minor",
      align: "right",
      render: (_value: unknown, employee: EmployeeOut) =>
        formatMinorUnits(employee.salary_minor, employee.currency),
    },
    {
      ...createSortableColumn("Salary (USD)", "salary_usd_minor", sortBy, sortDir),
      align: "right",
      render: (_value: unknown, employee: EmployeeOut) =>
        formatMinorUnits(employee.salary_usd_minor, "USD"),
    },
    {
      ...createSortableColumn("Hire date", "hire_date", sortBy, sortDir),
      render: (_value: unknown, employee: EmployeeOut) => formatDate(employee.hire_date),
    },
    {
      title: "Status",
      dataIndex: "status",
      key: "status",
    },
    {
      title: "Actions",
      key: "actions",
      render: (_value: unknown, employee: EmployeeOut) => (
        <Space>
          <Button onClick={() => onEdit?.(employee)} disabled={!onEdit}>Edit</Button>
          <Button onClick={() => onViewHistory?.(employee)} disabled={!onViewHistory}>
            History
          </Button>
          <Popconfirm
            title="Delete this employee?" okText="Delete" cancelText="Cancel"
            onConfirm={() => onDelete?.(employee)} disabled={!onDelete || deleting}
          >
            <Button danger disabled={!onDelete || deleting}>Delete</Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];
}

function getSortField(sorter: TableSorter): SortField | undefined {
  const sorterResult = Array.isArray(sorter) ? sorter[0] : sorter;
  const field = sorterResult?.field;
  return isSortField(field) ? field : undefined;
}

function isSortField(value: unknown): value is SortField {
  return typeof value === "string" && SORT_FIELD_VALUES.has(value);
}

export default function EmployeeTable({
  data,
  page,
  pageSize,
  sortBy,
  sortDir,
  loading,
  isPlaceholderData,
  onPageChange,
  onSortChange,
  onClearFilters,
  onEdit,
  onDelete,
  deleting,
  onViewHistory,
}: EmployeeTableProps) {
  const columns = createColumns(sortBy, sortDir, onEdit, onDelete, deleting, onViewHistory);
  const handleTableChange: TableProps<EmployeeOut>["onChange"] = (
    pagination,
    _filters,
    sorter,
    extra,
  ) => {
    if (!Array.isArray(sorter) && sorter.order === null) {
      onSortChange(DEFAULT_SORT_FIELD, DEFAULT_SORT_DIRECTION);
    } else {
      const sortedField = getSortField(sorter);
      if (sortedField) {
        const sorterResult = Array.isArray(sorter) ? sorter[0] : sorter;
        const direction: SortDirection =
          sorterResult?.order === "descend" ? "desc" : DEFAULT_SORT_DIRECTION;
        onSortChange(sortedField, direction);
      }
    }
    if (
      extra.action === "paginate" &&
      pagination.current &&
      pagination.pageSize
    ) {
      onPageChange(pagination.current, pagination.pageSize);
    }
  };

  return (
    <>
      <Typography.Text strong>
        {data?.total ?? 0} employees
      </Typography.Text>
      <Table<EmployeeOut>
        columns={columns}
        dataSource={data?.items ?? []}
        loading={loading}
        locale={{
          emptyText: (
            <Empty
              description="No employees match these filters"
              image={Empty.PRESENTED_IMAGE_SIMPLE}
            >
              <Button onClick={onClearFilters}>Clear filters</Button>
            </Empty>
          ),
        }}
        onChange={handleTableChange}
        pagination={{
          current: page,
          pageSize,
          pageSizeOptions: PAGE_SIZE_OPTIONS,
          showSizeChanger: true,
          total: data?.total ?? 0,
        }}
        rowClassName={() => (isPlaceholderData ? PLACEHOLDER_ROW_CLASS : "")}
        rowKey="id"
      />
    </>
  );
}
