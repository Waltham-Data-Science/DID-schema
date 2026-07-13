import { useEffect, useMemo, useState } from "react";
import type { Binding, BindingRegistryMeta, IndexEntry } from "./types";
import { loadBindingRegistry } from "./schemaIndex";

interface Props {
  entry: IndexEntry;
}

// Columns shown first (in this order) when a binding carries them; any other
// keys a corpus-derived binding introduces are appended alphabetically so the
// browser keeps rendering new binding shapes without a code change.
const PREFERRED_COLUMNS = ["variable", "value_set", "method", "root", "source", "notes"];

export function BindingRegistry({ entry }: Props) {
  const [reg, setReg] = useState<BindingRegistryMeta | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [showRaw, setShowRaw] = useState(false);

  useEffect(() => {
    let cancelled = false;
    setReg(null);
    setError(null);
    setShowRaw(false);
    loadBindingRegistry(entry)
      .then((r) => !cancelled && setReg(r))
      .catch((e) => !cancelled && setError(String(e)));
    return () => {
      cancelled = true;
    };
  }, [entry.path]);

  const bindingColumns = useMemo(
    () => bindingKeys(reg?.bindings ?? []),
    [reg],
  );

  if (error) return <div className="detail-error">Error: {error}</div>;
  if (!reg) return <div className="detail-loading">Loading...</div>;

  const kinds = reg.kind_variables ?? [];
  const bindings = reg.bindings ?? [];

  return (
    <div className="detail">
      <header className="detail-header">
        <h2>
          {reg.title ?? "Binding registry"}
          <span className="badge-meta">meta</span>
        </h2>
        {reg.description && <p className="registry-description">{reg.description}</p>}
        <dl className="detail-meta">
          <dt>Path</dt>
          <dd>
            <code>{entry.path}</code>
          </dd>
        </dl>
      </header>

      <section>
        <h3>
          Kind variables <span className="count-pill">{kinds.length}</span>
        </h3>
        <p className="section-note">
          The kind-defining variables (D9): a subject is expected to carry at
          least one <code>term_assertion</code> whose <code>variable</code> is in
          this set (checked at ingest). Each maps a variable to the ontology
          value-set its term value is drawn from.
        </p>
        {kinds.length === 0 ? (
          <p className="muted">No kind variables declared.</p>
        ) : (
          <table className="fields-table">
            <thead>
              <tr>
                <th>Variable</th>
                <th>Value set</th>
                <th>Root</th>
                <th>Source</th>
              </tr>
            </thead>
            <tbody>
              {kinds.map((k) => (
                <tr key={k.variable}>
                  <td>
                    <code>{k.variable}</code>
                  </td>
                  <td>
                    <span className="enum-chip">{k.value_set}</span>
                  </td>
                  <td>{k.root ? <code>{k.root}</code> : <span className="muted">—</span>}</td>
                  <td>{k.source ?? <span className="muted">—</span>}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>

      <section>
        <h3>
          Bindings <span className="count-pill">{bindings.length}</span>
        </h3>
        <p className="section-note">
          Corpus-derived <code>variable → value_set</code> bindings, added during
          discovery (D3/D6). Consumer tooling resolves a term value against the
          bound value-set at validation time.
        </p>
        {bindings.length === 0 ? (
          <p className="muted">
            No bindings yet — the registry is seeded with the kind variables
            above; per-variable value-set bindings are populated as the corpus is
            surveyed.
          </p>
        ) : (
          <table className="fields-table">
            <thead>
              <tr>
                {bindingColumns.map((c) => (
                  <th key={c}>{c}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {bindings.map((b, i) => (
                <tr key={i}>
                  {bindingColumns.map((c) => (
                    <td key={c}>
                      <BindingCell value={b[c]} column={c} />
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>

      {reg.notes && (
        <section>
          <h3>Notes</h3>
          <p className="docline">{reg.notes}</p>
        </section>
      )}

      <section>
        <button className="btn-secondary" onClick={() => setShowRaw((v) => !v)}>
          {showRaw ? "Hide raw JSON" : "View raw JSON"}
        </button>
        {showRaw && <pre className="raw-json">{JSON.stringify(reg, null, 2)}</pre>}
      </section>
    </div>
  );
}

function BindingCell({ value, column }: { value: unknown; column: string }) {
  if (value === undefined || value === null || value === "") {
    return <span className="muted">—</span>;
  }
  if (column === "value_set" && typeof value === "string") {
    return <span className="enum-chip">{value}</span>;
  }
  if (typeof value === "string" || typeof value === "number" || typeof value === "boolean") {
    return <code>{String(value)}</code>;
  }
  return <code>{JSON.stringify(value)}</code>;
}

// Union of keys across all bindings, PREFERRED_COLUMNS first (in order), the
// rest alphabetized. Guarantees stable columns even for heterogeneous rows.
function bindingKeys(bindings: Binding[]): string[] {
  const seen = new Set<string>();
  for (const b of bindings) {
    for (const k of Object.keys(b)) seen.add(k);
  }
  const preferred = PREFERRED_COLUMNS.filter((c) => seen.has(c));
  const rest = [...seen].filter((k) => !PREFERRED_COLUMNS.includes(k)).sort();
  return [...preferred, ...rest];
}
