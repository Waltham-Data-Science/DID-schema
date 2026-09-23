// Turns the raw build-time inputs (sources.ts) into the model the V_eta viewer
// renders. Pure functions only: nothing here fetches, and nothing here knows
// the name of any V_eta class.
//
// RULE 5 APPLIES TO THE VIEWER TOO. `buildModel` counts what it read before it
// counts what it placed, and it NAMES every class it could not place and every
// category entry naming a class the tree does not have. A viewer that silently
// dropped an unplaced class would look exactly like a viewer whose inputs
// agree, which is the defect this repository keeps paying for.

import grammar from "./grammar.json";

// ---- raw schema shapes (only the parts the viewer reads) ------------------

export interface RawField {
  name: string;
  type: string;
  mustBeNonEmpty?: boolean;
  mustBeScalar?: boolean;
  mustNotHaveNaN?: boolean;
  queryable?: boolean;
  documentation?: string;
  constraints?: Record<string, unknown>;
  ontology?: unknown;
  fields?: RawField[];
  default_value?: unknown;
  needs_ndi?: unknown;
}

export interface RawDependency {
  name: string;
  mustBeNonEmpty?: boolean;
  documentation?: string;
  must_refer_to_document_class?: string | string[];
  multiple?: boolean;
  min_count?: number;
  max_count?: number;
  [k: string]: unknown;
}

interface RawClassFile {
  document_class: {
    class_name: string;
    class_version?: string | null;
    superclasses?: Array<string | { class_name: string }>;
    maturity_level?: string | null;
    abstract?: boolean;
  };
  depends_on?: RawDependency[];
  file?: unknown[];
  fields?: RawField[];
}

interface RawIndexEntry {
  class_name: string;
  path: string;
  disposition?: string | null;
  is_meta?: boolean;
}

// ---- the model ------------------------------------------------------------

export interface VetaClass {
  name: string;
  path: string; // repository-relative, e.g. schemas/V_eta/stable/strain.json
  tier: string; // stable | draft | deprecated
  version: string | null;
  maturity: string | null;
  abstract: boolean;
  disposition: string | null; // from index.json
  superclasses: string[];
  subclasses: string[];
  fields: RawField[];
  dependsOn: RawDependency[];
  files: unknown[];
  category: string | null; // symbol of the final-set category, if in the persist set
  excludedAs: string | null; // disposition bucket from "NOT in the final set"
}

export interface Category {
  symbol: string;
  title: string;
  declaredCount: number;
  classes: string[];
}

export interface ExcludedGroup {
  disposition: string;
  declaredCount: number;
  classes: string[];
}

export interface Tenet {
  id: string;
  title: string;
  body: string;
}

export interface TenetSection {
  title: string;
  body: string;
}

export interface VetaDenominator {
  jsonFilesMatched: number;
  classFiles: number;
  classesByTier: Record<string, number>;
  nonClassFiles: string[];
  categorised: number;
  excluded: number;
  // Found in the tree, placed in no category and no excluded bucket.
  unplaced: string[];
  // Named by the final-set document, absent from the tree.
  namedButNotBuilt: string[];
  // A category or bucket whose "(n)" disagrees with the names listed under it.
  countMismatches: string[];
  // Named in more than one place in the final-set document.
  placedTwice: string[];
  missingCategories: string[];
  tenetsParsed: number;
  missingTenets: string[];
  indexEntries: number;
  indexMissing: string[];
}

export interface VetaModel {
  classes: Map<string, VetaClass>;
  categories: Category[];
  excluded: ExcludedGroup[];
  tenets: Tenet[];
  tenetSections: TenetSection[]; // the non-tenet `##` sections (thesis, meta-principle, ...)
  tenetsTitle: string;
  tenetsPreamble: string;
  denominator: VetaDenominator;
}

// ---- parsers --------------------------------------------------------------

const G = grammar;

function tokens(line: string): string[] {
  const re = new RegExp(G.final_class_set.class_token, "g");
  const out: string[] = [];
  for (const m of line.matchAll(re)) out.push(m[1]);
  return out;
}

export function parseFinalClassSet(md: string): {
  categories: Category[];
  excluded: ExcludedGroup[];
} {
  const catRe = new RegExp(G.final_class_set.category_heading);
  const exclRe = new RegExp(G.final_class_set.excluded_section_heading);
  const dispRe = new RegExp(G.final_class_set.disposition_heading);
  const anyHeading = new RegExp(G.final_class_set.any_heading);

  const categories: Category[] = [];
  const excluded: ExcludedGroup[] = [];
  let inExcluded = false;
  let cur: { classes: string[] } | null = null;

  for (const line of md.split(/\r?\n/)) {
    const c = catRe.exec(line);
    if (c) {
      const cat: Category = {
        symbol: c[1],
        title: c[2],
        declaredCount: Number(c[3]),
        classes: [],
      };
      categories.push(cat);
      cur = cat;
      inExcluded = false;
      continue;
    }
    if (exclRe.test(line)) {
      inExcluded = true;
      cur = null;
      continue;
    }
    if (anyHeading.test(line)) {
      cur = null;
      inExcluded = false;
      continue;
    }
    const d = inExcluded ? dispRe.exec(line) : null;
    if (d) {
      const grp: ExcludedGroup = {
        disposition: d[1],
        declaredCount: Number(d[2]),
        classes: [],
      };
      excluded.push(grp);
      cur = grp;
      continue;
    }
    if (cur) cur.classes.push(...tokens(line));
  }
  return { categories, excluded };
}

export function parseTenets(md: string): {
  title: string;
  preamble: string;
  tenets: Tenet[];
  sections: TenetSection[];
} {
  const tenetRe = new RegExp(G.tenets.tenet_heading);
  const sectionRe = new RegExp(G.tenets.section_heading);
  let title = "";
  const preamble: string[] = [];
  const tenets: Array<Tenet & { lines: string[] }> = [];
  const sections: Array<TenetSection & { lines: string[] }> = [];
  let cur: string[] = preamble;

  for (const line of md.split(/\r?\n/)) {
    const t = tenetRe.exec(line);
    if (t) {
      const x = { id: t[1], title: t[2], body: "", lines: [] as string[] };
      tenets.push(x);
      cur = x.lines;
      continue;
    }
    const s = sectionRe.exec(line);
    if (s) {
      const x = { title: s[1], body: "", lines: [] as string[] };
      sections.push(x);
      cur = x.lines;
      continue;
    }
    if (!title && /^# /.test(line)) {
      title = line.slice(2).trim();
      continue;
    }
    cur.push(line);
  }
  // A trailing `---` rule separates sections in the source; it is layout, not
  // content.
  const finish = (lines: string[]) =>
    lines.join("\n").trim().replace(/\n?-{3,}$/, "").trim();
  return {
    title,
    preamble: finish(preamble),
    tenets: tenets.map(({ id, title, lines }) => ({ id, title, body: finish(lines) })),
    // "## The tenets" only introduces T1-T14 and has no body worth a card.
    sections: sections
      .map(({ title, lines }) => ({ title, body: finish(lines) }))
      .filter((x) => x.body.length > 0),
  };
}

// ---- the model ------------------------------------------------------------

function isClassFile(v: unknown): v is RawClassFile {
  return (
    typeof v === "object" &&
    v !== null &&
    "document_class" in v &&
    "fields" in v &&
    typeof (v as RawClassFile).document_class?.class_name === "string"
  );
}

export function buildModel(
  files: Record<string, unknown>,
  keyPrefix: string,
  finalClassSetMd: string,
  tenetsMd: string,
): VetaModel {
  const tiers = new Set(G.schema_tree.class_tiers);
  const classes = new Map<string, VetaClass>();
  const classesByTier: Record<string, number> = {};
  const nonClassFiles: string[] = [];
  let index: RawIndexEntry[] = [];
  const indexPath = G.schema_tree.index;

  const keys = Object.keys(files).sort();
  for (const key of keys) {
    const path = key.startsWith(keyPrefix) ? key.slice(keyPrefix.length) : key;
    const data = files[key];
    if (path === indexPath) {
      index = ((data as { schemas?: RawIndexEntry[] }).schemas ?? []) as RawIndexEntry[];
      nonClassFiles.push(path);
      continue;
    }
    // schemas/V_eta/<tier>/<file>.json -- examples/ holds document INSTANCES
    // that carry a document_class too, so the tier is what decides.
    const tier = path.split("/")[2];
    if (!tiers.has(tier) || !isClassFile(data)) {
      nonClassFiles.push(path);
      continue;
    }
    const dc = data.document_class;
    classesByTier[tier] = (classesByTier[tier] ?? 0) + 1;
    classes.set(dc.class_name, {
      name: dc.class_name,
      path,
      tier,
      version: dc.class_version ?? null,
      maturity: dc.maturity_level ?? null,
      abstract: dc.abstract === true,
      disposition: null,
      superclasses: (dc.superclasses ?? []).map((s) =>
        typeof s === "string" ? s : s.class_name,
      ),
      subclasses: [],
      fields: data.fields ?? [],
      dependsOn: data.depends_on ?? [],
      files: data.file ?? [],
      category: null,
      excludedAs: null,
    });
  }

  const indexMissing: string[] = [];
  const byName = new Map(index.map((e) => [e.class_name, e]));
  for (const c of classes.values()) {
    const e = byName.get(c.name);
    if (e) c.disposition = e.disposition ?? null;
    else indexMissing.push(c.name);
    for (const s of c.superclasses) classes.get(s)?.subclasses.push(c.name);
  }
  for (const c of classes.values()) c.subclasses.sort();

  const { categories, excluded } = parseFinalClassSet(finalClassSetMd);
  const namedButNotBuilt: string[] = [];
  const countMismatches: string[] = [];
  const placedTwice: string[] = [];
  const seen = new Set<string>();
  const place = (name: string, apply: (c: VetaClass) => void) => {
    if (seen.has(name)) placedTwice.push(name);
    seen.add(name);
    const c = classes.get(name);
    if (c) apply(c);
    else namedButNotBuilt.push(name);
  };
  let categorised = 0;
  for (const cat of categories) {
    if (cat.classes.length !== cat.declaredCount)
      countMismatches.push(
        `${cat.symbol} ${cat.title}: heading says ${cat.declaredCount}, lists ${cat.classes.length}`,
      );
    for (const n of cat.classes)
      place(n, (c) => {
        c.category = cat.symbol;
        categorised++;
      });
  }
  let excludedN = 0;
  for (const grp of excluded) {
    if (grp.classes.length !== grp.declaredCount)
      countMismatches.push(
        `${grp.disposition}: heading says ${grp.declaredCount}, lists ${grp.classes.length}`,
      );
    for (const n of grp.classes)
      place(n, (c) => {
        c.excludedAs = grp.disposition;
        excludedN++;
      });
  }
  const unplaced = [...classes.values()]
    .filter((c) => !c.category && !c.excludedAs && !byName.get(c.name)?.is_meta)
    .map((c) => c.name)
    .sort();
  const present = new Set(categories.map((c) => c.symbol));
  const missingCategories = G.final_class_set.expected_categories.filter(
    (s) => !present.has(s),
  );

  const t = parseTenets(tenetsMd);
  const parsedIds = new Set(t.tenets.map((x) => x.id));
  const missingTenets = G.tenets.expected_tenets.filter((id) => !parsedIds.has(id));

  return {
    classes,
    categories,
    excluded,
    tenets: t.tenets,
    tenetSections: t.sections,
    tenetsTitle: t.title,
    tenetsPreamble: t.preamble,
    denominator: {
      jsonFilesMatched: keys.length,
      classFiles: classes.size,
      classesByTier,
      nonClassFiles,
      categorised,
      excluded: excludedN,
      unplaced,
      namedButNotBuilt,
      countMismatches,
      placedTwice,
      missingCategories,
      tenetsParsed: t.tenets.length,
      missingTenets,
      indexEntries: index.length,
      indexMissing,
    },
  };
}

// The full superclass chain of a class, nearest first, each ancestor once.
export function ancestors(model: VetaModel, name: string): string[] {
  const out: string[] = [];
  const seen = new Set<string>([name]);
  const queue = [...(model.classes.get(name)?.superclasses ?? [])];
  while (queue.length) {
    const n = queue.shift()!;
    if (seen.has(n)) continue;
    seen.add(n);
    out.push(n);
    queue.push(...(model.classes.get(n)?.superclasses ?? []));
  }
  return out;
}

export function refTargets(d: RawDependency): string[] {
  const t = d.must_refer_to_document_class;
  if (!t) return [];
  return Array.isArray(t) ? t : [t];
}
