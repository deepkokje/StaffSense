import { QueryClient } from "@tanstack/react-query";

const QUERY_STALE_TIME_MILLISECONDS = 30_000;
const QUERY_RETRY_COUNT = 1;

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: QUERY_STALE_TIME_MILLISECONDS,
      retry: QUERY_RETRY_COUNT,
      refetchOnWindowFocus: false,
    },
  },
});
