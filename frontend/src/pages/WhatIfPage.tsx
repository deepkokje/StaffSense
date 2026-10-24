import { Alert, Card, Empty, Select, Skeleton, Space, Typography } from "antd";

import CountryCostTable from "../components/CountryCostTable";
import ErrorBanner from "../components/ErrorBanner";
import RaiseCostForm from "../components/RaiseCostForm";
import RaiseCostResult from "../components/RaiseCostResult";
import WhatIfCostSummary from "../components/WhatIfCostSummary";
import { COUNTRY_OPTIONS } from "../constants/filterOptions";
import { useBringToBandMinQuery } from "../hooks/useBringToBandMinQuery";
import { useRaiseCostQuery } from "../hooks/useRaiseCostQuery";
import { useWhatIfState } from "../hooks/useWhatIfState";

const COUNTRY_FILTER_WIDTH = 240;

export default function WhatIfPage() {
  const { bandQuery, raiseQuery, changeBandCountries, submitRaise } = useWhatIfState();
  const bandCost = useBringToBandMinQuery(bandQuery);
  const raiseCost = useRaiseCostQuery(raiseQuery, raiseQuery !== undefined);

  return (
    <Space direction="vertical" size="large" style={{ width: "100%" }}>
      <Typography.Title level={1}>What-if</Typography.Title>
      <Alert type="info" showIcon message="Read-only estimates: annual base salary only. No salaries are changed." />
      <Card title="Bring everyone to band minimum">
        <Space direction="vertical" size="large" style={{ width: "100%" }}>
          <Select<string[]>
            aria-label="Band minimum country"
            mode="multiple"
            virtual={false}
            allowClear
            placeholder="All countries"
            style={{ minWidth: COUNTRY_FILTER_WIDTH }}
            options={COUNTRY_OPTIONS.map((value) => ({ label: value, value }))}
            value={bandQuery.country ? [...bandQuery.country] : []}
            onChange={changeBandCountries}
          />
          {bandCost.isError && (
            <ErrorBanner
              title="Unable to calculate band minimum cost"
              message={bandCost.error.message}
              retrying={bandCost.isFetching}
              onRetry={() => void bandCost.refetch()}
            />
          )}
          {bandCost.isPending ? <Skeleton active /> : bandCost.data ? (
            <>
              <WhatIfCostSummary report={bandCost.data} label="Band minimum cost summary" />
              {bandCost.data.total_cost_usd_minor === 0 && (
                <Empty description="Everyone is within band" />
              )}
              {bandCost.data.by_country.length > 0 && (
                <CountryCostTable
                  items={bandCost.data.by_country}
                  loading={bandCost.isFetching}
                  isPlaceholderData={bandCost.isPlaceholderData}
                />
              )}
            </>
          ) : null}
        </Space>
      </Card>
      <Card title="Give a department a raise">
        <Space direction="vertical" size="large" style={{ width: "100%" }}>
          <RaiseCostForm onCalculate={submitRaise} loading={raiseCost.isFetching} />
          {raiseCost.isError && (
            <ErrorBanner
              title="Unable to calculate raise cost"
              message={raiseCost.error.message}
              retrying={raiseCost.isFetching}
              onRetry={() => void raiseCost.refetch()}
            />
          )}
          {raiseCost.isFetching && !raiseCost.data && <Skeleton active />}
          {raiseCost.data && (
            <RaiseCostResult
              report={raiseCost.data}
              loading={raiseCost.isFetching}
              isPlaceholderData={raiseCost.isPlaceholderData}
            />
          )}
        </Space>
      </Card>
    </Space>
  );
}
