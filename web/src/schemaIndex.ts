import type {
  IndexEntry,
  SchemaDocument,
  SchemaIndex,
  TopicCategory,
  TopicsFile,
} from "./types";

const BASE = import.meta.env.BASE_URL;

export async function loadIndex(): Promise<SchemaIndex> {
  const res = await fetch(`${BASE}schemas/V_delta/index.json`);
  if (!res.ok) throw new Error(`Failed to load index.json: ${res.status}`);
  return res.json();
}

// Topics live alongside the schema set but have no semantic relationship
// to validation -- they are purely a viewer affordance. Missing or malformed
// files are non-fatal: the viewer falls back to a single Uncategorized node.
export async function loadTopics(): Promise<TopicsFile | null> {
  try {
    const res = await fetch(`${BASE}schemas/V_delta/topics.json`);
    if (!res.ok) return null;
    return await res.json();
  } catch {
    return null;
  }
}

export async function loadSchema(entry: IndexEntry): Promise<SchemaDocument> {
  // entry.path is repo-relative, e.g. "schemas/V_delta/stable/base.json".
  const res = await fetch(`${BASE}${entry.path}`);
  if (!res.ok) throw new Error(`Failed to load ${entry.path}: ${res.status}`);
  return res.json();
}

// A tree node used by both the superclass view and the topic view.
// Leaf nodes carry an `entry` and are clickable; folder/category nodes
// have `entry: null` and are pure grouping headers.
export interface TreeNode {
  key: string;
  label: string;
  entry: IndexEntry | null;
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
      return { entry, key, label: entry.class_name, children: [] };
    }
    const nextSeen = new Set(seen);
    nextSeen.add(entry.class_name);
    const kids = (byParent.get(entry.class_name) ?? [])
      .slice()
      .sort(sortByName)
      .map((child) => buildNode(child, key, nextSeen));
    return { entry, key, label: entry.class_name, children: kids };
  };

  return roots.map((r) => buildNode(r, "", new Set()));
}

export function sortedFlat(entries: IndexEntry[]): IndexEntry[] {
  return entries.slice().sort((a, b) => a.class_name.localeCompare(b.class_name));
}

// Build a topic tree: folder nodes from the topics file, with leaves
// resolved against the live index by class_name. A class listed in topics
// but not present in the index is dropped (with a warning). Any class
// present in the index but not referenced anywhere in the topics file is
// gathered under a synthesized "Uncategorized" root so nothing disappears
// from the viewer.
export function buildTopicTree(
  entries: IndexEntry[],
  topics: TopicsFile | null,
): TreeNode[] {
  const byName = new Map(entries.map((e) => [e.class_name, e]));
  const referenced = new Set<string>();

  const buildCategory = (cat: TopicCategory, keyPrefix: string): TreeNode => {
    const key = `${keyPrefix}/${cat.name}`;
    const leafChildren: TreeNode[] = [];
    for (const className of cat.classes ?? []) {
      const entry = byName.get(className);
      if (!entry) {
        console.warn(
          `topics.json references unknown class "${className}" under "${cat.name}"`,
        );
        continue;
      }
      referenced.add(className);
      leafChildren.push({
        entry,
        key: `${key}/${className}`,
        label: className,
        children: [],
      });
    }
    leafChildren.sort((a, b) => a.label.localeCompare(b.label));

    const subCategories = (cat.children ?? []).map((c) =>
      buildCategory(c, key),
    );
    // Folders before leaves so the tree groups subtopics at the top of
    // each category.
    return {
      entry: null,
      key,
      label: cat.name,
      children: [...subCategories, ...leafChildren],
    };
  };

  const rootLeaves: TreeNode[] = [];
  for (const className of topics?.classes ?? []) {
    const entry = byName.get(className);
    if (!entry) {
      console.warn(
        `topics.json references unknown top-level class "${className}"`,
      );
      continue;
    }
    referenced.add(className);
    rootLeaves.push({
      entry,
      key: `/${className}`,
      label: className,
      children: [],
    });
  }
  const rootCategories = (topics?.topics ?? []).map((t) =>
    buildCategory(t, ""),
  );

  // Display order: the "meta" category first, "base" leaf second, then the
  // remaining top-level categories alphabetized. Any other root leaves slot
  // in alphabetically alongside categories after base.
  const metaCategory = rootCategories.find((n) => n.label === "meta") ?? null;
  const baseLeaf = rootLeaves.find((n) => n.label === "base") ?? null;
  const remaining: TreeNode[] = [
    ...rootCategories.filter((n) => n !== metaCategory),
    ...rootLeaves.filter((n) => n !== baseLeaf),
  ].sort((a, b) => a.label.localeCompare(b.label));

  const roots: TreeNode[] = [];
  if (metaCategory) roots.push(metaCategory);
  if (baseLeaf) roots.push(baseLeaf);
  roots.push(...remaining);

  const uncategorized = entries
    .filter((e) => !referenced.has(e.class_name))
    .sort((a, b) => a.class_name.localeCompare(b.class_name));
  if (uncategorized.length > 0) {
    roots.push({
      entry: null,
      key: "/Uncategorized",
      label: "Uncategorized",
      children: uncategorized.map((e) => ({
        entry: e,
        key: `/Uncategorized/${e.class_name}`,
        label: e.class_name,
        children: [],
      })),
    });
  }
  return roots;
}
