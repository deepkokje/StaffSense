import type { QueryClient } from "@tanstack/react-query";

import { queryKeys } from "./queryKeys";

export async function invalidateEmployeeData(client: QueryClient): Promise<void> {
  await Promise.all(
    Object.values(queryKeys).map((queryKey) => client.invalidateQueries({ queryKey })),
  );
}
