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
  // Open nodes, by path key. The root starts open so the first level shows.
  const [expanded, setExpanded] = useState<Set<string>>(
    () => new Set([...MODEL.classes.values()].filter((c) => !c.superclasses.length).map((c) => c.name)),
  );

  const toggle = (key: string) =>
    setExpanded((prev) => {
      const next = new Set(prev);
      if (next.has(key)) next.delete(key);
      else next.add(key);
      return next;
    });

  // Select a class and open the tree down to it (along its first superclass),
  // so a class reached from a card link or a tenet is visible in the tree.
  const select = (name: string) => {
    setSelected(name);
    setExpanded((prev) => {
      const next = new Set(prev);
      for (const k of pathKeys(MODEL, name).slice(0, -1)) next.add(k);
      return next;
    });
  };

  const expandAll = () => {
    const all = new Set<string>();
    const walk = (name: string, key: string, seen: Set<string>) => {
      const c = MODEL.classes.get(name);
      if (!c || seen.has(name) || !c.subclasses.length) return;
      all.add(key);
      seen.add(name);
      for (const k of c.subclasses) walk(k, `${key}${SEP}${k}`, seen);
      seen.delete(name);
    };
    for (const c of MODEL.classes.values())
      if (!c.superclasses.length) walk(c.name, c.name, new Set());
    setExpanded(all);
  };

  const openClass = (name: string) => {
    select(name);
    setTab("classes");
  };

  return (
    <div className="detail veta">
      <header className="detail-header">
        <h2>V_eta schema shape</h2>
        <p className="registry-description">
          The go-forward V_eta class set, rendered directly from{" "}
          <code>schemas/V_eta/</code> at build time as an inheritance tree from{" "}
          <code>base</code>. Nothing here is copied in: edit a schema, rebuild,
          and this page follows.
        </p>
        <Denominator model={MODEL} />
        <div className="view-toggle veta-tabs" role="tablist">
          <button
            role="tab"
            aria-selected={tab === "classes"}
            className={tab === "classes" ? "active" : ""}
            onClick={() => setTab("classes")}
          >
            Class tree
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
            <div className="veta-tree-actions">
              <button type="button" className="btn-secondary" onClick={expandAll}>
                expand all
              </button>
              <button type="button" className="btn-secondary" onClick={() => setExpanded(new Set())}>
                collapse all
              </button>
            </div>
            <ClassTree
              model={MODEL}
              query={query}
              showExcluded={showExcluded}
              selected={selected}
              expanded={expanded}
              onToggle={toggle}
              onSelect={select}
            />
          </div>
          <div className="veta-detail">
            {selected && MODEL.classes.get(selected) ? (
              <ClassCard
                model={MODEL}
                cls={MODEL.classes.get(selected)!}
                onSelect={select}
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

// ---- the class tree -------------------------------------------------------
//
// Classes are drawn by inheritance, starting from the tree's roots (in V_eta,
// only `base`). A class with several superclasses -- most leaves are
// `<direction>_observation` + `<data_type>` -- appears under EACH parent, and
// says where else it sits, so no parent looks childless.
//
// A node's key is its path from the root ("base/data/subject_statement"),
// because the same class can be open under one parent and closed under another.

const SEP = "/";

// The first-superclass path from a root down to `name`, as the keys of every
// node on it. Used to open the tree onto a class selected from elsewhere.
function pathKeys(model: VetaModel, name: string): string[] {
  const chain = [name];
  const seen = new Set(chain);
  let cur = model.classes.get(name);
  while (cur && cur.superclasses.length) {
    const up = cur.superclasses[0];
    if (seen.has(up)) break;
    seen.add(up);
    chain.unshift(up);
    cur = model.classes.get(up);
  }
  return chain.map((_, i) => chain.slice(0, i + 1).join(SEP));
}

function ClassTree({
  model,
  query,
  showExcluded,
  selected,
  expanded,
  onToggle,
  onSelect,
}: {
  model: VetaModel;
  query: string;
  showExcluded: boolean;
  selected: string | null;
  expanded: Set<string>;
  onToggle: (key: string) => void;
  onSelect: (n: string) => void;
}) {
  const q = query.trim().toLowerCase();
  const roots = useMemo(
    () =>
      [...model.classes.values()]
        .filter((c) => c.superclasses.length === 0)
        .map((c) => c.name)
        .sort(),
    [model],
  );

  // Does this class, or anything below it, pass the filters? Memoised per
  // class: the answer does not depend on which parent it is reached through.
  const visible = useMemo(() => {
    const memo = new Map<string, boolean>();
    const self = (c: VetaClass) =>
      (showExcluded || !c.excludedAs) && (!q || c.name.toLowerCase().includes(q));
    const walk = (name: string, stack: Set<string>): boolean => {
      if (memo.has(name)) return memo.get(name)!;
      const c = model.classes.get(name);
      if (!c || stack.has(name)) return false;
      stack.add(name);
      const kids = c.subclasses.map((k) => walk(k, stack)).some(Boolean);
      stack.delete(name);
      const v = self(c) || kids;
      memo.set(name, v);
      return v;
    };
    for (const r of roots) walk(r, new Set());
    return memo;
  }, [model, roots, q, showExcluded]);

  const matches = (c: VetaClass) =>
    (showExcluded || !c.excludedAs) && (!q || c.name.toLowerCase().includes(q));

  const render = (name: string, parentKey: string, depth: number): ReactNode => {
    const c = model.classes.get(name);
    if (!c || !visible.get(name)) return null;
    const key = parentKey ? `${parentKey}${SEP}${name}` : name;
    if (parentKey.split(SEP).includes(name)) return null; // cycle guard
    const kids = c.subclasses.filter((k) => visible.get(k));
    // While filtering, every path to a match is open.
    const open = q ? true : expanded.has(key);
    const parent = parentKey.split(SEP).pop();
    const others = c.superclasses.filter((s) => s !== parent);
    return (
      <li key={key}>
        <div className="veta-tree-row" style={{ paddingLeft: `${depth * 1.1}rem` }}>
          {kids.length > 0 ? (
            <button
              type="button"
              className="tree-caret"
              aria-label={open ? "collapse" : "expand"}
              aria-expanded={open}
              onClick={() => onToggle(key)}
            >
              {open ? "▾" : "▸"}
            </button>
          ) : (
            <span className="tree-caret tree-caret-empty" />
          )}
          <button
            type="button"
            className={`veta-chip ${selected === name ? "veta-chip-on" : ""} ${
              c.abstract ? "veta-chip-abstract" : ""
            } ${matches(c) ? "" : "veta-chip-dim"}`}
            title={`${name}${c.abstract ? " (abstract)" : ""} -- ${c.path}`}
            onClick={() => onSelect(name)}
          >
            {name}
          </button>
          {kids.length > 0 && <span className="tree-folder-count">{kids.length}</span>}
          {c.disposition && c.disposition !== "persist" && (
            <span className={`veta-dot cov-${c.disposition === "in_progress" ? "wip" : c.disposition}`}>
              {c.disposition === "in_progress" ? "wip" : c.disposition}
            </span>
          )}
          {others.length > 0 && parentKey && (
            <span className="veta-also" title={`superclasses: ${c.superclasses.join(", ")}`}>
              also ⊂ {others.join(", ")}
            </span>
          )}
        </div>
        {open && kids.length > 0 && (
          <ul className="veta-tree">{kids.map((k) => render(k, key, depth + 1))}</ul>
        )}
      </li>
    );
  };

  const shown = roots.filter((r) => visible.get(r));
  if (shown.length === 0) return <p className="muted">No class matches.</p>;
  return <ul className="veta-tree">{shown.map((r) => render(r, "", 0))}</ul>;
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
