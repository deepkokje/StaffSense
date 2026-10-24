import { Col, Row, Typography } from "antd";

import HeadlineCard from "../components/dashboard/HeadlineCard";
import BandGraph from "../components/dashboard/BandGraph";
import BarGraph from "../components/dashboard/BarGraph";
import CostPieChart from "../components/dashboard/CostPieChart";
import { useDashboardData } from "../hooks/useDashboardData";

const GRID_GUTTER = 24;
const BANDS_PATH = "/insights/attention?tab=bands";
const OUTLIERS_PATH = "/insights/attention?tab=outliers";
const WHAT_IF_PATH = "/insights/what-if";

export default function DashboardPage() {
  const { belowBand, aboveBand, outliers, bandMinimum } = useDashboardData();

  return (
    <>
      <Typography.Title level={1}>How we pay people</Typography.Title>
      <Row gutter={[GRID_GUTTER, GRID_GUTTER]}>
        <Col xs={24} sm={12} xl={8}>
          <HeadlineCard
            title="Below band"
            value={belowBand.data && <BandGraph summary={belowBand.data.summary} highlight="below_min" />}
            caption="paid under their band minimum"
            linkPath={BANDS_PATH}
            loading={belowBand.isLoading}
            error={belowBand.isError ? belowBand.error?.message ?? "Unable to load band summary." : undefined}
            emptyMessage={belowBand.data?.summary.below_min === 0 ? "Nobody is below band minimum" : undefined}
            onRetry={() => void belowBand.refetch()}
          />
        </Col>
        <Col xs={24} sm={12} xl={8}>
          <HeadlineCard
            title="Above band"
            value={aboveBand.data && <BandGraph summary={aboveBand.data.summary} highlight="above_max" />}
            caption="paid over their band maximum"
            linkPath={BANDS_PATH}
            loading={aboveBand.isLoading}
            error={aboveBand.isError ? aboveBand.error?.message ?? "Unable to load band summary." : undefined}
            emptyMessage={aboveBand.data?.summary.above_max === 0 ? "Nobody is above band maximum" : undefined}
            onRetry={() => void aboveBand.refetch()}
          />
        </Col>
        <Col xs={24} sm={12} xl={8}>
          <HeadlineCard
            title="Outliers"
            value={outliers.data && (
              <BarGraph
                label="Outlier count"
                items={[{
                  label: "Flagged employees",
                  value: outliers.data.total,
                  displayValue: String(outliers.data.total),
                  color: "#722ed1",
                }]}
              />
            )}
            caption="more than 20% from their peer-group median"
            linkPath={OUTLIERS_PATH}
            loading={outliers.isLoading}
            error={outliers.isError ? outliers.error?.message ?? "Unable to load outliers." : undefined}
            emptyMessage={outliers.data?.total === 0 ? "No outliers" : undefined}
            onRetry={() => void outliers.refetch()}
          />
        </Col>
        <Col xs={24} sm={12} xl={8}>
          <HeadlineCard
            title="Cost to reach band minimum"
            value={bandMinimum.data && (
              <CostPieChart report={bandMinimum.data} />
            )}
            caption={bandMinimum.data && `${bandMinimum.data.employees_affected} employees affected, per year`}
            linkPath={WHAT_IF_PATH}
            loading={bandMinimum.isLoading}
            error={bandMinimum.isError ? bandMinimum.error?.message ?? "Unable to load band minimum cost." : undefined}
            emptyMessage={bandMinimum.data?.total_cost_usd_minor === 0 ? "Everyone is within band" : undefined}
            onRetry={() => void bandMinimum.refetch()}
          />
        </Col>
      </Row>
    </>
  );
}
