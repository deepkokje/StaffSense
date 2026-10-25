import { QueryClient } from "@tanstack/react-query";
import { expect, test, vi } from "vitest";

import { invalidateEmployeeData } from "./invalidateEmployeeData";
import { queryKeys } from "./queryKeys";

test("invalidates employees and every insight, dashboard and salary history key", async () => {
  const client = new QueryClient();
  const invalidate = vi.spyOn(client, "invalidateQueries").mockResolvedValue();
  await invalidateEmployeeData(client);
  for (const key of Object.values(queryKeys)) {
    expect(invalidate).toHaveBeenCalledWith({ queryKey: key });
  }
});
