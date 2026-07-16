import { useEffect, useState } from "react";
import type {
  Binding,
  BindingRegistryMeta,
  IndexEntry,
  NodeRef,
  RelationTerm,
} from "./types";
import { loadBindingRegistry } from "./schemaIndex";

interface Props {
  entry: IndexEntry;
}

// Columns shown first (in this order) when a binding carries them; any other keys
// a corpus-derived binding introduces are appended alphabetically so the browser
// keeps rendering new binding shapes without a code change. `subject_defining` is
// handled specially (a badge on the variable cell), so it is not a column here.
const PREFERRED_COLUMNS = [
  "variable",
  "method",
  "class",
  "values",
  "ontology",
  "root_node",
  "notes",
];

// Raw key -> human column header (so the bindings table matches the Title-Case
// headers of the other tables instead of showing raw snake_case keys).
const COLUMN_LABELS: Record<string, string> = {
  variable: "Variable",
  method: "Method",
  class: "Class",
  values: "Values",
  ontology: "Ontology",
  root_node: "Root node",
  notes: "Notes",
};

const DASH = "—";

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

  if (error) return <div className="detail-error">Error: {error}</div>;
  if (!reg) return <div className="detail-loading">Loading...</div>;

  const bindings = reg.subject_statement_bindings ?? [];
  const examples = reg.binding_examples ?? [];
  const relations = reg.relation_bindings ?? [];

  return (
    <div className="detail">
      <header className="detail-header">
        <h2>
          {reg.title ?? "Binding registry"}
          <span className="badge-meta">meta</span>
        </h2>
        {reg.description && (
          <p className="registry-description">
            <RichText text={reg.description} />
          </p>
        )}
        <dl className="detail-meta">
          <dt>Path</dt>
          <dd>
            <code>{entry.path}</code>
          </dd>
        </dl>
      </header>

      <section>
        <h3>
          Subject statement bindings{" "}
          <span className="count-pill">{bindings.length}</span>
        </h3>
        <p className="section-note">
          Each maps a variable (and, on interactions, a method) to the concrete
          subject_statement leaf <code>class</code> that carries the statement
          (e.g. <code>mass_observation</code>, <code>dose_manipulation</code>,{" "}
          <code>term_assertion</code>). The leaf fixes the value type — no{" "}
          <code>data_type</code> — and a term-valued leaf additionally pins its
          admissible term set (<code>values</code> or an <code>ontology</code>{" "}
          subtree). Rows flagged <span className="flag-tag">subject-defining</span>{" "}
          are the kind ingestion invariant (D9): a subject is expected to carry ≥1
          assertion whose variable matches one. The rest are populated by the
          D3/D6 corpus sweep.
        </p>
        <BindingTable bindings={bindings} emptyLabel="No bindings declared." />
      </section>

      <section>
        <h3>
          Binding examples <span className="count-pill">{examples.length}</span>
        </h3>
        <p className="section-note">
          Illustrative only — <em>not</em> swept data. These show the binding
          shapes: a term leaf with an ontology subtree, a term leaf with an
          enumerated set of ontology terms, a dimensional leaf (no spec), and a
          method+variable interaction.
        </p>
        <BindingTable bindings={examples} emptyLabel="No examples." />
      </section>

      <section>
        <h3>
          Relation bindings{" "}
          <span className="count-pill">{relations.length}</span>
        </h3>
        <p className="section-note">
          The admissible terms carried on{" "}
          <code>directed_relation.relation</code> /{" "}
          <code>undirected_relation.relation</code> (D6). <code>class</code> pins
          each term to its carrier — <code>directed_relation</code> (asymmetric
          from → to) or <code>undirected_relation</code> (symmetric members) — and
          thus which endpoint types and optional fields apply. Abstract endpoint
          types (<code>entity</code>, <code>subject</code>) mean “any of that
          genus”; an empty endpoint is unconstrained.
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
                <th>From → To types</th>
                <th>Flags</th>
              </tr>
            </thead>
            <tbody>
              {relations.map((r) => (
                <RelationRow key={r.relation.name} term={r} />
              ))}
            </tbody>
          </table>
        )}
      </section>

      {reg.notes && (
        <section>
          <h3>Notes</h3>
          <p className="docline">
            <RichText text={reg.notes} />
          </p>
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

function BindingTable({
  bindings,
  emptyLabel,
}: {
  bindings: Binding[];
  emptyLabel: string;
}) {
  if (bindings.length === 0) return <p className="muted">{emptyLabel}</p>;
  const columns = bindingKeys(bindings);
  return (
    <table className="fields-table">
      <thead>
        <tr>
          {columns.map((c) => (
            <th key={c}>{COLUMN_LABELS[c] ?? c}</th>
          ))}
        </tr>
      </thead>
      <tbody>
        {bindings.map((b, i) => (
          <tr key={i}>
            {columns.map((c) => (
              <td key={c}>
                <BindingCell value={b[c]} column={c} binding={b} />
              </td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );
}

function isNodeRef(v: unknown): v is NodeRef {
  return typeof v === "object" && v !== null && "name" in v;
}

function NodeRefView({ value }: { value: NodeRef }) {
  return (
    <span>
      <code>{value.name}</code>
      {value.node ? <span className="node-curie"> {value.node}</span> : null}
    </span>
  );
}

function BindingCell({
  value,
  column,
  binding,
}: {
  value: unknown;
  column: string;
  binding: Binding;
}) {
  // The variable cell also carries the subject-defining badge.
  if (column === "variable") {
    return (
      <span>
        {isNodeRef(value) ? <NodeRefView value={value} /> : <span className="muted">{DASH}</span>}
        {binding.subject_defining && (
          <span className="flag-tag" title="kind-defining variable (D9)">
            subject-defining
          </span>
        )}
      </span>
    );
  }
  if (value === undefined || value === null || value === "") {
    return <span className="muted">{DASH}</span>;
  }
  if (column === "method" && isNodeRef(value)) {
    return <NodeRefView value={value} />;
  }
  // values are an enumeration of ontology-term NodeRefs (or, defensively, strings).
  if (column === "values" && Array.isArray(value)) {
    return (
      <>
        {value.map((v, i) =>
          isNodeRef(v) ? (
            <span key={i} className="enum-chip" title={v.node || undefined}>
              {v.name}
            </span>
          ) : (
            <span key={i} className="enum-chip">
              {String(v)}
            </span>
          ),
        )}
      </>
    );
  }
  if (column === "class" && typeof value === "string") {
    return <span className="enum-chip">{value}</span>;
  }
  if (typeof value === "string" || typeof value === "number" || typeof value === "boolean") {
    return <code>{String(value)}</code>;
  }
  return <code>{JSON.stringify(value)}</code>;
}

// One row of the relation bindings: term, backing node, carrier class, typed
// endpoints (from -> to for directed; members for undirected), and flags. The
// endpoint roles show as a tooltip on the type group.
function RelationRow({ term }: { term: RelationTerm }) {
  const directed = term.class === "directed_relation";
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
      <span className="muted">any</span>
    );
  return (
    <tr>
      <td>
        <code>{term.relation.name}</code>
      </td>
      <td>
        {term.relation.node ? (
          <span className="node-curie">{term.relation.node}</span>
        ) : (
          <span className="muted">{DASH}</span>
        )}
      </td>
      <td>
        <code>{term.class}</code>
      </td>
      <td>
        {directed ? (
          <span title={roleHint(term)}>
            {typeChips(term.from_types)}
            <span className="rel-arrow"> → </span>
            {typeChips(term.to_types)}
          </span>
        ) : (
          typeChips(term.member_types)
        )}
      </td>
      <td>
        {flags.length === 0 ? (
          <span className="muted">{DASH}</span>
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

function roleHint(term: RelationTerm): string | undefined {
  if (!term.from_role && !term.to_role) return undefined;
  return `from: ${term.from_role ?? "?"} → to: ${term.to_role ?? "?"}`;
}

// Render a string with backtick-delimited `code` spans and turn " -- " into an
// em dash, so meta prose that uses lightweight markup renders instead of showing
// the raw backticks.
function RichText({ text }: { text: string }) {
  const parts = text.split(/(`[^`]+`)/g);
  return (
    <>
      {parts.map((p, i) =>
        p.length > 1 && p.startsWith("`") && p.endsWith("`") ? (
          <code key={i}>{p.slice(1, -1)}</code>
        ) : (
          <span key={i}>{p.replace(/ -- /g, " — ")}</span>
        ),
      )}
    </>
  );
}

// Union of keys across all bindings, PREFERRED_COLUMNS first (in order), the rest
// alphabetized. `subject_defining` is rendered as a badge on the variable cell, so
// it is never a column. Guarantees stable columns even for heterogeneous rows.
function bindingKeys(bindings: Binding[]): string[] {
  const seen = new Set<string>();
  for (const b of bindings) {
    for (const k of Object.keys(b)) {
      if (k !== "subject_defining") seen.add(k);
    }
  }
  const preferred = PREFERRED_COLUMNS.filter((c) => seen.has(c));
  const rest = [...seen].filter((k) => !PREFERRED_COLUMNS.includes(k)).sort();
  return [...preferred, ...rest];
}
