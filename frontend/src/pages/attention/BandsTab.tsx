import { Skeleton, Space } from "antd";

import type { BandsQuery } from "../../api/types";
import AttentionFilters from "../../components/AttentionFilters";
import BandsTable from "../../components/BandsTable";
import BandSummaryCards from "../../components/BandSummaryCards";
import ErrorBanner from "../../components/ErrorBanner";
import { DEFAULT_PAGE_SIZE, FIRST_PAGE } from "../../constants/attention";
import { useAttentionTableState } from "../../hooks/useAttentionTableState";
import { useBandsQuery } from "../../hooks/useBandsQuery";

const INITIAL_QUERY: BandsQuery = { page: FIRST_PAGE, page_size: DEFAULT_PAGE_SIZE };

export default function BandsTab() {
  const { query, updateFilters, changePage } = useAttentionTableState(INITIAL_QUERY);
  const bands = useBandsQuery(query);

  return (
    <Space direction="vertical" size="large" style={{ width: "100%" }}>
      {bands.data ? (
        <BandSummaryCards
          summary={bands.data.summary}
          status={query.status}
          onStatusChange={(status) => updateFilters({ status })}
        />
      ) : bands.isPending ? <Skeleton active /> : null}
      <AttentionFilters filters={query} onChange={updateFilters} showDepartment />
      {bands.isError && (
        <ErrorBanner
          title="Unable to load band compliance"
          message={bands.error.message}
          retrying={bands.isFetching}
          onRetry={() => void bands.refetch()}
        />
      )}
      <BandsTable
        items={bands.data?.items ?? []}
        total={bands.data?.total ?? 0}
        query={query}
        loading={bands.isFetching}
        isPlaceholderData={bands.isPlaceholderData}
        onPageChange={changePage}
      />
    </Space>
  );
}
