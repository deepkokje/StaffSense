import { Drawer, Empty, Skeleton, Table, Tag } from "antd";
import type { TableColumnsType } from "antd";

import type { EmployeeOut, SalaryHistoryEntry } from "../api/types";
import { useSalaryHistoryQuery } from "../hooks/useSalaryHistoryQuery";
import { formatBasisPoints } from "../lib/formatBasisPoints";
import { formatDate } from "../lib/formatDate";
import { formatMinorUnits } from "../lib/formatMoney";
import ErrorBanner from "./ErrorBanner";

const DRAWER_WIDTH = 800;
const ISO_DATE_LENGTH = 10;

interface SalaryHistoryDrawerProps {
  employee?: EmployeeOut;
  onClose: () => void;
}

const columns: TableColumnsType<SalaryHistoryEntry> = [
  {
    title: "Date", key: "date",
    render: (_value: unknown, entry: SalaryHistoryEntry) =>
      formatDate(entry.changed_at.slice(0, ISO_DATE_LENGTH)),
  },
  {
    title: "Old salary", key: "old",
    render: (_value: unknown, entry: SalaryHistoryEntry) =>
      formatMinorUnits(entry.old_salary_minor, entry.currency),
  },
  {
    title: "New salary", key: "new",
    render: (_value: unknown, entry: SalaryHistoryEntry) =>
      formatMinorUnits(entry.new_salary_minor, entry.currency),
  },
  {
    title: "Change", key: "change",
    render: (_value: unknown, entry: SalaryHistoryEntry) => {
      const isRaise = entry.change_minor > 0;
      const isCut = entry.change_minor < 0;
      const sign = isRaise ? "+" : isCut ? "-" : "";
      const absoluteMinor = isCut ? -entry.change_minor : entry.change_minor;
      const percentage = entry.change_bp === null ? "n/a" : formatBasisPoints(entry.change_bp);
      return (
        <Tag color={isRaise ? "green" : isCut ? "red" : undefined}>
          {sign}{formatMinorUnits(absoluteMinor, entry.currency)} ({percentage})
        </Tag>
      );
    },
  },
];

export default function SalaryHistoryDrawer({ employee, onClose }: SalaryHistoryDrawerProps) {
  const query = useSalaryHistoryQuery(employee?.id);
  return (
    <Drawer
      open={employee !== undefined} title={`Salary history - ${employee?.name ?? ""}`}
      width={DRAWER_WIDTH} onClose={onClose}
    >
      {query.isLoading ? (
        <div aria-label="Loading salary history"><Skeleton active /></div>
      ) : query.isError ? (
        <ErrorBanner
          title="Unable to load salary history" message={query.error.message}
          onRetry={() => void query.refetch()} retrying={query.isFetching}
        />
      ) : query.data?.items.length === 0 ? (
        <Empty description="No salary changes recorded" />
      ) : query.data ? (
        <Table
          columns={columns} pagination={false} rowKey="key"
          dataSource={query.data.items.map((entry, index) => ({ ...entry, key: String(index) }))}
        />
      ) : null}
    </Drawer>
  );
}
