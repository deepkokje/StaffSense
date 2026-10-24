import { Select, Space, Switch, Typography } from "antd";

import type { BenchmarksQuery } from "../api/types";
import { COUNTRY_OPTIONS, LEVEL_OPTIONS, TITLE_OPTIONS } from "../constants/filterOptions";

interface BenchmarkFiltersProps {
  query: BenchmarksQuery;
  onChange: (updates: Partial<BenchmarksQuery>) => void;
}

const FILTER_WIDTH = 220;

export default function BenchmarkFilters({ query, onChange }: BenchmarkFiltersProps) {
  return (
    <Space wrap size="middle">
      <Select<string[]>
        aria-label="Benchmark country"
        placeholder="Country"
        mode="multiple"
        virtual={false}
        allowClear
        style={{ minWidth: FILTER_WIDTH }}
        value={query.country ? [...query.country] : []}
        options={COUNTRY_OPTIONS.map((value) => ({ label: value, value }))}
        onChange={(country) => onChange({ country: country.length ? country : undefined })}
      />
      <Select<string[]>
        aria-label="Benchmark title"
        placeholder="Title"
        mode="multiple"
        virtual={false}
        allowClear
        style={{ minWidth: FILTER_WIDTH }}
        value={query.title ? [...query.title] : []}
        options={TITLE_OPTIONS.map((value) => ({ label: value, value }))}
        onChange={(title) => onChange({ title: title.length ? title : undefined })}
      />
      <Select<number[]>
        aria-label="Benchmark level"
        placeholder="Level"
        mode="multiple"
        virtual={false}
        allowClear
        style={{ minWidth: FILTER_WIDTH }}
        value={query.level ? [...query.level] : []}
        options={LEVEL_OPTIONS.map((value) => ({ label: `Level ${value}`, value }))}
        onChange={(level) => onChange({ level: level.length ? level : undefined })}
      />
      <Space>
        <Switch
          aria-label="Show small groups"
          checked={query.include_insufficient}
          onChange={(include_insufficient) => onChange({ include_insufficient })}
        />
        <Typography.Text>Show small groups</Typography.Text>
      </Space>
    </Space>
  );
}
