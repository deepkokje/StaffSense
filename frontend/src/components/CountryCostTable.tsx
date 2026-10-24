import { Table } from "antd";
import type { TableColumnsType } from "antd";

import type { CountryCost } from "../api/types";
import { formatMinorUnits } from "../lib/formatMoney";

const USD_CURRENCY = "USD";
const TABLE_SCROLL_WIDTH = 650;
const columns: TableColumnsType<CountryCost> = [
  { title: "Country", dataIndex: "country", key: "country" },
  { title: "Employees affected", dataIndex: "employees_affected", key: "employees_affected" },
  {
    title: "Cost (local currency)", key: "cost_local_minor", align: "right",
    render: (_value: unknown, row: CountryCost) => formatMinorUnits(row.cost_local_minor, row.currency),
  },
  {
    title: "Cost (USD)", key: "cost_usd_minor", align: "right",
    render: (_value: unknown, row: CountryCost) => formatMinorUnits(row.cost_usd_minor, USD_CURRENCY),
  },
];

interface CountryCostTableProps {
  items: CountryCost[];
  loading: boolean;
  isPlaceholderData: boolean;
}

export default function CountryCostTable({
  items, loading, isPlaceholderData,
}: CountryCostTableProps) {
  return (
    <Table<CountryCost>
      columns={columns}
      dataSource={items}
      rowKey="country"
      loading={loading}
      pagination={false}
      scroll={{ x: TABLE_SCROLL_WIDTH }}
      rowClassName={() => isPlaceholderData ? "employee-row-placeholder" : ""}
    />
  );
}
