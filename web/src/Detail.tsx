import type { ReactElement } from "react";
import { useEffect, useState } from "react";
import type { IndexEntry, FieldDef, SchemaDocument } from "./types";
import { superclassName } from "./types";
import { loadSchema } from "./schemaIndex";

interface Props {
  entry: IndexEntry;
  onSelect: (className: string) => void;
}

export function Detail({ entry, onSelect }: Props) {
  const [doc, setDoc] = useState<SchemaDocument | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [showRaw, setShowRaw] = useState(false);

  useEffect(() => {
    let cancelled = false;
    setDoc(null);
    setError(null);
    setShowRaw(false);
    loadSchema(entry)
      .then((d) => {
        if (!cancelled) setDoc(d);
      })
      .catch((e) => {
        if (!cancelled) setError(String(e));
      });
    return () => {
      cancelled = true;
    };
  }, [entry.class_name, entry.path]);

  if (error) return <div className="detail-error">Error: {error}</div>;
  if (!doc) return <div className="detail-loading">Loading...</div>;

  const dc = doc.document_class ?? {
    class_name: entry.class_name,
    class_version: entry.class_version ?? undefined,
    superclasses: entry.superclasses,
    maturity_level: entry.maturity_level,
  };
  const maturity = dc.maturity_level ?? entry.maturity_level ?? null;

  return (
    <div className="detail">
      <header className="detail-header">
        <h2>
          {dc.class_name}
          {entry.is_meta && <span className="badge-meta">meta</span>}
        </h2>
        <dl className="detail-meta">
          <dt>Version</dt>
          <dd>{dc.class_version ?? "—"}</dd>
          <dt>Maturity</dt>
          <dd>
            <span className={`maturity-${maturity ?? "meta"}`}>
              {maturity ?? "(none)"}
            </span>
          </dd>
          <dt>Tier</dt>
          <dd>{entry.tier}</dd>
          <dt>Superclasses</dt>
          <dd>
            {dc.superclasses && dc.superclasses.length > 0 ? (
              dc.superclasses.map((ref, i) => {
                const name = superclassName(ref);
                return (
                  <span key={name}>
                    {i > 0 && ", "}
                    <button className="link" onClick={() => onSelect(name)}>
                      {name}
                    </button>
                  </span>
                );
              })
            ) : (
              <em>none</em>
            )}
          </dd>
          <dt>Path</dt>
          <dd>
            <code>{entry.path}</code>
          </dd>
        </dl>
      </header>

      {doc.fields && doc.fields.length > 0 && (
        <section>
          <h3>Fields</h3>
          <FieldsTable fields={doc.fields} />
        </section>
      )}

      {doc.depends_on && doc.depends_on.length > 0 && (
        <section>
          <h3>Depends on</h3>
          <ul className="kv-list">
            {doc.depends_on.map((d) => (
              <li key={d.name}>
                <code>{d.name}</code>
                {d.mustBeNonEmpty && (
                  <span className="flag-tag">mustBeNonEmpty</span>
                )}
                {d.documentation && (
                  <div className="docline">{d.documentation}</div>
                )}
              </li>
            ))}
          </ul>
        </section>
      )}

      {doc.file && doc.file.length > 0 && (
        <section>
          <h3>Files</h3>
          <ul className="kv-list">
            {doc.file.map((f) => (
              <li key={f.name}>
                <code>{f.name}</code>
                {f.documentation && (
                  <div className="docline">{f.documentation}</div>
                )}
              </li>
            ))}
          </ul>
        </section>
      )}

      <section>
        <button className="btn-secondary" onClick={() => setShowRaw((v) => !v)}>
          {showRaw ? "Hide raw JSON" : "View raw JSON"}
        </button>
        {showRaw && (
          <pre className="raw-json">{JSON.stringify(doc, null, 2)}</pre>
        )}
      </section>
    </div>
  );
}

function FieldsTable({ fields }: { fields: FieldDef[] }) {
  return (
    <table className="fields-table">
      <thead>
        <tr>
          <th>Name</th>
          <th>Type</th>
          <th>Default</th>
          <th>Flags</th>
          <th>Constraints</th>
          <th>Documentation</th>
        </tr>
      </thead>
      <tbody>
        {fields.flatMap((f) => renderFieldRows(f, 0, ""))}
      </tbody>
    </table>
  );
}

function renderFieldRows(
  field: FieldDef,
  depth: number,
  parentKey: string,
): ReactElement[] {
  const key = parentKey ? `${parentKey}.${field.name}` : field.name;
  const row = (
    <tr key={key} className={depth > 0 ? "field-row-nested" : undefined}>
      <td>
        <span
          className="field-name"
          style={{ paddingLeft: `${depth * 1.25}rem` }}
        >
          {depth > 0 && <span className="field-tree-prefix">└ </span>}
          <code>{field.name}</code>
        </span>
      </td>
      <td>
        <code>{field.type}</code>
      </td>
      <td>
        <code>{formatValue(field.default_value)}</code>
      </td>
      <td>
        <FlagList field={field} />
      </td>
      <td>
        <Constraints value={field.constraints} />
        {field.ontology && (
          <div className="ontology">
            <span className="ontology-label">ontology:</span>{" "}
            <code>{field.ontology.node}</code>
            {field.ontology.name ? ` (${field.ontology.name})` : ""}
          </div>
        )}
      </td>
      <td className="doc-cell">{field.documentation ?? ""}</td>
    </tr>
  );
  const childRows = (field.fields ?? []).flatMap((sub) =>
    renderFieldRows(sub, depth + 1, key),
  );
  return [row, ...childRows];
}

function FlagList({ field }: { field: FieldDef }) {
  const flags: string[] = [];
  if (field.mustBeNonEmpty) flags.push("nonEmpty");
  if (field.mustBeScalar) flags.push("scalar");
  if (field.mustNotHaveNaN) flags.push("noNaN");
  if (field.queryable) flags.push("queryable");
  if (flags.length === 0) return <span className="muted">—</span>;
  return (
    <>
      {flags.map((f) => (
        <span key={f} className="flag-tag">
          {f}
        </span>
      ))}
    </>
  );
}

function Constraints({ value }: { value: FieldDef["constraints"] }) {
  if (!value || Object.keys(value).length === 0) {
    return <span className="muted">—</span>;
  }
  return (
    <ul className="constraints">
      {Object.entries(value).map(([k, v]) => (
        <li key={k}>
          <span className="constraint-key">{k}:</span>{" "}
          {Array.isArray(v) ? (
            v.map((item, i) => (
              <span key={i} className="enum-chip">
                {String(item)}
              </span>
            ))
          ) : (
            <code>{formatValue(v)}</code>
          )}
        </li>
      ))}
    </ul>
  );
}

function formatValue(v: unknown): string {
  if (v === null) return "null";
  if (v === undefined) return "—";
  if (typeof v === "string") return v === "" ? '""' : v;
  return JSON.stringify(v);
}
