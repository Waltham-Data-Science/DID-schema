export type Tier = "stable" | "draft" | "deprecated";
export type Maturity = "stable" | "draft" | "deprecated" | null;
// Migration disposition (written into index.json by build_v_eta.py):
//   persist     — settled go-forward class (in the final V1 set)
//   retire      — decided to dissolve/delete; not in final V1 (see disposition_note)
//   in_progress — persists but its ⑥/⑦ disposition is not yet finalized
export type Disposition = "persist" | "retire" | "in_progress";

export interface IndexEntry {
  class_name: string;
  tier: Tier;
  class_version: string | null;
  maturity_level: Maturity;
  superclasses: string[];
  path: string;
  is_meta?: boolean;
  disposition?: Disposition;
  disposition_note?: string;
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
// An ontology node reference: a CURIE plus a human-readable label snapshot.
export interface NodeRef {
  node: string;
  name: string;
}

// A kind-defining variable: a subtree value binding (variable -> ontology +
// root_node). No enumerated value_set — the admissible set is always the subtree.
export interface KindVariable {
  variable: NodeRef;
  ontology?: string;
  root_node?: string;
}

// A corpus-derived subject_statement binding. The shape is intentionally open:
// bindings are added during discovery (D3/D6), keyed on variable.node (+
// method.node) and naming the concrete subject_statement-leaf `class` that carries
// the statement. The leaf fixes the value type, so there is no data_type; a
// term-valued leaf additionally pins an admissible set (values | ontology+
// root_node). The browser renders whatever columns are present.
export interface Binding {
  variable?: NodeRef;
  method?: NodeRef;
  class?: string;
  values?: unknown[];
  ontology?: string;
  root_node?: string;
  [k: string]: unknown;
}

// A D6 relation-vocabulary term: the admissible value on directed_relation.relation
// / undirected_relation.relation, pinned to its carrier `class` and typed endpoints.
// `relation` is a {node, name} NodeRef, the same shape as a binding's variable/method.
export interface RelationTerm {
  relation: NodeRef;
  class: string; // "directed_relation" | "undirected_relation"
  child_role?: string;
  parent_role?: string;
  child_types?: string[];
  parent_types?: string[];
  member_types?: string[];
  ordered?: boolean;
  timed?: boolean;
  [k: string]: unknown;
}

export interface BindingRegistryMeta {
  title?: string;
  description?: string;
  subject_kind_variables?: KindVariable[];
  subject_statement_bindings?: Binding[];
  relation_vocabulary?: RelationTerm[];
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
