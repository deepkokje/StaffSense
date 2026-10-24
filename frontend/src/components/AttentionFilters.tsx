import { Select, Space } from "antd";

import type { PeerFilters } from "../api/types";
import { ATTENTION_FILTER_WIDTH } from "../constants/attention";
import {
  COUNTRY_OPTIONS, DEPARTMENT_OPTIONS, LEVEL_OPTIONS, TITLE_OPTIONS,
} from "../constants/filterOptions";

type FilterValues = PeerFilters & { department?: readonly string[] };

interface AttentionFiltersProps {
  filters: FilterValues;
  showDepartment?: boolean;
  onChange: (updates: Partial<FilterValues>) => void;
}

const TEXT_FILTERS = [
  { key: "country", label: "Country", options: COUNTRY_OPTIONS },
  { key: "department", label: "Department", options: DEPARTMENT_OPTIONS },
  { key: "title", label: "Title", options: TITLE_OPTIONS },
] as const;

export default function AttentionFilters({
  filters, showDepartment = false, onChange,
}: AttentionFiltersProps) {
  return (
    <Space wrap size="middle">
      {TEXT_FILTERS.filter((filter) => showDepartment || filter.key !== "department")
        .map(({ key, label, options }) => (
          <Select<string[]>
            key={key}
            aria-label={`Attention ${key}`}
            placeholder={label}
            mode="multiple"
            virtual={false}
            allowClear
            style={{ minWidth: ATTENTION_FILTER_WIDTH }}
            value={filters[key] ? [...filters[key]] : []}
            options={options.map((value) => ({ label: value, value }))}
            onChange={(values) => onChange({ [key]: values.length ? values : undefined })}
          />
        ))}
      <Select<number[]>
        aria-label="Attention level"
        placeholder="Level"
        mode="multiple"
        virtual={false}
        allowClear
        style={{ minWidth: ATTENTION_FILTER_WIDTH }}
        value={filters.level ? [...filters.level] : []}
        options={LEVEL_OPTIONS.map((value) => ({ label: `Level ${value}`, value }))}
        onChange={(level) => onChange({ level: level.length ? level : undefined })}
      />
    </Space>
  );
}
