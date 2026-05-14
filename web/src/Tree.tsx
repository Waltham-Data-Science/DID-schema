import { useState } from "react";
import type { IndexEntry } from "./types";
import type { TreeNode } from "./schemaIndex";

interface Props {
  nodes: TreeNode[];
  selected: string | null;
  onSelect: (className: string) => void;
  // Topic-tree folder nodes start expanded; class-hierarchy nodes collapsed.
  defaultOpen?: boolean;
}

export function Tree({ nodes, selected, onSelect, defaultOpen = false }: Props) {
  return (
    <ul className="tree">
      {nodes.map((n) => (
        <TreeItem
          key={n.key}
          node={n}
          selected={selected}
          onSelect={onSelect}
          defaultOpen={defaultOpen}
        />
      ))}
    </ul>
  );
}

function TreeItem({
  node,
  selected,
  onSelect,
  defaultOpen,
}: {
  node: TreeNode;
  selected: string | null;
  onSelect: (className: string) => void;
  defaultOpen: boolean;
}) {
  const isFolder = node.entry === null;
  // Topic-folder rows are roomier than schema-leaf rows so the hierarchy
  // reads at a glance; default-open keeps the topic tree usable on load.
  const [open, setOpen] = useState(isFolder ? defaultOpen : false);
  const hasChildren = node.children.length > 0;
  return (
    <li>
      <div className="tree-row">
        {hasChildren ? (
          <button
            className="tree-caret"
            aria-label={open ? "Collapse" : "Expand"}
            onClick={() => setOpen((v) => !v)}
          >
            {open ? "▾" : "▸"}
          </button>
        ) : (
          <span className="tree-caret tree-caret-empty" />
        )}
        {isFolder ? (
          <button
            className="tree-folder"
            onClick={() => setOpen((v) => !v)}
            title={node.label}
          >
            {node.label}
            <span className="tree-folder-count">{leafCount(node)}</span>
          </button>
        ) : (
          <ClassLabel
            entry={node.entry!}
            selected={selected === node.entry!.class_name}
            onSelect={onSelect}
          />
        )}
      </div>
      {hasChildren && open && (
        <ul className="tree">
          {node.children.map((c) => (
            <TreeItem
              key={c.key}
              node={c}
              selected={selected}
              onSelect={onSelect}
              defaultOpen={defaultOpen}
            />
          ))}
        </ul>
      )}
    </li>
  );
}

function leafCount(node: TreeNode): number {
  if (node.entry !== null) return 1;
  let n = 0;
  for (const c of node.children) n += leafCount(c);
  return n;
}

export function FlatList({
  entries,
  selected,
  onSelect,
}: {
  entries: IndexEntry[];
  selected: string | null;
  onSelect: (className: string) => void;
}) {
  return (
    <ul className="tree flat-list">
      {entries.map((e) => (
        <li key={e.class_name}>
          <div className="tree-row">
            <span className="tree-caret tree-caret-empty" />
            <ClassLabel
              entry={e}
              selected={selected === e.class_name}
              onSelect={onSelect}
            />
          </div>
        </li>
      ))}
    </ul>
  );
}

function ClassLabel({
  entry,
  selected,
  onSelect,
}: {
  entry: IndexEntry;
  selected: boolean;
  onSelect: (className: string) => void;
}) {
  const maturity = entry.maturity_level ?? "meta";
  const cls = [
    "tree-label",
    `maturity-${maturity}`,
    selected ? "selected" : "",
  ]
    .filter(Boolean)
    .join(" ");
  return (
    <button className={cls} onClick={() => onSelect(entry.class_name)}>
      {entry.class_name}
      {entry.is_meta && <span className="badge-meta">meta</span>}
    </button>
  );
}
