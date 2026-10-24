import { act, renderHook } from "@testing-library/react";
import { describe, expect, test } from "vitest";

import { useEmployeeTableState } from "./useEmployeeTableState";

describe("useEmployeeTableState", () => {
  test("resets page when search changes", () => {
    const { result } = renderHook(() => useEmployeeTableState());
    act(() => result.current.setPage(4));
    act(() => result.current.setSearch("Ada"));

    expect(result.current.page).toBe(1);
  });

  test("resets page when a filter changes", () => {
    const { result } = renderHook(() => useEmployeeTableState());
    act(() => result.current.setPage(4));
    act(() => result.current.setFilters({ ...result.current.filters, country: ["IN"] }));

    expect(result.current.page).toBe(1);
  });

  test("resets page when sorting changes", () => {
    const { result } = renderHook(() => useEmployeeTableState());
    act(() => result.current.setPage(4));
    act(() => result.current.setSort("salary_usd_minor", "desc"));

    expect(result.current.page).toBe(1);
  });

  test("clears filters and restores initial controls", () => {
    const { result } = renderHook(() => useEmployeeTableState());
    act(() => {
      result.current.setSearch("Ada");
      result.current.setFilters({
        ...result.current.filters,
        country: ["IN"],
        gender: "FEMALE",
      });
      result.current.setPage(3);
      result.current.clearFilters();
    });

    expect(result.current.page).toBe(1);
    expect(result.current.pageSize).toBe(25);
    expect(result.current.search).toBe("");
    expect(result.current.filters.country).toEqual([]);
    expect(result.current.filters.gender).toBeUndefined();
    expect(result.current.sortBy).toBe("name");
    expect(result.current.sortDir).toBe("asc");
  });
});
