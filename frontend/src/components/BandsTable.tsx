import { Tag } from "antd";
import type { TableColumnsType } from "antd";
import type { ComponentProps } from "react";

import type { FlaggedEmployee } from "../api/types";
import { formatMinorUnits } from "../lib/formatMoney";
import { formatPermille } from "../lib/formatPermille";
import AttentionTable from "./AttentionTable";
import { attentionColumns } from "./attentionColumns";

const BAND_COLUMNS = [
  { label: "Band min", key: "band_min_minor" },
  { label: "Band mid", key: "band_mid_minor" },
  { label: "Band max", key: "band_max_minor" },
] as const;

const columns: TableColumnsType<FlaggedEmployee> = [
  ...attentionColumns<FlaggedEmployee>(),
  ...BAND_COLUMNS.map(({ label, key }) => ({
    title: label, key, align: "right" as const,
    render: (_value: unknown, row: FlaggedEmployee) => formatMinorUnits(row[key], row.currency),
  })),
  {
    title: "Compa-ratio", key: "compa_ratio_permille", align: "right",
    render: (_value: unknown, row: FlaggedEmployee) => formatPermille(row.compa_ratio_permille),
  },
  {
    title: "Gap to band", key: "gap_to_band_minor", align: "right",
    render: (_value: unknown, row: FlaggedEmployee) =>
      formatMinorUnits(row.gap_to_band_minor, row.currency),
  },
  {
    title: "Status", key: "status",
    render: (_value: unknown, row: FlaggedEmployee) => (
      <Tag color={row.status === "below_min" ? "red" : "orange"}>
        {row.status === "below_min" ? "Below min" : "Above max"}
      </Tag>
    ),
  },
];

type BandsTableProps = Omit<ComponentProps<typeof AttentionTable<FlaggedEmployee>>, "columns">;

export default function BandsTable(props: BandsTableProps) {
  return <AttentionTable {...props} columns={columns} />;
}
