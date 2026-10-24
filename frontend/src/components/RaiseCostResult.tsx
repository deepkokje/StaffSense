import { Col, Empty, Row, Space, Statistic } from "antd";

import type { RaiseCostReport } from "../api/types";
import { formatMinorUnits } from "../lib/formatMoney";
import CountryCostTable from "./CountryCostTable";
import WhatIfCostSummary from "./WhatIfCostSummary";

interface RaiseCostResultProps {
  report: RaiseCostReport;
  loading: boolean;
  isPlaceholderData: boolean;
}

const USD_CURRENCY = "USD";

export default function RaiseCostResult({
  report, loading, isPlaceholderData,
}: RaiseCostResultProps) {
  return (
    <Space direction="vertical" size="large" style={{ width: "100%" }}>
      <WhatIfCostSummary report={report} label="Department raise cost summary" />
      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12}>
          <Statistic
            title="Current annual payroll (USD)"
            value={report.current_payroll_usd_minor}
            formatter={() => formatMinorUnits(report.current_payroll_usd_minor, USD_CURRENCY)}
          />
        </Col>
        <Col xs={24} sm={12}>
          <Statistic
            title="New annual payroll (USD)"
            value={report.new_payroll_usd_minor}
            formatter={() => formatMinorUnits(report.new_payroll_usd_minor, USD_CURRENCY)}
          />
        </Col>
      </Row>
      {report.employees_affected === 0 ? (
        <Empty description="No employees in this selection" />
      ) : (
        <CountryCostTable
          items={report.by_country}
          loading={loading}
          isPlaceholderData={isPlaceholderData}
        />
      )}
    </Space>
  );
}
