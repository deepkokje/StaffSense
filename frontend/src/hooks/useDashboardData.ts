import { useBandsQuery } from "./useBandsQuery";
import { useBringToBandMinQuery } from "./useBringToBandMinQuery";
import { useOutliersQuery } from "./useOutliersQuery";

const SUMMARY_PAGE = 1;
const SUMMARY_PAGE_SIZE = 1;
const SUMMARY_QUERY = { page: SUMMARY_PAGE, page_size: SUMMARY_PAGE_SIZE };
const NO_FILTERS = {};

function cardState<T>(query: {
  data: T | undefined;
  isLoading: boolean;
  isError: boolean;
  error: Error | null;
  refetch: () => unknown;
}) {
  return {
    data: query.data,
    isLoading: query.isLoading,
    isError: query.isError,
    error: query.error,
    refetch: query.refetch,
  };
}

export function useDashboardData() {
  const bands = useBandsQuery(SUMMARY_QUERY);
  const outliers = useOutliersQuery(SUMMARY_QUERY);
  const bandMinimum = useBringToBandMinQuery(NO_FILTERS);

  return {
    belowBand: cardState(bands),
    aboveBand: cardState(bands),
    outliers: cardState(outliers),
    bandMinimum: cardState(bandMinimum),
  };
}
