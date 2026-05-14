// Copies schemas/V_delta into web/public/schemas/V_delta so they ship with
// the static bundle. Runs automatically before `npm run dev` and `npm run build`.
import { cp, rm, mkdir } from "node:fs/promises";
import { existsSync } from "node:fs";
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const repoRoot = resolve(here, "..", "..");
const src = resolve(repoRoot, "schemas", "V_delta");
const dst = resolve(here, "..", "public", "schemas", "V_delta");

if (!existsSync(src)) {
  console.error(`sync-schemas: source not found: ${src}`);
  process.exit(1);
}

await rm(dst, { recursive: true, force: true });
await mkdir(dirname(dst), { recursive: true });
await cp(src, dst, { recursive: true });
console.log(`sync-schemas: copied ${src} -> ${dst}`);
