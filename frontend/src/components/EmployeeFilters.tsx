import { Button, Col, Input, Row, Select, Space } from "antd";

import type { EmployeeStatus, Gender } from "../api/types";
import {
  COUNTRY_OPTIONS,
  DEPARTMENT_OPTIONS,
  GENDER_OPTIONS,
  LEVEL_OPTIONS,
  STATUS_OPTIONS,
} from "../constants/filterOptions";
import type { EmployeeFiltersState } from "../hooks/useEmployeeTableState";

interface EmployeeFiltersProps {
  search: string;
  filters: EmployeeFiltersState;
  onSearchChange: (search: string) => void;
  onFiltersChange: (filters: EmployeeFiltersState) => void;
  onClearFilters: () => void;
}

const SEARCH_PLACEHOLDER = "Search name or email";
const GENDER_ALL_VALUE = "ALL";

export default function EmployeeFilters({
  search,
  filters,
  onSearchChange,
  onFiltersChange,
  onClearFilters,
}: EmployeeFiltersProps) {
  const updateFilters = (updates: Partial<EmployeeFiltersState>) => {
    onFiltersChange({ ...filters, ...updates });
  };

  return (
    <Space direction="vertical" size="middle" style={{ width: "100%" }}>
      <Input.Search
        aria-label={SEARCH_PLACEHOLDER}
        allowClear
        onChange={(event) => onSearchChange(event.target.value)}
        placeholder={SEARCH_PLACEHOLDER}
        value={search}
      />
      <Row gutter={[12, 12]}>
        <Col xs={24} sm={12} md={6}>
          <Select
            aria-label="Country"
            mode="multiple"
            onChange={(country: string[]) => updateFilters({ country })}
            options={COUNTRY_OPTIONS.map((value) => ({ label: value, value }))}
            placeholder="Country"
            style={{ width: "100%" }}
            value={filters.country}
          />
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Select
            aria-label="Department"
            mode="multiple"
            onChange={(department: string[]) => updateFilters({ department })}
            options={DEPARTMENT_OPTIONS.map((value) => ({ label: value, value }))}
            placeholder="Department"
            style={{ width: "100%" }}
            value={filters.department}
          />
        </Col>
        <Col xs={24} sm={12} md={4}>
          <Select
            aria-label="Level"
            mode="multiple"
            onChange={(level: number[]) => updateFilters({ level })}
            options={LEVEL_OPTIONS.map((value) => ({ label: `Level ${value}`, value }))}
            placeholder="Level"
            style={{ width: "100%" }}
            value={filters.level}
          />
        </Col>
        <Col xs={24} sm={12} md={4}>
          <Select
            aria-label="Status"
            mode="multiple"
            onChange={(status: EmployeeStatus[]) => updateFilters({ status })}
            options={STATUS_OPTIONS.map((value) => ({ label: value, value }))}
            placeholder="Status"
            style={{ width: "100%" }}
            value={filters.status}
          />
        </Col>
        <Col xs={24} sm={12} md={4}>
          <Select
            aria-label="Gender"
            onChange={(gender: Gender | typeof GENDER_ALL_VALUE) =>
              updateFilters({ gender: gender === GENDER_ALL_VALUE ? undefined : gender })
            }
            options={[
              { label: "All genders", value: GENDER_ALL_VALUE },
              ...GENDER_OPTIONS.map((value) => ({ label: value, value })),
            ]}
            style={{ width: "100%" }}
            value={filters.gender ?? GENDER_ALL_VALUE}
          />
        </Col>
      </Row>
      <div>
        <Button onClick={onClearFilters}>Clear filters</Button>
      </div>
    </Space>
  );
}
