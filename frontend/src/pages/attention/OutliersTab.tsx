import { Segmented, Space } from "antd";

import type { OutlierDirection, OutliersQuery } from "../../api/types";
import AttentionFilters from "../../components/AttentionFilters";
import ErrorBanner from "../../components/ErrorBanner";
import OutliersTable from "../../components/OutliersTable";
import { DEFAULT_PAGE_SIZE, FIRST_PAGE } from "../../constants/attention";
import { useAttentionTableState } from "../../hooks/useAttentionTableState";
import { useOutliersQuery } from "../../hooks/useOutliersQuery";

const INITIAL_QUERY: OutliersQuery = { page: FIRST_PAGE, page_size: DEFAULT_PAGE_SIZE };
const ALL_DIRECTIONS = "all";
const DIRECTION_OPTIONS: { label: string; value: OutlierDirection | typeof ALL_DIRECTIONS }[] = [
  { label: "All", value: ALL_DIRECTIONS },
  { label: "Above", value: "above" },
  { label: "Below", value: "below" },
];

export default function OutliersTab() {
  const { query, updateFilters, changePage } = useAttentionTableState(INITIAL_QUERY);
  const outliers = useOutliersQuery(query);

  return (
    <Space direction="vertical" size="large" style={{ width: "100%" }}>
      <Segmented<OutlierDirection | typeof ALL_DIRECTIONS>
        aria-label="Outlier direction"
        options={DIRECTION_OPTIONS}
        value={query.direction ?? ALL_DIRECTIONS}
        onChange={(direction) => updateFilters({
          direction: direction === ALL_DIRECTIONS ? undefined : direction,
        })}
      />
      <AttentionFilters filters={query} onChange={updateFilters} />
      {outliers.isError && (
        <ErrorBanner
          title="Unable to load outliers"
          message={outliers.error.message}
          retrying={outliers.isFetching}
          onRetry={() => void outliers.refetch()}
        />
      )}
      <OutliersTable
        items={outliers.data?.items ?? []}
        total={outliers.data?.total ?? 0}
        query={query}
        loading={outliers.isFetching}
        isPlaceholderData={outliers.isPlaceholderData}
        onPageChange={changePage}
      />
    </Space>
  );
}
