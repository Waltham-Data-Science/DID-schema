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

// Inside a schema file, `superclasses` is an array of objects with at least
// a `class_name` key. The repo-level index.json normalizes these to plain
// strings, so callers may see either shape -- always pass through
// `superclassName()` to extract the string.
export type SuperclassRef = string | { class_name: string; [k: string]: unknown };

export function superclassName(ref: SuperclassRef): string {
  return typeof ref === "string" ? ref : ref.class_name;
}
