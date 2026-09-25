import { useEffect, useMemo, useState } from "react";
import type { ReactNode } from "react";
import { FINAL_CLASS_SET_MD, TENETS_MD, VETA_FILES, VETA_KEY_PREFIX } from "./sources";
import { ancestors, buildModel, refTargets } from "./model";
import type { RawDependency, RawField, VetaClass, VetaModel } from "./model";
import { InlineMarkdown, Markdown } from "./Markdown";
import { loadTenets } from "../schemaIndex";
import type { TenetRow, TenetsDoc } from "../types";

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
    // A class outside the final set is hidden by default; selecting one (from
    // a tenet, a card link) must still land on a visible node.
    if (MODEL.classes.get(name)?.excludedAs) setShowExcluded(true);
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
            Tenets T1–T15
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

  // How big each branch is, over what the tree is SHOWING (so the numbers move
  // with the filter and the final-set toggle). Distinct classes: a class under
  // several parents counts once per branch, so siblings' numbers need not add
  // up to their parent's.
  //   all    -- every class anywhere below
  //   leaves -- those below with nothing shown below them (terminal nodes)
  const branch = useMemo(() => {
    const memo = new Map<string, { all: Set<string>; leaves: Set<string> }>();
    const walk = (name: string, stack: Set<string>) => {
      const hit = memo.get(name);
      if (hit) return hit;
      const all = new Set<string>();
      const leaves = new Set<string>();
      stack.add(name);
      for (const k of model.classes.get(name)?.subclasses ?? []) {
        if (!visible.get(k) || stack.has(k)) continue;
        const sub = walk(k, stack);
        all.add(k);
        sub.all.forEach((x) => all.add(x));
        if (sub.all.size === 0) leaves.add(k);
        sub.leaves.forEach((x) => leaves.add(x));
      }
      stack.delete(name);
      const out = { all, leaves };
      memo.set(name, out);
      return out;
    };
    for (const r of roots) if (visible.get(r)) walk(r, new Set());
    return memo;
  }, [model, roots, visible]);

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
          {kids.length > 0 && (
            <span
              className="tree-folder-count"
              title={`${branch.get(name)?.all.size ?? 0} subclass(es) anywhere below; ${
                branch.get(name)?.leaves.size ?? 0
              } terminal node(s); ${kids.length} direct. A class with several parents counts under each.`}
            >
              {branch.get(name)?.all.size ?? 0}
            </span>
          )}
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
//
// Built for skimming, from the structure the document already has:
//   1. the 14 headings ARE one-line rules, so the tab opens as that list;
//   2. an opened tenet shows its opening text, then its bold lead-ins as a
//      collapsed outline (model.splitLeadIns) -- T13 reads as 8 sub-rules;
//   3. tenet numbers in the text link to the tenet; "(SPEC §n)" is dimmed;
//   4. each tenet lists the classes it shaped, from the tenet map
//      (web/public/tenets.json, tools/tenet_map.py), linked into the tree.
// Nothing is rewritten: every word shown is the document's own, re-grouped.

function words(s: string) {
  return s.split(/\s+/).filter(Boolean).length;
}

// "Litmus:" says nothing on its own, so a title that ends in a colon brings
// the first sentence of its body into the summary line.
function leadSentence(body: string): string {
  const m = /^(.+?[.?!])(\s|$)/s.exec(body.replace(/\s+/g, " "));
  return m ? m[1] : body;
}

function TenetsText({ model, onClass }: { model: VetaModel; onClass: (n: string) => void }) {
  const isClass = (n: string) => model.classes.has(n);
  const [open, setOpen] = useState<Set<string>>(new Set());
  const [openPoints, setOpenPoints] = useState<Set<string>>(new Set());
  const [pendingScroll, setPendingScroll] = useState<string | null>(null);
  const [map, setMap] = useState<TenetsDoc | null>(null);
  const [mapError, setMapError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    loadTenets()
      .then((d) => !cancelled && setMap(d))
      .catch((e) => !cancelled && setMapError(String(e)));
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    if (!pendingScroll) return;
    document.getElementById(`veta-${pendingScroll}`)?.scrollIntoView({ behavior: "smooth" });
    setPendingScroll(null);
  }, [pendingScroll, open]);

  const rowsByTenet = useMemo(() => {
    const m = new Map<string, TenetRow[]>();
    for (const r of map?.rows ?? []) {
      if (!m.has(r.tenet)) m.set(r.tenet, []);
      m.get(r.tenet)!.push(r);
    }
    return m;
  }, [map]);

  const [before, after] = useMemo(() => {
    // Sections before the first tenet (the thesis) render above T1-T15; the
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

  const toggle = (id: string) =>
    setOpen((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  const togglePoint = (key: string) =>
    setOpenPoints((prev) => {
      const next = new Set(prev);
      if (next.has(key)) next.delete(key);
      else next.add(key);
      return next;
    });
  // From a "T10" link in the text: open that tenet and bring it into view.
  const openTenet = (id: string) => {
    setOpen((prev) => new Set(prev).add(id));
    setPendingScroll(id);
  };
  const allPoints = () =>
    new Set(model.tenets.flatMap((t) => t.points.map((_, i) => `${t.id}:${i}`)));

  const md = (source: string) => (
    <Markdown source={source} isClass={isClass} onClass={onClass} onTenet={openTenet} />
  );

  return (
    <div className="veta-tenets">
      <p className="section-note">
        Rendered from <code>schemas/V_eta_tenets.md</code> — {model.tenetsTitle}. Every
        heading is a one-line rule; open one for its text. Class names link into the tree.
      </p>
      {before.map((s) => (
        <section key={s.title} className="veta-tenet-aside">
          <h3>{s.title}</h3>
          {md(s.body)}
        </section>
      ))}

      <div className="veta-tenet-toolbar">
        <button
          type="button"
          className="btn-secondary"
          onClick={() => {
            setOpen(new Set());
            setOpenPoints(new Set());
          }}
        >
          headlines only
        </button>
        <button
          type="button"
          className="btn-secondary"
          onClick={() => {
            setOpen(new Set(model.tenets.map((t) => t.id)));
            setOpenPoints(new Set());
          }}
        >
          open all tenets
        </button>
        <button
          type="button"
          className="btn-secondary"
          onClick={() => {
            setOpen(new Set(model.tenets.map((t) => t.id)));
            setOpenPoints(allPoints());
          }}
        >
          full text
        </button>
      </div>

      <ol className="veta-tenet-list">
        {model.tenets.map((t) => {
          const isOpen = open.has(t.id);
          const rows = rowsByTenet.get(t.id) ?? [];
          return (
            <li key={t.id} id={`veta-${t.id}`} className={`veta-tenet-item ${isOpen ? "is-open" : ""}`}>
              <button
                type="button"
                className="veta-tenet-head"
                aria-expanded={isOpen}
                onClick={() => toggle(t.id)}
              >
                <span className="veta-tenet-caret">{isOpen ? "▾" : "▸"}</span>
                <span className="veta-tenet-id">{t.id}</span>
                <span className="veta-tenet-title">
                  <InlineMarkdown source={t.title} />
                </span>
                <span className="veta-tenet-meta">
                  {t.points.length > 0
                    ? `${t.points.length} point${t.points.length === 1 ? "" : "s"} · `
                    : ""}
                  {words(t.body)} words
                </span>
              </button>
              {isOpen && (
                <div className="veta-tenet-body">
                  {t.intro && md(t.intro)}
                  {t.points.length > 0 && (
                    <ul className="veta-points">
                      {t.points.map((pt, i) => {
                        const key = `${t.id}:${i}`;
                        const po = openPoints.has(key);
                        return (
                          <li key={key} className={po ? "is-open" : ""}>
                            <button
                              type="button"
                              className="veta-point-head"
                              aria-expanded={po}
                              onClick={() => togglePoint(key)}
                            >
                              <span className="veta-tenet-caret">{po ? "▾" : "▸"}</span>
                              <span>
                                <strong>
                                  <InlineMarkdown source={pt.title} />
                                </strong>
                                {pt.title.endsWith(":") && !po && (
                                  <span className="veta-point-lead">
                                    {" "}
                                    <InlineMarkdown source={leadSentence(pt.body)} />
                                  </span>
                                )}
                              </span>
                            </button>
                            {po && <div className="veta-point-body">{md(pt.body)}</div>}
                          </li>
                        );
                      })}
                    </ul>
                  )}
                  <TenetClasses
                    rows={rows}
                    model={model}
                    onClass={onClass}
                    error={mapError}
                    loaded={!!map}
                  />
                </div>
              )}
            </li>
          );
        })}
      </ol>

      {after.map((s) => (
        <section key={s.title} className="veta-tenet-aside">
          <h3>{s.title}</h3>
          {md(s.body)}
        </section>
      ))}
    </div>
  );
}

// The classes a tenet shaped, from the curated, cited tenet map. A chip links
// into the class tree when the class is in the tree; a decided-but-unbuilt
// target is drawn dashed so it cannot read as shipped.
function TenetClasses({
  rows,
  model,
  onClass,
  error,
  loaded,
}: {
  rows: TenetRow[];
  model: VetaModel;
  onClass: (n: string) => void;
  error: string | null;
  loaded: boolean;
}) {
  if (error)
    return <p className="muted veta-tenet-classes">Class map unavailable: {error}</p>;
  if (!loaded) return <p className="muted veta-tenet-classes">Loading the class map…</p>;
  if (rows.length === 0)
    return (
      <p className="muted veta-tenet-classes">
        No cited class mapping is recorded for this tenet (tools/tenet_map.py).
      </p>
    );
  const chip = (c: string, unbuilt: boolean) =>
    model.classes.has(c) ? (
      <button key={c} type="button" className="veta-chip" onClick={() => onClass(c)} title={`Open ${c} in the tree`}>
        {c}
      </button>
    ) : (
      <span
        key={c}
        className={`veta-chip veta-chip-static ${unbuilt ? "veta-chip-unbuilt" : ""}`}
        title={unbuilt ? `${c}: decided, not built` : `${c}: a did_v1 name, not a V_eta class`}
      >
        {c}
      </span>
    );
  return (
    <div className="veta-tenet-classes">
      <div className="veta-tenet-classes-head">Classes this tenet shaped</div>
      {rows.map((r, i) => (
        <div key={i} className="veta-tenet-class-row">
          <div className="veta-tenet-change">
            <InlineMarkdown source={r.change} />
          </div>
          <div className="veta-tenet-ba">
            {r.before.length > 0 && (
              <>
                <span className="veta-ba-label">did_v1</span>
                {r.before.map((c) => chip(c, false))}
                <span className="veta-ba-arrow">→</span>
              </>
            )}
            <span className="veta-ba-label">V_eta</span>
            {r.after.map((c) => chip(c, r.after_not_built.includes(c)))}
          </div>
          <div className="veta-tenet-cite" title={r.citation.quote}>
            source: <code>{r.citation.doc}</code>:{r.citation.line}
          </div>
        </div>
      ))}
    </div>
  );
}
