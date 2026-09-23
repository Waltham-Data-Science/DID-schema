import { useEffect, useMemo, useState } from "react";
import type { IndexEntry, SchemaIndex, TopicsFile } from "./types";
import {
  buildTopicTree,
  buildTree,
  isBindingRegistry,
  loadIndex,
  loadTopics,
  loadVersions,
  sortedFlat,
} from "./schemaIndex";
import type { TreeNode } from "./schemaIndex";
import { FlatList, Tree } from "./Tree";
import { Detail } from "./Detail";
import { BindingRegistry } from "./BindingRegistry";
import { Coverage } from "./Coverage";
import { ClassDetail } from "./ClassDetail";
import { Tenets } from "./Tenets";
import { Editor } from "./Editor";
import { AuthPanel } from "./AuthPanel";
import { loadAuth } from "./auth";
import type { AuthState } from "./auth";
import { ErrorBoundary } from "./ErrorBoundary";
import "./styles.css";

type ViewMode = "topic" | "class" | "flat";

// The full-width panels, and the one piece of state each needs.
type Panel =
  | null
  | { kind: "coverage" }
  | { kind: "tenets" }
  | { kind: "walkthrough"; v1Class: string };

// The toggleable filter tags shown in the legend: a class is visible only when
// BOTH its maturity tag and its disposition tag are active (meta files are
// governed by the single "meta" tag). All on by default.
const MATURITY_TAGS = ["stable", "draft", "deprecated", "meta"] as const;
const DISPOSITION_TAGS = ["persist", "retire", "in_progress"] as const;
const ALL_TAGS: string[] = [...MATURITY_TAGS, ...DISPOSITION_TAGS];

function entryVisible(e: IndexEntry, active: Set<string>): boolean {
  if (e.is_meta) return active.has("meta");
  const maturity = e.maturity_level ?? "meta";
  const disposition = e.disposition ?? "persist";
  return active.has(maturity) && active.has(disposition);
}

// Prune a tree to nodes that pass the predicate OR have a surviving descendant,
// so an ancestor stays visible as the path to a visible class (and folders keep
// only non-empty branches). Works for both the class tree and the topic tree.
function pruneTree(
  nodes: TreeNode[],
  keep: (e: IndexEntry) => boolean,
): TreeNode[] {
  const out: TreeNode[] = [];
  for (const n of nodes) {
    const kids = pruneTree(n.children, keep);
    const selfKept = n.entry ? keep(n.entry) : false;
    if (selfKept || kids.length > 0) out.push({ ...n, children: kids });
  }
  return out;
}

// sessionStorage key remembering which schema set the user last viewed.
const VERSION_KEY = "did-schema-set-version";

export default function App() {
  const [index, setIndex] = useState<SchemaIndex | null>(null);
  const [topics, setTopics] = useState<TopicsFile | null>(null);
  const [versions, setVersions] = useState<string[]>([]);
  const [version, setVersion] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [view, setView] = useState<ViewMode>("topic");
  const [selected, setSelected] = useState<string | null>(
    parseHash(window.location.hash),
  );
  const [editing, setEditing] = useState<boolean>(false);
  // WHICH FULL-WIDTH PANEL IS SHOWING. This was a pair of booleans, and adding
  // two more panels to a set of booleans is how a viewer ends up rendering two
  // of them at once. One value, one panel: `null` falls through to the selected
  // class's schema detail.
  const [panel, setPanel] = useState<Panel>(null);
  const [auth, setAuth] = useState<AuthState | null>(() => loadAuth());
  const [activeTags, setActiveTags] = useState<Set<string>>(
    () => new Set(ALL_TAGS),
  );
  const toggleTag = (tag: string) =>
    setActiveTags((prev) => {
      const next = new Set(prev);
      if (next.has(tag)) next.delete(tag);
      else next.add(tag);
      return next;
    });

  // Load the manifest of available schema sets, then pick the initial set:
  // a previously chosen set (if it still exists) else the manifest default.
  useEffect(() => {
    loadVersions()
      .then((m) => {
        setVersions(m.versions);
        const remembered = sessionStorage.getItem(VERSION_KEY);
        setVersion(
          remembered && m.versions.includes(remembered) ? remembered : m.default,
        );
      })
      .catch((e) => setError(String(e)));
  }, []);

  // (Re)load the index and topics whenever the selected set changes.
  useEffect(() => {
    if (!version) return;
    let cancelled = false;
    setIndex(null);
    setTopics(null);
    setError(null);
    sessionStorage.setItem(VERSION_KEY, version);
    loadIndex(version)
      .then((idx) => !cancelled && setIndex(idx))
      .catch((e) => !cancelled && setError(String(e)));
    loadTopics(version).then((t) => !cancelled && setTopics(t));
    return () => {
      cancelled = true;
    };
  }, [version]);

  useEffect(() => {
    const onHash = () => setSelected(parseHash(window.location.hash));
    window.addEventListener("hashchange", onHash);
    return () => window.removeEventListener("hashchange", onHash);
  }, []);

  const select = (className: string) => {
    // Selecting a class always returns to the detail view.
    setPanel(null);
    setEditing(false);
    window.location.hash = `#/${encodeURIComponent(className)}`;
  };

  // Open the per-class migration walkthrough for a did_v1 SOURCE class. Kept
  // separate from `select` on purpose: `select` takes a V_eta class name and
  // opens its schema, and the two namespaces overlap without being the same
  // (`image_stack` is a built class; `imageStack` is the v1 source).
  const openWalkthrough = (v1Class: string) => {
    setEditing(false);
    setPanel({ kind: "walkthrough", v1Class });
  };

  const keep = useMemo(
    () => (e: IndexEntry) => entryVisible(e, activeTags),
    [activeTags],
  );
  const classTree = useMemo(
    () => (index ? pruneTree(buildTree(index.schemas), keep) : []),
    [index, keep],
  );
  const topicTree = useMemo(
    () => (index ? pruneTree(buildTopicTree(index.schemas, topics), keep) : []),
    [index, topics, keep],
  );
  const flat = useMemo(
    () => (index ? sortedFlat(index.schemas).filter(keep) : []),
    [index, keep],
  );
  const selectedEntry = useMemo(
    () =>
      index && selected
        ? index.schemas.find((s) => s.class_name === selected) ?? null
        : null,
    [index, selected],
  );

  if (error) return <div className="fatal">Failed to load index: {error}</div>;
  if (!index) return <div className="loading">Loading schema index...</div>;

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="sidebar-header">
          <h1>DID schemas</h1>
          <div className="set-version">
            <label htmlFor="set-version-select">set: </label>
            <select
              id="set-version-select"
              value={version ?? ""}
              onChange={(e) => setVersion(e.target.value)}
              title="Schema set version to browse"
            >
              {versions.map((v) => (
                <option key={v} value={v}>
                  {v}
                </option>
              ))}
            </select>
          </div>
          <AuthPanel auth={auth} onAuth={setAuth} />
        </div>
        <div className="sidebar-controls">
          <div className="view-toggle" role="tablist">
            <button
              role="tab"
              aria-selected={view === "topic"}
              className={view === "topic" ? "active" : ""}
              onClick={() => setView("topic")}
            >
              Topic
            </button>
            <button
              role="tab"
              aria-selected={view === "class"}
              className={view === "class" ? "active" : ""}
              onClick={() => setView("class")}
            >
              Class
            </button>
            <button
              role="tab"
              aria-selected={view === "flat"}
              className={view === "flat" ? "active" : ""}
              onClick={() => setView("flat")}
            >
              Flat
            </button>
          </div>
          <button
            className="btn-add"
            onClick={() => setEditing(true)}
            aria-pressed={editing}
            title="Open the editor for a new schema"
          >
            + Add new schema
          </button>
          <button
            className="btn-coverage"
            onClick={() => {
              setPanel({ kind: "coverage" });
              setEditing(false);
            }}
            aria-pressed={panel?.kind === "coverage"}
            title="V_eta migration coverage: every did_v1 class and its V_eta fate"
          >
            ⛿ Coverage ledger
          </button>
          <button
            className="btn-coverage"
            onClick={() => {
              setPanel({ kind: "tenets" });
              setEditing(false);
            }}
            aria-pressed={panel?.kind === "tenets"}
            title="Brainstorm J's 14 tenets and the classes each one shaped"
          >
            ✦ Tenets
          </button>
        </div>
        <nav className="sidebar-scroll">
          {view === "topic" ? (
            <Tree nodes={topicTree} selected={selected} onSelect={select} />
          ) : view === "class" ? (
            <Tree nodes={classTree} selected={selected} onSelect={select} />
          ) : (
            <FlatList entries={flat} selected={selected} onSelect={select} />
          )}
        </nav>
        <Legend activeTags={activeTags} onToggle={toggleTag} />
      </aside>
      <main className="content">
        {editing ? (
          <ErrorBoundary resetKey="editor">
            <Editor
              index={index.schemas}
              version={version}
              onCancel={() => setEditing(false)}
            />
          </ErrorBoundary>
        ) : panel?.kind === "coverage" ? (
          <ErrorBoundary resetKey="coverage">
            <Coverage onSelect={select} onOpenClass={openWalkthrough} />
          </ErrorBoundary>
        ) : panel?.kind === "tenets" ? (
          <ErrorBoundary resetKey="tenets">
            <Tenets onSelect={select} onOpenClass={openWalkthrough} />
          </ErrorBoundary>
        ) : panel?.kind === "walkthrough" ? (
          <ErrorBoundary resetKey={`wt-${panel.v1Class}`}>
            <ClassDetail
              v1Class={panel.v1Class}
              index={index.schemas}
              onSelect={select}
              onBack={() => setPanel({ kind: "coverage" })}
            />
          </ErrorBoundary>
        ) : selectedEntry ? (
          <ErrorBoundary resetKey={selectedEntry.class_name}>
            {isBindingRegistry(selectedEntry) ? (
              <BindingRegistry entry={selectedEntry} />
            ) : (
              <Detail entry={selectedEntry} />
            )}
          </ErrorBoundary>
        ) : (
          <div className="placeholder">
            <h2>Select a schema from the left to view its definition.</h2>
            <p>
              Browse by <strong>Topic</strong> (subject-area folders, for
              humans), <strong>Class</strong> (by superclass), or{" "}
              <strong>Flat</strong> (alphabetical). A class with multiple
              superclasses appears under each parent in the class view.
            </p>
          </div>
        )}
      </main>
    </div>
  );
}

function Legend({
  activeTags,
  onToggle,
}: {
  activeTags: Set<string>;
  onToggle: (tag: string) => void;
}) {
  // tag -> [css class, visible label, tooltip]
  const items: Array<[string, string, string, string]> = [
    ["stable", "maturity-stable", "stable", "maturity: stable"],
    ["draft", "maturity-draft", "draft", "maturity: draft"],
    ["deprecated", "maturity-deprecated", "deprecated", "maturity: deprecated"],
    ["meta", "maturity-meta", "meta", "schema-machinery meta files"],
    ["persist", "badge-persist", "persist", "settled go-forward class (final V1)"],
    ["retire", "badge-retire", "retire", "decided to dissolve/delete; not in final V1"],
    ["in_progress", "badge-wip", "wip", "persists but its 6/7 disposition is not yet finalized"],
  ];
  return (
    <div className="legend" role="group" aria-label="Filter classes by tag">
      {items.map(([tag, cls, label, tip]) => {
        const on = activeTags.has(tag);
        return (
          <span key={tag} style={{ display: "contents" }}>
            {tag === "persist" && <span className="legend-sep" />}
            <button
              type="button"
              className={`legend-item ${cls} ${on ? "" : "legend-off"}`}
              aria-pressed={on}
              title={`${tip} — click to ${on ? "hide" : "show"}`}
              onClick={() => onToggle(tag)}
            >
              {label}
            </button>
          </span>
        );
      })}
    </div>
  );
}

function parseHash(hash: string): string | null {
  if (!hash) return null;
  const m = hash.match(/^#\/(.+)$/);
  return m ? decodeURIComponent(m[1]) : null;
}
