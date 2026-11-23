// Owner: Member D (WBS 5.1.1)
/// <reference types="vitest" />
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { fileURLToPath, URL } from "node:url";

const apiTarget = process.env.API_URL ?? "http://localhost:8000";

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@contracts": fileURLToPath(new URL("../contracts", import.meta.url)),
      "@fixtures": fileURLToPath(new URL("../tests/fixtures", import.meta.url)),
    },
  },
  server: { port: 5173, proxy: { "/api": apiTarget }, fs: { allow: [".."] } },
  preview: { port: 8080, proxy: { "/api": apiTarget } },
  test: { environment: "jsdom", include: ["src/**/*.test.{ts,tsx}"] },
});
