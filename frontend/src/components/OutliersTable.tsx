import { Tag } from "antd";
import type { TableColumnsType } from "antd";
import type { ComponentProps } from "react";

import type { Outlier } from "../api/types";
import { formatMinorUnits } from "../lib/formatMoney";
import { formatPermille } from "../lib/formatPermille";
import AttentionTable from "./AttentionTable";
import { attentionColumns } from "./attentionColumns";

const columns: TableColumnsType<Outlier> = [
  ...attentionColumns<Outlier>(),
  {
    title: "Peer median (local)", key: "group_median_minor", align: "right",
    render: (_value: unknown, row: Outlier) =>
      formatMinorUnits(row.group_median_minor, row.currency),
  },
  {
    title: "Deviation", key: "deviation_permille", align: "right",
    render: (_value: unknown, row: Outlier) => (
      <Tag color={row.direction === "below" ? "red" : "orange"}>
        {row.direction === "above" ? "+" : ""}{formatPermille(row.deviation_permille)}
      </Tag>
    ),
  },
  { title: "Peer group size", dataIndex: "group_headcount", key: "group_headcount" },
];

type OutliersTableProps = Omit<ComponentProps<typeof AttentionTable<Outlier>>, "columns">;

export default function OutliersTable(props: OutliersTableProps) {
  return <AttentionTable {...props} columns={columns} />;
}
