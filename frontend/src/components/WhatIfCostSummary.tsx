import { Col, Row, Statistic } from "antd";

import type { BandMinCostReport } from "../api/types";
import { formatMinorUnits } from "../lib/formatMoney";

interface WhatIfCostSummaryProps {
  report: BandMinCostReport;
  label: string;
}

const USD_CURRENCY = "USD";

export default function WhatIfCostSummary({ report, label }: WhatIfCostSummaryProps) {
  return (
    <Row gutter={[16, 16]} aria-label={label}>
      <Col xs={24} sm={12}>
        <Statistic
          title="Annual base salary cost (USD)"
          value={report.total_cost_usd_minor}
          formatter={() => formatMinorUnits(report.total_cost_usd_minor, USD_CURRENCY)}
        />
      </Col>
      <Col xs={24} sm={12}>
        <Statistic title="Employees affected" value={report.employees_affected} />
      </Col>
    </Row>
  );
}
