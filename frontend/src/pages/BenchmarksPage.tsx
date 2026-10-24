import { Space, Typography } from "antd";

import BenchmarkFilters from "../components/BenchmarkFilters";
import BenchmarkTable from "../components/BenchmarkTable";
import ErrorBanner from "../components/ErrorBanner";
import { useBenchmarkFilters } from "../hooks/useBenchmarkFilters";
import { useBenchmarksQuery } from "../hooks/useBenchmarksQuery";

export default function BenchmarksPage() {
  const { query, page, pageSize, updateFilters, changePage } = useBenchmarkFilters();
  const benchmarks = useBenchmarksQuery(query);

  return (
    <Space direction="vertical" size="large" style={{ width: "100%" }}>
      <Typography.Title level={1}>Benchmarks</Typography.Title>
      <BenchmarkFilters query={query} onChange={updateFilters} />
      {benchmarks.isError && (
        <ErrorBanner
          title="Unable to load benchmarks"
          message={benchmarks.error.message}
          retrying={benchmarks.isFetching}
          onRetry={() => void benchmarks.refetch()}
        />
      )}
      <BenchmarkTable
        items={benchmarks.data?.items ?? []}
        loading={benchmarks.isFetching}
        isPlaceholderData={benchmarks.isPlaceholderData}
        page={page}
        pageSize={pageSize}
        onPageChange={changePage}
      />
    </Space>
  );
}
