// Owner: Member D (WBS 6.3.1)
import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: ".",
  timeout: 120_000,
  use: { baseURL: process.env.BASE_URL ?? "http://localhost:8080", trace: "retain-on-failure" },
});
