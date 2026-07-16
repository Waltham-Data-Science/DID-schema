import { useEffect, useMemo, useState } from "react";
import type {
  Binding,
  BindingRegistryMeta,
  IndexEntry,
  RelationTerm,
} from "./types";
import { loadBindingRegistry } from "./schemaIndex";

interface Props {
  entry: IndexEntry;
}

// Columns shown first (in this order) when a binding carries them; any other
// keys a corpus-derived binding introduces are appended alphabetically so the
// browser keeps rendering new binding shapes without a code change.
const PREFERRED_COLUMNS = [
  "variable",
  "method",
  "class",
  "data_type",
  "values",
  "ontology",
  "root_node",
  "notes",
];

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
  const relations = reg.relation_vocabulary ?? [];

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
          this set (checked at ingest). Each is a subtree value binding — the
          admissible term value is drawn from the given <code>ontology</code>{" "}
          subtree rooted at <code>root_node</code>.
        </p>
        {kinds.length === 0 ? (
          <p className="muted">No kind variables declared.</p>
        ) : (
          <table className="fields-table">
            <thead>
              <tr>
                <th>Variable</th>
                <th>Ontology</th>
                <th>Root node</th>
              </tr>
            </thead>
            <tbody>
              {kinds.map((k) => (
                <tr key={k.variable.name}>
                  <td>
                    <code>{k.variable.name}</code>
                    {k.variable.node ? (
                      <span className="node-curie"> {k.variable.node}</span>
                    ) : null}
                  </td>
                  <td>
                    {k.ontology ? (
                      <span className="enum-chip">{k.ontology}</span>
                    ) : (
                      <span className="muted">—</span>
                    )}
                  </td>
                  <td>
                    {k.root_node ? (
                      <code>{k.root_node}</code>
                    ) : (
                      <span className="muted">—</span>
                    )}
                  </td>
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
          Corpus-derived value bindings, added during discovery (D3/D6). Each is
          keyed on <code>variable.node</code> (and <code>method.node</code> on
          interactions) within a carrier <code>class</code>, with an inline
          admissible-set spec: a <code>data_type</code>, an enumerated{" "}
          <code>values</code> list, or an ontology subtree (<code>ontology</code>{" "}
          + <code>root_node</code>). Consumer tooling resolves a term value against
          the matching binding at validation time.
        </p>
        {bindings.length === 0 ? (
          <p className="muted">
            No bindings yet — the registry is seeded with the kind variables
            above; per-variable value bindings are populated as the corpus is
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

      <section>
        <h3>
          Relation vocabulary{" "}
          <span className="count-pill">{relations.length}</span>
        </h3>
        <p className="section-note">
          The admissible terms carried on{" "}
          <code>directed_relation.relation</code> /{" "}
          <code>undirected_relation.relation</code> (D6). <code>class</code> pins
          each term to its carrier — <code>directed_relation</code> (asymmetric
          child → parent) or <code>undirected_relation</code> (symmetric members)
          — and thus which endpoint types and optional fields apply.
        </p>
        {relations.length === 0 ? (
          <p className="muted">No relation terms declared.</p>
        ) : (
          <table className="fields-table">
            <thead>
              <tr>
                <th>Term</th>
                <th>Node</th>
                <th>Class</th>
                <th>Child → Parent types</th>
                <th>Flags</th>
              </tr>
            </thead>
            <tbody>
              {relations.map((r) => (
                <RelationRow key={r.name} term={r} />
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
  // variable/method are NodeRef objects {node, name}.
  if (
    (column === "variable" || column === "method") &&
    typeof value === "object" &&
    value !== null &&
    "name" in value
  ) {
    const ref = value as { node?: string; name?: string };
    return (
      <span>
        <code>{ref.name}</code>
        {ref.node ? <span className="node-curie"> {ref.node}</span> : null}
      </span>
    );
  }
  if (column === "values" && Array.isArray(value)) {
    return (
      <>
        {value.map((v, i) => (
          <span key={i} className="enum-chip">
            {String(v)}
          </span>
        ))}
      </>
    );
  }
  if (column === "data_type" && typeof value === "string") {
    return <span className="enum-chip">{value}</span>;
  }
  if (typeof value === "string" || typeof value === "number" || typeof value === "boolean") {
    return <code>{String(value)}</code>;
  }
  return <code>{JSON.stringify(value)}</code>;
}

// One row of the relation vocabulary: term, backing node, carrier class, typed
// endpoints (child -> parent for directed; members for undirected), and flags.
function RelationRow({ term }: { term: RelationTerm }) {
  const directed = term.class !== "undirected_relation";
  const flags: string[] = [];
  if (term.ordered) flags.push("ordered");
  if (term.timed) flags.push("timed");
  const typeChips = (types: string[] | undefined) =>
    types && types.length > 0 ? (
      types.map((t) => (
        <span key={t} className="enum-chip">
          {t}
        </span>
      ))
    ) : (
      <span className="muted">open</span>
    );
  return (
    <tr>
      <td>
        <code>{term.name}</code>
      </td>
      <td>
        {term.node ? (
          <span className="node-curie">{term.node}</span>
        ) : (
          <span className="muted">— open</span>
        )}
      </td>
      <td>
        <span className="enum-chip">
          {directed ? "directed" : "undirected"}
        </span>
      </td>
      <td>
        {directed ? (
          <span>
            {typeChips(term.child_types)}
            <span className="rel-arrow"> → </span>
            {typeChips(term.parent_types)}
          </span>
        ) : (
          typeChips(term.member_types)
        )}
      </td>
      <td>
        {flags.length === 0 ? (
          <span className="muted">—</span>
        ) : (
          flags.map((f) => (
            <span key={f} className="flag-tag">
              {f}
            </span>
          ))
        )}
      </td>
    </tr>
  );
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
