import { Table } from "antd";
import type { TableColumnsType } from "antd";

import type { AttentionEmployee, AttentionPageQuery } from "../api/types";
import {
  EMPTY_ATTENTION_MESSAGE, PAGE_SIZE_OPTIONS, PLACEHOLDER_ROW_CLASS,
} from "../constants/attention";

interface AttentionTableProps<T extends AttentionEmployee> {
  columns: TableColumnsType<T>;
  items: T[];
  total: number;
  query: AttentionPageQuery;
  loading: boolean;
  isPlaceholderData: boolean;
  onPageChange: (page: number, pageSize: number) => void;
}

const TABLE_SCROLL_WIDTH = 1_300;

export default function AttentionTable<T extends AttentionEmployee>({
  columns, items, total, query, loading, isPlaceholderData, onPageChange,
}: AttentionTableProps<T>) {
  return (
    <Table<T>
      columns={columns}
      dataSource={items}
      rowKey="employee_id"
      loading={loading}
      rowClassName={() => isPlaceholderData ? PLACEHOLDER_ROW_CLASS : ""}
      locale={{ emptyText: EMPTY_ATTENTION_MESSAGE }}
      scroll={{ x: TABLE_SCROLL_WIDTH }}
      pagination={{
        current: query.page,
        pageSize: query.page_size,
        total,
        pageSizeOptions: PAGE_SIZE_OPTIONS,
        showSizeChanger: true,
        showTotal: (count) => `${count} employees`,
        onChange: onPageChange,
      }}
    />
  );
}
