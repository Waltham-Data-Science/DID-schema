// After `npm run build`: did the V_eta shape panel's bundle really read the
// schema tree it was built from?
//
// The panel imports schemas/V_eta/**/*.json with `import.meta.glob` and two
// schemas/*.md files with `?raw` (src/veta/sources.ts). That makes the bundle
// fresh BY CONSTRUCTION -- but "by construction" is a claim about a build tool's
// behaviour, and a glob that resolved to nothing (a moved directory, a typo in
// the pattern) produces a bundle that builds, deploys and renders an empty
// panel. So this checks the output, not the intent:
//
//   * every JSON file under schemas/V_eta/ on disk appears as a glob key in the
//     bundle, and the bundle carries no key for a file that is not on disk;
//   * every class file's class_name reaches the bundle;
//   * every non-blank line of the two markdown inputs reaches the bundle.
//
// The pre-build half (the inputs agree with each other) is
// tools/check_veta_viewer.py. RULE 5: the denominator prints first, and a
// bundle with no V_eta keys at all is a failure, not a clean zero.
//
// Usage (from web/):  node scripts/check-veta-bundle.mjs [distDir]
import { readFile, readdir } from "node:fs/promises";
import { existsSync } from "node:fs";
import { resolve, dirname, relative, join, sep } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const webDir = resolve(here, "..");
const repoRoot = resolve(webDir, "..");
const dist = resolve(webDir, process.argv[2] ?? "dist");
const grammar = JSON.parse(await readFile(resolve(webDir, "src/veta/grammar.json"), "utf8"));
const KEY_PREFIX = "../../../";

async function walk(dir) {
  const out = [];
  for (const e of await readdir(dir, { withFileTypes: true })) {
    const p = join(dir, e.name);
    if (e.isDirectory()) out.push(...(await walk(p)));
    else out.push(p);
  }
  return out;
}

if (!existsSync(dist)) {
  console.log(`DENOMINATOR: 0 JS chunk(s) read -- ${dist} does not exist`);
  process.exit(1);
}
const chunks = (await walk(dist)).filter((p) => p.endsWith(".js"));
const bundle = (await Promise.all(chunks.map((p) => readFile(p, "utf8")))).join("\n");
// String literals in the bundle escape quotes, backticks, `$` and backslashes;
// undo that so a markdown line can be looked for verbatim.
const unescaped = bundle.replace(/\\(['"`$\\])/g, "$1");

const vetaDir = resolve(repoRoot, "schemas", "V_eta");
const onDisk = (await walk(vetaDir))
  .filter((p) => p.endsWith(".json"))
  .map((p) => relative(repoRoot, p).split(sep).join("/"))
  .sort();
const keyRe = /"\.\.\/\.\.\/\.\.\/(schemas\/V_eta\/[^"]+\.json)"/g;
const inBundle = [...new Set([...bundle.matchAll(keyRe)].map((m) => m[1]))].sort();

const failures = [];
const bundleSet = new Set(inBundle);
const diskSet = new Set(onDisk);
for (const f of onDisk) if (!bundleSet.has(f)) failures.push(`on disk, not in the bundle: ${f}`);
for (const f of inBundle) if (!diskSet.has(f)) failures.push(`in the bundle, not on disk: ${f}`);

let classNames = 0;
const tiers = new Set(grammar.schema_tree.class_tiers);
for (const f of onDisk) {
  if (!tiers.has(f.split("/")[2])) continue;
  const data = JSON.parse(await readFile(resolve(repoRoot, f), "utf8"));
  const name = data?.document_class?.class_name;
  if (typeof name !== "string") continue;
  classNames++;
  if (!bundle.includes(`"${name}"`) && !bundle.includes(`'${name}'`))
    failures.push(`class_name ${name} (${f}) does not reach the bundle`);
}

let mdLines = 0;
for (const rel of [grammar.final_class_set.path, grammar.tenets.path]) {
  const text = await readFile(resolve(repoRoot, rel), "utf8");
  for (const line of text.split(/\r?\n/)) {
    if (!line.trim()) continue;
    mdLines++;
    if (!unescaped.includes(line)) {
      failures.push(`${rel}: line not in the bundle: ${line.slice(0, 80)}`);
    }
  }
}

console.log(
  `DENOMINATOR: ${chunks.length} JS chunk(s) read; ${onDisk.length} V_eta JSON file(s) on disk, ` +
    `${inBundle.length} in the bundle; ${classNames} class name(s) and ${mdLines} markdown line(s) looked for`,
);
if (inBundle.length === 0) failures.push("the bundle carries no V_eta glob key at all");
if (failures.length) {
  console.log(`FAIL: ${failures.length} way(s) the bundle differs from the schema tree:`);
  for (const f of failures.slice(0, 50)) console.log(`  - ${f}`);
  if (failures.length > 50) console.log(`  ... and ${failures.length - 50} more`);
  process.exit(1);
}
console.log("OK: the V_eta shape bundle reflects the schema tree it was built from");
