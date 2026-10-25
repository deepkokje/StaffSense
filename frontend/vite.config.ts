import react from "@vitejs/plugin-react";
import { defineConfig } from "vitest/config";

export default defineConfig({
  plugins: [react()],
  test: {
    environment: "jsdom",
    setupFiles: ["./src/test/setup.ts"],
    // Ant Design/jsdom integration tests contend heavily for CPU when run in parallel.
    maxWorkers: 1,
  },
});
