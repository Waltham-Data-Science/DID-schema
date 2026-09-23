import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { fileURLToPath } from "node:url";

// The repository root. The V_eta shape panel imports schemas/V_eta/**/*.json
// and two schemas/*.md files directly (web/src/veta/sources.ts), which sit
// outside web/, so the dev server must be allowed to serve them.
const repoRoot = fileURLToPath(new URL("..", import.meta.url));

// Base path matches the GitHub Pages URL for this repo:
//   https://waltham-data-science.github.io/DID-schema/
// Override with VITE_BASE_PATH if deploying elsewhere.
const base = process.env.VITE_BASE_PATH ?? "/DID-schema/";

export default defineConfig({
  base,
  plugins: [react()],
  server: {
    fs: {
      allow: [repoRoot],
    },
  },
  build: {
    outDir: "dist",
  },
});
