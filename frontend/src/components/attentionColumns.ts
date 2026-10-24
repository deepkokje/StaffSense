import type { TableColumnsType } from "antd";

import type { AttentionEmployee } from "../api/types";
import { formatMinorUnits } from "../lib/formatMoney";

export function attentionColumns<T extends AttentionEmployee>(): TableColumnsType<T> {
  return [
    { title: "Name", dataIndex: "name", key: "name" },
    { title: "Title", dataIndex: "title", key: "title" },
    { title: "Level", dataIndex: "level", key: "level" },
    { title: "Country", dataIndex: "country", key: "country" },
    {
      title: "Salary (local)", key: "salary_minor", align: "right",
      render: (_value: unknown, row: T) => formatMinorUnits(row.salary_minor, row.currency),
    },
  ];
}
