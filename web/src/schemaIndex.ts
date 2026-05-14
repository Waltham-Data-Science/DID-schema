import type { IndexEntry, SchemaDocument, SchemaIndex } from "./types";

const BASE = import.meta.env.BASE_URL;

export async function loadIndex(): Promise<SchemaIndex> {
  const res = await fetch(`${BASE}schemas/V_delta/index.json`);
  if (!res.ok) throw new Error(`Failed to load index.json: ${res.status}`);
  return res.json();
}

export async function loadSchema(entry: IndexEntry): Promise<SchemaDocument> {
  // entry.path is repo-relative, e.g. "schemas/V_delta/stable/base.json".
  const res = await fetch(`${BASE}${entry.path}`);
  if (!res.ok) throw new Error(`Failed to load ${entry.path}: ${res.status}`);
  return res.json();
}

// A tree node for the left-pane superclass view. The same class_name may
// appear under multiple parents -- one TreeNode per occurrence -- so users
// can find a class via any of its parents.
export interface TreeNode {
  entry: IndexEntry;
  // Unique key (path-from-root) for React.
  key: string;
  children: TreeNode[];
}

export function buildTree(entries: IndexEntry[]): TreeNode[] {
  const byParent = new Map<string, IndexEntry[]>();
  const roots: IndexEntry[] = [];
  for (const e of entries) {
    if (!e.superclasses || e.superclasses.length === 0) {
      roots.push(e);
      continue;
    }
    for (const parent of e.superclasses) {
      if (!byParent.has(parent)) byParent.set(parent, []);
      byParent.get(parent)!.push(e);
    }
  }
  const sortByName = (a: IndexEntry, b: IndexEntry) =>
    a.class_name.localeCompare(b.class_name);
  roots.sort(sortByName);

  const buildNode = (
    entry: IndexEntry,
    keyPrefix: string,
    seen: Set<string>,
  ): TreeNode => {
    const key = `${keyPrefix}/${entry.class_name}`;
    // Cycle guard: a class cannot be its own ancestor.
    if (seen.has(entry.class_name)) {
      return { entry, key, children: [] };
    }
    const nextSeen = new Set(seen);
    nextSeen.add(entry.class_name);
    const kids = (byParent.get(entry.class_name) ?? [])
      .slice()
      .sort(sortByName)
      .map((child) => buildNode(child, key, nextSeen));
    return { entry, key, children: kids };
  };

  return roots.map((r) => buildNode(r, "", new Set()));
}

export function sortedFlat(entries: IndexEntry[]): IndexEntry[] {
  return entries.slice().sort((a, b) => a.class_name.localeCompare(b.class_name));
}
