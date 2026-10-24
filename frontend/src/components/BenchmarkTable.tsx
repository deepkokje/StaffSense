import { Table, Tag } from "antd";
import type { TableColumnsType } from "antd";

import type { BenchmarkStats, PeerGroupBenchmark } from "../api/types";
import { formatMinorUnits } from "../lib/formatMoney";

interface BenchmarkTableProps {
  items: PeerGroupBenchmark[];
  loading: boolean;
  isPlaceholderData: boolean;
  page: number;
  pageSize: number;
  onPageChange: (page: number, pageSize: number) => void;
}

const MIN_PEER_GROUP_SIZE = 5;
const MISSING_STAT = "-";
const TABLE_SCROLL_WIDTH = 1_100;
const STAT_COLUMNS: { label: string; key: keyof BenchmarkStats }[] = [
  { label: "Min", key: "min" },
  { label: "P25", key: "p25" },
  { label: "Median", key: "median" },
  { label: "P75", key: "p75" },
  { label: "Max", key: "max" },
];

const columns: TableColumnsType<PeerGroupBenchmark> = [
  { title: "Country", dataIndex: ["key", "country"], key: "country" },
  { title: "Title", dataIndex: ["key", "title"], key: "title" },
  { title: "Level", dataIndex: ["key", "level"], key: "level" },
  {
    title: "Headcount",
    key: "headcount",
    render: (_value: unknown, row: PeerGroupBenchmark) => (
      <>
        {row.headcount}{" "}
        {row.insufficient_data && (
          <Tag>Insufficient data (n &lt; {MIN_PEER_GROUP_SIZE})</Tag>
        )}
      </>
    ),
  },
  ...STAT_COLUMNS.map(({ label, key }) => ({
    title: label,
    key,
    align: "right" as const,
    render: (_value: unknown, row: PeerGroupBenchmark) =>
      row.insufficient_data || row.stats === null
        ? MISSING_STAT
        : formatMinorUnits(row.stats[key], row.currency),
  })),
];

export default function BenchmarkTable({
  items, loading, isPlaceholderData, page, pageSize, onPageChange,
}: BenchmarkTableProps) {
  return (
    <Table<PeerGroupBenchmark>
      columns={columns}
      dataSource={items}
      loading={loading}
      rowKey={(row) => JSON.stringify([row.key.title, row.key.level, row.key.country])}
      rowClassName={() => isPlaceholderData ? "employee-row-placeholder" : ""}
      locale={{ emptyText: "No peer groups match these filters" }}
      scroll={{ x: TABLE_SCROLL_WIDTH }}
      pagination={{
        current: page,
        pageSize,
        showSizeChanger: true,
        onChange: onPageChange,
      }}
    />
  );
}
