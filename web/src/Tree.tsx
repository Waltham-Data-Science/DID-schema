import { useState } from "react";
import type { IndexEntry } from "./types";
import type { TreeNode } from "./schemaIndex";

interface Props {
  nodes: TreeNode[];
  selected: string | null;
  onSelect: (className: string) => void;
}

export function Tree({ nodes, selected, onSelect }: Props) {
  return (
    <ul className="tree">
      {nodes.map((n) => (
        <TreeItem key={n.key} node={n} selected={selected} onSelect={onSelect} />
      ))}
    </ul>
  );
}

function TreeItem({
  node,
  selected,
  onSelect,
}: {
  node: TreeNode;
  selected: string | null;
  onSelect: (className: string) => void;
}) {
  const [open, setOpen] = useState(false);
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
        <ClassLabel
          entry={node.entry}
          selected={selected === node.entry.class_name}
          onSelect={onSelect}
        />
      </div>
      {hasChildren && open && (
        <ul className="tree">
          {node.children.map((c) => (
            <TreeItem
              key={c.key}
              node={c}
              selected={selected}
              onSelect={onSelect}
            />
          ))}
        </ul>
      )}
    </li>
  );
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
