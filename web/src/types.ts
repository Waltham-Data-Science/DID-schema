export type Tier = "stable" | "draft" | "deprecated";
export type Maturity = "stable" | "draft" | "deprecated" | null;

export interface IndexEntry {
  class_name: string;
  tier: Tier;
  class_version: string | null;
  maturity_level: Maturity;
  superclasses: string[];
  path: string;
  is_meta?: boolean;
}

export interface SchemaIndex {
  set_version: string;
  schema_version_value: string;
  based_on?: string;
  tiers: Tier[];
  notes?: string;
  schemas: IndexEntry[];
}

// Manifest of the schema sets available to the viewer, written by
// scripts/sync-schemas.mjs. `default` is the set shown on first load.
export interface VersionsManifest {
  versions: string[];
  default: string;
}

// Topic tree (purely a viewer affordance). Lives in
// schemas/V_delta/topics.json. Interior nodes have a `name`; leaves are
// referenced by class_name in `classes`. Children may be omitted.
export interface TopicCategory {
  name: string;
  description?: string;
  classes?: string[];
  children?: TopicCategory[];
}

export interface TopicsFile {
  set_version: string;
  notes?: string;
  // Top-level bare leaf classes (rendered without a folder at the root of
  // the topic tree). Example: `base`.
  classes?: string[];
  topics: TopicCategory[];
}

export interface FieldDef {
  name: string;
  type: string;
  blank_value?: unknown;
  default_value?: unknown;
  mustBeNonEmpty?: boolean;
  mustBeScalar?: boolean;
  mustNotHaveNaN?: boolean;
  queryable?: boolean;
  ontology?: { node?: string; name?: string } | null;
  documentation?: string;
  constraints?: Record<string, unknown> | null;
  fields?: FieldDef[];
}

export interface DependsOnEntry {
  name: string;
  mustBeNonEmpty?: boolean;
  documentation?: string;
}

export interface FileEntry {
  name: string;
  documentation?: string;
}

export interface SchemaDocument {
  document_class?: {
    class_name: string;
    class_version?: string;
    superclasses?: SuperclassRef[];
    maturity_level?: Maturity;
  };
  depends_on?: DependsOnEntry[];
  file?: FileEntry[];
  fields?: FieldDef[];
  // Meta-schemas and registries may have arbitrary other shapes; keep open.
  [key: string]: unknown;
}

// The binding registry meta-file (schemas/V_*/stable/binding_registry_meta.json).
// Maps a statement's `variable` to the admissible value_set for its term value,
// and declares the kind-defining variables whose presence marks a subject's kind
// (D9). Only present from V_eta on; absent sets simply have no registry to browse.
export interface KindVariable {
  variable: string;
  value_set: string;
  root?: string;
  source?: string;
}

// A corpus-derived variable->value_set binding. The shape is intentionally open:
// bindings are added during discovery (D3/D6) and may carry method/context keys
// beyond the core three, so the browser renders whatever columns are present.
export interface Binding {
  variable?: string;
  value_set?: string;
  method?: string;
  [k: string]: unknown;
}

export interface BindingRegistryMeta {
  title?: string;
  description?: string;
  kind_variables?: KindVariable[];
  bindings?: Binding[];
  notes?: string;
  [k: string]: unknown;
}

// Inside a schema file, `superclasses` is an array of objects with at least
// a `class_name` key. The repo-level index.json normalizes these to plain
// strings, so callers may see either shape -- always pass through
// `superclassName()` to extract the string.
export type SuperclassRef = string | { class_name: string; [k: string]: unknown };

export function superclassName(ref: SuperclassRef): string {
  return typeof ref === "string" ? ref : ref.class_name;
}
