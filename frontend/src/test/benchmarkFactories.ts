import type { PeerGroupBenchmark } from "../api/types";

export function makeBenchmark(
  overrides: Partial<PeerGroupBenchmark> = {},
): PeerGroupBenchmark {
  return {
    key: { title: "Software Engineer", level: 3, country: "US" },
    currency: "USD",
    headcount: 5,
    stats: { min: 100_000, p25: 125_000, median: 150_000, p75: 175_000, max: 200_000 },
    insufficient_data: false,
    ...overrides,
  };
}
