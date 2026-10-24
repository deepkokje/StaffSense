import { Space, Typography } from "antd";
import { Cell, Pie, PieChart, Tooltip } from "recharts";

import type { BandMinCostReport } from "../../api/types";
import { formatMinorUnits } from "../../lib/formatMoney";

interface CostPieChartProps {
  report: BandMinCostReport;
}

const USD_CURRENCY = "USD";
const CHART_SIZE = 240;
const RADIUS = 95;
const COLORS = ["#1677ff", "#722ed1", "#13c2c2", "#fa8c16", "#eb2f96", "#389e0d", "#595959", "#ad6800"];

export default function CostPieChart({ report }: CostPieChartProps) {
  const slices = report.by_country.map((country, index) => ({
    country: country.country,
    cost_usd_minor: country.cost_usd_minor,
    amount: formatMinorUnits(country.cost_usd_minor, USD_CURRENCY),
    color: COLORS[index % COLORS.length],
  }));

  return (
    <Space direction="vertical" size="middle" style={{ width: "100%" }}>
      <Typography.Text strong>
        {formatMinorUnits(report.total_cost_usd_minor, USD_CURRENCY)}
      </Typography.Text>
      {report.total_cost_usd_minor > 0 && (
        <PieChart
          width={CHART_SIZE}
          height={CHART_SIZE}
          title="Annual band-minimum cost by country in USD pie chart"
          style={{ maxWidth: "100%", margin: "0 auto" }}
        >
          <Pie
            data={slices}
            dataKey="cost_usd_minor"
            nameKey="country"
            outerRadius={RADIUS}
            isAnimationActive={false}
          >
            {slices.map((slice) => <Cell key={slice.country} fill={slice.color} />)}
          </Pie>
          <Tooltip
            formatter={(value) => typeof value === "number"
              ? formatMinorUnits(value, USD_CURRENCY) : String(value)}
          />
        </PieChart>
      )}
      {slices.map((slice) => (
        <div
          key={slice.country}
          role="img"
          aria-label={`${slice.country}: ${slice.amount}`}
          style={{ display: "flex", alignItems: "center", gap: 8 }}
        >
          <span
            aria-hidden="true"
            style={{ width: 12, height: 12, flexShrink: 0, background: slice.color, borderRadius: 2 }}
          />
          <Typography.Text>{slice.country}</Typography.Text>
          <Typography.Text strong style={{ marginLeft: "auto" }}>{slice.amount}</Typography.Text>
        </div>
      ))}
    </Space>
  );
}
