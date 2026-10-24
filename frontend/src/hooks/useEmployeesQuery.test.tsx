import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { renderHook, waitFor } from "@testing-library/react";
import type { PropsWithChildren } from "react";
import { beforeEach, describe, expect, test, vi } from "vitest";

import { fetchEmployees } from "../api/employees";
import type { EmployeeQuery } from "../api/types";
import { makeEmployeePage } from "../test/factories";
import { useEmployeesQuery } from "./useEmployeesQuery";

vi.mock("../api/employees", () => ({
  fetchEmployees: vi.fn(),
}));

const mockedFetchEmployees = vi.mocked(fetchEmployees);
const INITIAL_QUERY: EmployeeQuery = {
  page: 1,
  page_size: 25,
  sort_by: "name",
  sort_dir: "asc",
};

function createWrapper() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return function Wrapper({ children }: PropsWithChildren) {
    return (
      <QueryClientProviderForTest client={queryClient}>
        {children}
      </QueryClientProviderForTest>
    );
  };
}

function QueryClientProviderForTest({
  client,
  children,
}: PropsWithChildren<{ client: QueryClient }>) {
  return (
    <QueryClientProvider client={client}>
      {children}
    </QueryClientProvider>
  );
}

describe("useEmployeesQuery", () => {
  beforeEach(() => {
    mockedFetchEmployees.mockReset();
  });

  test("requests the initial query", async () => {
    mockedFetchEmployees.mockResolvedValue(makeEmployeePage());
    const { result } = renderHook(() => useEmployeesQuery(INITIAL_QUERY), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(mockedFetchEmployees).toHaveBeenCalledWith(INITIAL_QUERY, expect.any(AbortSignal));
  });

  test("fetches again when query parameters change", async () => {
    mockedFetchEmployees.mockResolvedValue(makeEmployeePage());
    const { rerender } = renderHook(
      ({ query }: { query: EmployeeQuery }) => useEmployeesQuery(query),
      { initialProps: { query: INITIAL_QUERY }, wrapper: createWrapper() },
    );
    await waitFor(() => expect(mockedFetchEmployees).toHaveBeenCalledTimes(1));

    rerender({ query: { ...INITIAL_QUERY, page: 2 } });
    await waitFor(() => expect(mockedFetchEmployees).toHaveBeenCalledTimes(2));
  });

  test("exposes query errors", async () => {
    mockedFetchEmployees.mockRejectedValue(new Error("Network unavailable"));
    const { result } = renderHook(() => useEmployeesQuery(INITIAL_QUERY), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isError).toBe(true));
    expect(result.current.error).toHaveProperty("message", "Network unavailable");
  });

  test("keeps the last successful page available after a later request fails", async () => {
    const firstPage = makeEmployeePage();
    mockedFetchEmployees
      .mockResolvedValueOnce(firstPage)
      .mockRejectedValueOnce(new Error("Network unavailable"));
    const { result, rerender } = renderHook(
      ({ query }: { query: EmployeeQuery }) => useEmployeesQuery(query),
      { initialProps: { query: INITIAL_QUERY }, wrapper: createWrapper() },
    );
    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    rerender({ query: { ...INITIAL_QUERY, q: "Ada" } });
    await waitFor(() => expect(result.current.isError).toBe(true));

    expect(result.current.displayData).toBe(firstPage);
  });
});
