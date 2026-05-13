import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Base path matches the GitHub Pages URL for this repo:
//   https://waltham-data-science.github.io/DID-schema/
// Override with VITE_BASE_PATH if deploying elsewhere.
const base = process.env.VITE_BASE_PATH ?? "/DID-schema/";

export default defineConfig({
  base,
  plugins: [react()],
  build: {
    outDir: "dist",
  },
});
