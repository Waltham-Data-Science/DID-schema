import { useMemo, useState } from "react";
import type { ReactNode } from "react";
import { FINAL_CLASS_SET_MD, TENETS_MD, VETA_FILES, VETA_KEY_PREFIX } from "./sources";
import { ancestors, buildModel, refTargets } from "./model";
import type { RawDependency, RawField, VetaClass, VetaModel } from "./model";
import { Markdown } from "./Markdown";

// THE V_eta SHAPE, READ FROM THE SCHEMA TREE AT BUILD TIME.
//
// Every class on this page comes from schemas/V_eta/**/*.json, every category
// from schemas/V_eta_final_class_set.md, every tenet from
// schemas/V_eta_tenets.md -- see sources.ts. There is no class data in this
// file. Change a schema, rebuild, and this page changes with it.
//
// The model is built once, when this module first loads: the inputs are
// constants of the bundle, so there is nothing to refetch.
const MODEL: VetaModel = buildModel(
  VETA_FILES,
  VETA_KEY_PREFIX,
  FINAL_CLASS_SET_MD,
  TENETS_MD,
);

type Tab = "classes" | "tenets";

interface Props {
  // Open a class in the app's full schema detail view (raw JSON, bindings...).
  onOpenSchema: (className: string) => void;
}

export default function VetaViewer({ onOpenSchema }: Props) {
  const [tab, setTab] = useState<Tab>("classes");
  const [selected, setSelected] = useState<string | null>(null);
  const [query, setQuery] = useState("");
  const [showExcluded, setShowExcluded] = useState(false);

  const openClass = (name: string) => {
    setSelected(name);
    setTab("classes");
  };

  return (
    <div className="detail veta">
      <header className="detail-header">
        <h2>V_eta schema shape</h2>
        <p className="registry-description">
          The go-forward V_eta class set, rendered directly from{" "}
          <code>schemas/V_eta/</code> at build time and grouped by the seven
          categories of <code>schemas/V_eta_final_class_set.md</code>. Nothing
          here is copied in: edit a schema, rebuild, and this page follows.
        </p>
        <Denominator model={MODEL} />
        <div className="view-toggle veta-tabs" role="tablist">
          <button
            role="tab"
            aria-selected={tab === "classes"}
            className={tab === "classes" ? "active" : ""}
            onClick={() => setTab("classes")}
          >
            Classes by category
          </button>
          <button
            role="tab"
            aria-selected={tab === "tenets"}
            className={tab === "tenets" ? "active" : ""}
            onClick={() => setTab("tenets")}
          >
            Tenets T1–T14
          </button>
        </div>
      </header>
      {tab === "classes" ? (
        <div className="veta-layout">
          <div className="veta-categories">
            <div className="cov-controls">
              <input
                className="cov-search"
                type="search"
                placeholder="Filter classes…"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
              />
              <label className="veta-toggle">
                <input
                  type="checkbox"
                  checked={showExcluded}
                  onChange={(e) => setShowExcluded(e.target.checked)}
                />{" "}
                show classes NOT in the final set
              </label>
            </div>
            <CategoryList
              model={MODEL}
              query={query}
              showExcluded={showExcluded}
              selected={selected}
              onSelect={setSelected}
            />
          </div>
          <div className="veta-detail">
            {selected && MODEL.classes.get(selected) ? (
              <ClassCard
                model={MODEL}
                cls={MODEL.classes.get(selected)!}
                onSelect={setSelected}
                onOpenSchema={onOpenSchema}
              />
            ) : (
              <p className="placeholder">Select a class to see its shape.</p>
            )}
          </div>
        </div>
      ) : (
        <TenetsText model={MODEL} onClass={openClass} />
      )}
    </div>
  );
}

// ---- denominator ----------------------------------------------------------

function Denominator({ model }: { model: VetaModel }) {
  const d = model.denominator;
  const warnings: ReactNode[] = [];
  const warn = (label: string, names: string[]) => {
    if (names.length)
      warnings.push(
        <li key={label}>
          <strong>{label}</strong> ({names.length}): {names.join(", ")}
        </li>,
      );
  };
  warn("in the tree but in no category", d.unplaced);
  warn("named by the final-set document but not in the tree", d.namedButNotBuilt);
  warn("named twice in the final-set document", d.placedTwice);
  warn("category heading count disagrees with its list", d.countMismatches);
  warn("categories missing from the final-set document", d.missingCategories);
  warn("tenets missing from the tenets document", d.missingTenets);
  warn("classes with no index.json entry", d.indexMissing);
  const tiers = Object.entries(d.classesByTier)
    .map(([t, n]) => `${n} ${t}`)
    .join(" · ");
  return (
    <>
      <div className="cov-stats">
        <Stat n={d.jsonFilesMatched} label="JSON files read" />
        <Stat n={d.classFiles} label={`classes (${tiers})`} />
        <Stat n={d.categorised} label="in the final set" />
        <Stat n={d.excluded} label="not in the final set" />
        <Stat n={d.tenetsParsed} label="tenets" />
        <Stat n={warnings.length} label="input disagreements" warn={warnings.length > 0} />
      </div>
      {warnings.length > 0 && (
        <div className="cov-gap-banner">
          The viewer's inputs disagree with each other — shown, not hidden:
          <ul>{warnings}</ul>
        </div>
      )}
    </>
  );
}

function Stat({ n, label, warn }: { n: number; label: string; warn?: boolean }) {
  return (
    <div className={`cov-stat ${warn ? "cov-stat-warn" : ""}`}>
      <span className="cov-stat-n">{n}</span>
      <span className="cov-stat-label">{label}</span>
    </div>
  );
}

// ---- categories -----------------------------------------------------------

function CategoryList({
  model,
  query,
  showExcluded,
  selected,
  onSelect,
}: {
  model: VetaModel;
  query: string;
  showExcluded: boolean;
  selected: string | null;
  onSelect: (n: string) => void;
}) {
  const q = query.trim().toLowerCase();
  const match = (n: string) => !q || n.toLowerCase().includes(q);
  const groups: Array<{ key: string; title: string; names: string[]; muted?: boolean }> =
    model.categories.map((c) => ({
      key: c.symbol,
      title: `${c.symbol} ${c.title}`,
      names: c.classes,
    }));
  if (model.denominator.unplaced.length)
    groups.push({
      key: "unplaced",
      title: "⚠ In the tree, in no category",
      names: model.denominator.unplaced,
    });
  if (showExcluded)
    for (const g of model.excluded)
      groups.push({
        key: `x-${g.disposition}`,
        title: `Not in the final set — ${g.disposition}`,
        names: g.classes,
        muted: true,
      });
  return (
    <>
      {groups.map((g) => {
        const names = g.names.filter(match);
        if (q && names.length === 0) return null;
        return (
          <section key={g.key} className={`veta-category ${g.muted ? "veta-muted" : ""}`}>
            <h3>
              {g.title} <span className="count-pill">{g.names.length}</span>
            </h3>
            <div className="veta-chips">
              {names.map((n) => {
                const c = model.classes.get(n);
                return (
                  <button
                    key={n}
                    type="button"
                    className={`veta-chip ${selected === n ? "veta-chip-on" : ""} ${
                      c ? "" : "veta-chip-missing"
                    } ${c?.abstract ? "veta-chip-abstract" : ""}`}
                    title={
                      c
                        ? `${n}${c.abstract ? " (abstract)" : ""} — ${c.path}`
                        : `${n} is named by the final-set document but is not in the tree`
                    }
                    onClick={() => c && onSelect(n)}
                    disabled={!c}
                  >
                    {n}
                  </button>
                );
              })}
            </div>
          </section>
        );
      })}
    </>
  );
}

// ---- one class ------------------------------------------------------------

function ClassRef({ name, onSelect }: { name: string; onSelect: (n: string) => void }) {
  return (
    <button type="button" className="md-class-link" onClick={() => onSelect(name)}>
      <code>{name}</code>
    </button>
  );
}

function ClassCard({
  model,
  cls,
  onSelect,
  onOpenSchema,
}: {
  model: VetaModel;
  cls: VetaClass;
  onSelect: (n: string) => void;
  onOpenSchema: (n: string) => void;
}) {
  const chain = useMemo(() => ancestors(model, cls.name), [model, cls.name]);
  const inherited = chain
    .map((a) => model.classes.get(a))
    .filter((a): a is VetaClass => !!a && (a.fields.length > 0 || a.dependsOn.length > 0));
  const category = model.categories.find((c) => c.symbol === cls.category);
  return (
    <article className="veta-card">
      <h3 className="veta-card-title">
        <code>{cls.name}</code>
        {cls.version && <span className="muted"> v{cls.version}</span>}
      </h3>
      <div className="veta-badges">
        <span className={`cov-badge maturity-${cls.maturity ?? "meta"}`}>
          {cls.maturity ?? cls.tier}
        </span>
        {cls.disposition && (
          <span className={`cov-badge cov-${cls.disposition === "in_progress" ? "wip" : cls.disposition}`}>
            {cls.disposition}
          </span>
        )}
        {cls.abstract && <span className="cov-badge veta-abstract">abstract</span>}
        {category && (
          <span className="cov-badge veta-category-badge">
            {category.symbol} {category.title}
          </span>
        )}
        {cls.excludedAs && (
          <span className="cov-badge cov-retire">not in final set ({cls.excludedAs})</span>
        )}
      </div>
      <dl className="kv-list veta-kv">
        <dt>file</dt>
        <dd>
          <code>{cls.path}</code>{" "}
          <button type="button" className="btn-secondary" onClick={() => onOpenSchema(cls.name)}>
            full schema view
          </button>
        </dd>
        <dt>superclasses</dt>
        <dd>
          {cls.superclasses.length === 0 ? (
            <span className="muted">none (a root)</span>
          ) : (
            cls.superclasses.map((s) => <ClassRef key={s} name={s} onSelect={onSelect} />)
          )}
          {chain.length > cls.superclasses.length && (
            <div className="muted veta-chain">
              full chain: {chain.join(" → ")}
            </div>
          )}
        </dd>
        <dt>subclasses</dt>
        <dd>
          {cls.subclasses.length === 0 ? (
            <span className="muted">none</span>
          ) : (
            cls.subclasses.map((s) => <ClassRef key={s} name={s} onSelect={onSelect} />)
          )}
        </dd>
        {cls.files.length > 0 && (
          <>
            <dt>files</dt>
            <dd>
              <code>{JSON.stringify(cls.files)}</code>
            </dd>
          </>
        )}
      </dl>

      <h4>depends_on ({cls.dependsOn.length})</h4>
      <DepsTable deps={cls.dependsOn} onSelect={onSelect} model={model} />

      <h4>fields ({cls.fields.length} declared here)</h4>
      <FieldsTable fields={cls.fields} model={model} onSelect={onSelect} />

      {inherited.length > 0 && (
        <details
          className="veta-inherited"
          // Open by default when the class declares nothing of its own -- an
          // empty card would otherwise read as an empty class.
          open={cls.fields.length === 0 && cls.dependsOn.length === 0}
        >
          <summary>
            inherited from {inherited.length} ancestor(s):{" "}
            {inherited
              .map((a) => `${a.name} (${a.fields.length} field(s), ${a.dependsOn.length} edge(s))`)
              .join(", ")}
          </summary>
          {inherited.map((a) => (
            <section key={a.name}>
              <h5>
                from <ClassRef name={a.name} onSelect={onSelect} />
              </h5>
              {a.dependsOn.length > 0 && (
                <DepsTable deps={a.dependsOn} onSelect={onSelect} model={model} />
              )}
              {a.fields.length > 0 && (
                <FieldsTable fields={a.fields} model={model} onSelect={onSelect} />
              )}
            </section>
          ))}
        </details>
      )}
    </article>
  );
}

function DepsTable({
  deps,
  model,
  onSelect,
}: {
  deps: RawDependency[];
  model: VetaModel;
  onSelect: (n: string) => void;
}) {
  if (deps.length === 0) return <p className="muted">none</p>;
  return (
    <table className="fields-table">
      <thead>
        <tr>
          <th>edge</th>
          <th>→ must refer to</th>
          <th>cardinality</th>
          <th>documentation</th>
        </tr>
      </thead>
      <tbody>
        {deps.map((d) => {
          const targets = refTargets(d);
          const card = [
            d.mustBeNonEmpty ? "required" : "optional",
            d.multiple ? "multiple" : null,
            d.min_count !== undefined || d.max_count !== undefined
              ? `[${d.min_count ?? 0}..${d.max_count ?? "∞"}]`
              : null,
          ]
            .filter(Boolean)
            .join(", ");
          return (
            <tr key={d.name}>
              <td className="field-name">
                <code>{d.name}</code>
              </td>
              <td>
                {targets.length === 0 ? (
                  <span className="muted">any</span>
                ) : (
                  targets.map((t) =>
                    model.classes.has(t) ? (
                      <ClassRef key={t} name={t} onSelect={onSelect} />
                    ) : (
                      <code key={t} title="not a class in the tree">
                        {t}
                      </code>
                    ),
                  )
                )}
              </td>
              <td>{card}</td>
              <td className="doc-cell">{d.documentation}</td>
            </tr>
          );
        })}
      </tbody>
    </table>
  );
}

// How a field's value is shaped: its type, scalar or array, required or not,
// and any constraint worth reading at a glance.
function valueShape(f: RawField): string {
  const parts = [f.mustBeScalar === false ? `${f.type}[]` : f.type];
  if (f.mustBeNonEmpty) parts.push("required");
  if (f.mustNotHaveNaN) parts.push("no NaN");
  return parts.join(" · ");
}

function FieldsTable({
  fields,
  model,
  onSelect,
}: {
  fields: RawField[];
  model: VetaModel;
  onSelect: (n: string) => void;
}) {
  if (fields.length === 0) return <p className="muted">none</p>;
  const rows: ReactNode[] = [];
  const walk = (fs: RawField[], depth: number, prefix: string) => {
    for (const f of fs) {
      const key = `${prefix}${f.name}`;
      const constraints = Object.entries(f.constraints ?? {});
      rows.push(
        <tr key={key}>
          <td className="field-name" style={{ paddingLeft: `${0.5 + depth * 1.1}rem` }}>
            {depth > 0 && <span className="field-tree-prefix">└ </span>}
            <code>{f.name}</code>
          </td>
          <td>
            <span className="type-badge">
              {model.classes.has(f.type) ? (
                <ClassRef name={f.type} onSelect={onSelect} />
              ) : (
                valueShape(f).split(" · ")[0]
              )}
            </span>{" "}
            <span className="muted">{valueShape(f).split(" · ").slice(1).join(" · ")}</span>
          </td>
          <td>
            {constraints.length === 0 ? (
              <span className="muted">—</span>
            ) : (
              constraints.map(([k, v]) => (
                <div key={k} className="constraints">
                  <span className="constraint-key">{k}</span>: <code>{JSON.stringify(v)}</code>
                </div>
              ))
            )}
          </td>
          <td className="doc-cell">{f.documentation}</td>
        </tr>,
      );
      if (f.fields?.length) walk(f.fields, depth + 1, `${key}.`);
    }
  };
  walk(fields, 0, "");
  return (
    <table className="fields-table">
      <thead>
        <tr>
          <th>field</th>
          <th>value shape</th>
          <th>constraints</th>
          <th>documentation</th>
        </tr>
      </thead>
      <tbody>{rows}</tbody>
    </table>
  );
}

// ---- tenets ---------------------------------------------------------------

function TenetsText({ model, onClass }: { model: VetaModel; onClass: (n: string) => void }) {
  const isClass = (n: string) => model.classes.has(n);
  const [before, after] = useMemo(() => {
    // Sections before "## The tenets" (the thesis) render above T1-T14; the
    // rest (the meta-principle) render below. Order is the document's own.
    const idx = TENETS_MD.search(/^### T1 /m);
    const b: typeof model.tenetSections = [];
    const a: typeof model.tenetSections = [];
    for (const s of model.tenetSections) {
      const at = TENETS_MD.indexOf(`## ${s.title}`);
      (at < idx ? b : a).push(s);
    }
    return [b, a];
  }, [model]);
  return (
    <div className="veta-tenets">
      <p className="section-note">
        Rendered from <code>schemas/V_eta_tenets.md</code> — {model.tenetsTitle}.
        Code spans naming a class in the tree link to it.
      </p>
      {model.tenetsPreamble && (
        <Markdown source={model.tenetsPreamble} isClass={isClass} onClass={onClass} />
      )}
      {before.map((s) => (
        <section key={s.title} className="veta-tenet">
          <h3>{s.title}</h3>
          <Markdown source={s.body} isClass={isClass} onClass={onClass} />
        </section>
      ))}
      <nav className="veta-tenet-index">
        {model.tenets.map((t) => (
          <a key={t.id} href={`#veta-${t.id}`} onClick={(e) => {
            e.preventDefault();
            document.getElementById(`veta-${t.id}`)?.scrollIntoView({ behavior: "smooth" });
          }}>
            {t.id}
          </a>
        ))}
      </nav>
      {model.tenets.map((t) => (
        <section key={t.id} id={`veta-${t.id}`} className="veta-tenet">
          <h3>
            <span className="veta-tenet-id">{t.id}</span> {t.title}
          </h3>
          <Markdown source={t.body} isClass={isClass} onClass={onClass} />
        </section>
      ))}
      {after.map((s) => (
        <section key={s.title} className="veta-tenet">
          <h3>{s.title}</h3>
          <Markdown source={s.body} isClass={isClass} onClass={onClass} />
        </section>
      ))}
    </div>
  );
}
