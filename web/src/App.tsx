import { useEffect, useMemo, useState } from "react";
import type { SchemaIndex } from "./types";
import { buildTree, loadIndex, sortedFlat } from "./schemaIndex";
import { FlatList, Tree } from "./Tree";
import { Detail } from "./Detail";
import { ErrorBoundary } from "./ErrorBoundary";
import "./styles.css";

type ViewMode = "tree" | "flat";

export default function App() {
  const [index, setIndex] = useState<SchemaIndex | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [view, setView] = useState<ViewMode>("tree");
  const [selected, setSelected] = useState<string | null>(
    parseHash(window.location.hash),
  );

  useEffect(() => {
    loadIndex().then(setIndex).catch((e) => setError(String(e)));
  }, []);

  useEffect(() => {
    const onHash = () => setSelected(parseHash(window.location.hash));
    window.addEventListener("hashchange", onHash);
    return () => window.removeEventListener("hashchange", onHash);
  }, []);

  const select = (className: string) => {
    window.location.hash = `#/${encodeURIComponent(className)}`;
  };

  const tree = useMemo(
    () => (index ? buildTree(index.schemas) : []),
    [index],
  );
  const flat = useMemo(
    () => (index ? sortedFlat(index.schemas) : []),
    [index],
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
            set: <code>{index.set_version}</code>
          </div>
        </div>
        <div className="sidebar-controls">
          <div className="view-toggle" role="tablist">
            <button
              role="tab"
              aria-selected={view === "tree"}
              className={view === "tree" ? "active" : ""}
              onClick={() => setView("tree")}
            >
              Tree
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
            disabled
            title="Wires up in Step 5 of issue #28"
          >
            + Add new schema
          </button>
        </div>
        <nav className="sidebar-scroll">
          {view === "tree" ? (
            <Tree nodes={tree} selected={selected} onSelect={select} />
          ) : (
            <FlatList entries={flat} selected={selected} onSelect={select} />
          )}
        </nav>
        <Legend />
      </aside>
      <main className="content">
        {selectedEntry ? (
          <ErrorBoundary resetKey={selectedEntry.class_name}>
            <Detail entry={selectedEntry} onSelect={select} />
          </ErrorBoundary>
        ) : (
          <div className="placeholder">
            <h2>Select a schema from the left to view its definition.</h2>
            <p>
              Toggle between the <strong>Tree</strong> view (by superclass) and
              the <strong>Flat</strong> view (alphabetical). A class with
              multiple superclasses appears under each parent in tree view.
            </p>
          </div>
        )}
      </main>
    </div>
  );
}

function Legend() {
  return (
    <div className="legend">
      <span className="legend-item maturity-stable">stable</span>
      <span className="legend-item maturity-draft">draft</span>
      <span className="legend-item maturity-deprecated">deprecated</span>
      <span className="legend-item maturity-meta">meta</span>
    </div>
  );
}

function parseHash(hash: string): string | null {
  if (!hash) return null;
  const m = hash.match(/^#\/(.+)$/);
  return m ? decodeURIComponent(m[1]) : null;
}
