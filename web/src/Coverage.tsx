import { useEffect, useMemo, useState } from "react";
import type {
  CoverageLedger,
  CoverageRow,
  DecisionFamily,
  DecisionState,
  DecisionsDoc,
} from "./types";
import { loadCoverage, loadDecisions } from "./schemaIndex";

interface Props {
  // Jump to a class's detail view (used by the clickable V_eta class chip).
  onSelect: (className: string) => void;
}

const DASH = "—";

// Coarse category for a row, used for both the badge style and the filter chips.
// The generated ledger puts settled classes on `persist`/`retire`/`in_progress`
// and everything else on a descriptive string ("UNMAPPED ...", "dissolved ...",
// "test/demo ..."), so key off the structured flags first, then the disposition.
type Kind = "persist" | "retire" | "in_progress" | "dissolved" | "unmapped" | "nonprod";

function kindOf(r: CoverageRow): Kind {
  if (r.gap) return "unmapped";
  if (r.nonprod) return "nonprod";
  if (r.disposition === "persist") return "persist";
  if (r.disposition === "retire") return "retire";
  if (r.disposition === "in_progress") return "in_progress";
  return "dissolved";
}

const KIND_META: Record<Kind, { label: string; cls: string; tip: string }> = {
  persist: { label: "persist", cls: "cov-persist", tip: "settled go-forward V_eta class" },
  retire: { label: "retire", cls: "cov-retire", tip: "carried but dissolving; not in final set" },
  in_progress: { label: "in progress", cls: "cov-wip", tip: "carried; ⑥/⑦ disposition not finalized" },
  dissolved: { label: "dissolved", cls: "cov-dissolved", tip: "folded into another class by rename/decomposition" },
  unmapped: { label: "unmapped", cls: "cov-gap", tip: "no V_eta home, no migrator, never reviewed — an actionable hole" },
  nonprod: { label: "test/demo", cls: "cov-nonprod", tip: "NDI test/demo scaffolding, not real corpus data" },
};

const KIND_ORDER: Kind[] = [
  "unmapped", "in_progress", "retire", "persist", "dissolved", "nonprod",
];

// Decision-state styling. The ledger's `fate` says what happens to a class;
// this says whether the MODEL behind it has been decided. A class showing
// `in_progress` with no decision marker used to be indistinguishable from one
// nobody had thought about -- which is how a signed cluster sat unbuilt for a
// day while two documents called it a proposal.
const DSTATE_META: Record<DecisionState, { label: string; cls: string; tip: string }> = {
  signed_awaiting_build: {
    label: "decided ✓ awaiting build",
    cls: "cov-dec-signed",
    tip: "The team decided this and the plan document carries a TEAM-SIGN-OFF line. The model is settled; only the build is outstanding.",
  },
  awaiting_signature: {
    label: "decided — unsigned",
    cls: "cov-dec-unsigned",
    tip: "Decided in a walkthrough, but no TEAM-SIGN-OFF line in the plan yet. Nothing here needs re-deciding — it needs recording.",
  },
  proposed_unreviewed: {
    label: "proposed — unreviewed",
    cls: "cov-dec-proposed",
    tip: "Written up by Claude alone. NOT a decision and never counted as one.",
  },
  open: {
    label: "no proposal",
    cls: "cov-dec-open",
    tip: "Nobody has proposed anything for this family yet.",
  },
};

export function Coverage({ onSelect }: Props) {
  const [led, setLed] = useState<CoverageLedger | null>(null);
  const [dec, setDec] = useState<DecisionsDoc | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [q, setQ] = useState("");
  const [activeKinds, setActiveKinds] = useState<Set<Kind>>(new Set(KIND_ORDER));
  const [source, setSource] = useState<"all" | "ndi" | "app">("all");

  useEffect(() => {
    let cancelled = false;
    loadCoverage()
      .then((l) => !cancelled && setLed(l))
      .catch((e) => !cancelled && setError(String(e)));
    // Non-fatal: an older bundle may have no decisions.json, and the ledger is
    // still worth showing without it. Failing the whole panel would trade a
    // partial view for none.
    loadDecisions()
      .then((d) => !cancelled && setDec(d))
      .catch(() => undefined);
    return () => {
      cancelled = true;
    };
  }, []);

  const toggleKind = (k: Kind) =>
    setActiveKinds((prev) => {
      const next = new Set(prev);
      if (next.has(k)) next.delete(k);
      else next.add(k);
      return next;
    });

  // A ledger row is keyed by its v1 SOURCE class; families are keyed by V_eta
  // class names. Join on the V_eta side, falling back to the v1 name for the
  // classes that migrate 1:1 keeping their name.
  const famOf = useMemo(() => {
    if (!dec) return () => undefined as DecisionFamily | undefined;
    const byName = new Map(dec.families.map((f) => [f.name, f]));
    return (r: CoverageRow): DecisionFamily | undefined => {
      const key = (r.veta_class && dec.by_class[r.veta_class])
        ?? dec.by_class[r.v1_class];
      return key ? byName.get(key) : undefined;
    };
  }, [dec]);

  const rows = led?.rows ?? [];
  const kindCounts = useMemo(() => {
    const c = {} as Record<Kind, number>;
    for (const k of KIND_ORDER) c[k] = 0;
    for (const r of rows) c[kindOf(r)]++;
    return c;
  }, [rows]);

  const filtered = useMemo(() => {
    const needle = q.trim().toLowerCase();
    return rows.filter((r) => {
      if (!activeKinds.has(kindOf(r))) return false;
      if (source !== "all" && r.source !== source) return false;
      if (needle) {
        const hay = `${r.v1_class} ${r.veta_class ?? ""} ${r.disposition}`.toLowerCase();
        if (!hay.includes(needle)) return false;
      }
      return true;
    });
  }, [rows, activeKinds, source, q]);

  if (error) {
    return (
      <div className="detail">
        <div className="detail-error">
          Could not load coverage ledger: {error}
          <p className="section-note">
            It is generated by <code>tools/coverage.py</code> and copied to{" "}
            <code>public/coverage.json</code> by <code>npm run sync-schemas</code>.
          </p>
        </div>
      </div>
    );
  }
  if (!led) return <div className="detail-loading">Loading coverage ledger…</div>;

  const s = led.summary;

  return (
    <div className="detail coverage">
      <header className="detail-header">
        <h2>{led.title}</h2>
        <p className="registry-description">{led.description}</p>
        <div className="cov-stats">
          <Stat n={s.total} label="v1 source classes" />
          <Stat n={s.by_source.ndi ?? 0} label="NDI / main" />
          <Stat n={s.by_source.app ?? 0} label="vhlab app" />
          <Stat n={s.with_migrator} label="bespoke migrator" />
          <Stat n={s.gaps} label="unmapped" warn={s.gaps > 0} />
        </div>
        {dec && (
          <p className="cov-decision-banner">
            <strong>{dec.summary.families} decision families</strong> cover{" "}
            {dec.summary.open_classes} still-open classes.{" "}
            {dec.summary.by_state.signed_awaiting_build} are decided, signed off and{" "}
            <strong>awaiting build</strong>
            {dec.summary.by_state.awaiting_signature > 0 &&
              `, ${dec.summary.by_state.awaiting_signature} await a signature`}
            {dec.summary.by_state.proposed_unreviewed > 0 &&
              `, ${dec.summary.by_state.proposed_unreviewed} are unreviewed proposals`}
            {dec.summary.by_state.open > 0 &&
              `, ${dec.summary.by_state.open} have no proposal`}
            . A class marked <em>in progress</em> below is not necessarily
            undecided — check its <strong>decision</strong> column.
          </p>
        )}
        {s.gaps > 0 && (
          <p className="cov-gap-banner">
            ⚠ {s.gaps} class{s.gaps === 1 ? "" : "es"} on NDI/main have no V_eta home
            yet — filter to <strong>unmapped</strong> below to see them.
          </p>
        )}
      </header>

      <div className="cov-controls">
        <input
          className="cov-search"
          type="search"
          placeholder="Filter by class name…"
          value={q}
          onChange={(e) => setQ(e.target.value)}
        />
        <div className="cov-kind-chips" role="group" aria-label="Filter by fate">
          {KIND_ORDER.map((k) => {
            const on = activeKinds.has(k);
            const m = KIND_META[k];
            return (
              <button
                key={k}
                type="button"
                className={`cov-chip ${m.cls} ${on ? "" : "cov-chip-off"}`}
                aria-pressed={on}
                title={`${m.tip} — click to ${on ? "hide" : "show"}`}
                onClick={() => toggleKind(k)}
              >
                {m.label} <span className="cov-chip-n">{kindCounts[k]}</span>
              </button>
            );
          })}
        </div>
        <div className="cov-source-toggle" role="group" aria-label="Filter by writer">
          {(["all", "ndi", "app"] as const).map((sv) => (
            <button
              key={sv}
              type="button"
              className={source === sv ? "active" : ""}
              onClick={() => setSource(sv)}
              title={
                sv === "ndi"
                  ? "NDI production templates"
                  : sv === "app"
                    ? "vhlab app/calculator classes (no NDI template)"
                    : "both writers"
              }
            >
              {sv === "all" ? "all writers" : sv === "ndi" ? "NDI" : "vhlab app"}
            </button>
          ))}
        </div>
      </div>

      <p className="section-note">
        Showing {filtered.length} of {rows.length}. The{" "}
        <strong>→ V_eta target(s)</strong> column lists the V_eta document class(es)
        each v1 class migrates into (click a chip to open it). A{" "}
        <span className="cov-target-2pass enum-chip">class✦</span> is minted in the
        NDI second pass; <em>· on</em> <span className="cov-target-carried enum-chip">
        subject</span> is the pre-existing class the statements attach to; ⓘ marks a
        caveat (dynamic emit / deferral).
      </p>

      <table className="fields-table cov-table">
        <thead>
          <tr>
            <th>v1 class</th>
            <th>→ V_eta target(s)</th>
            <th>fate</th>
            <th>decision</th>
            <th>migrator</th>
            <th>writer</th>
          </tr>
        </thead>
        <tbody>
          {filtered.map((r) => {
            const kind = kindOf(r);
            const m = KIND_META[kind];
            return (
              <tr key={r.v1_class} className={r.gap ? "cov-row-gap" : ""}>
                <td>
                  <code>{r.v1_class}</code>
                </td>
                <td>
                  <TargetCell row={r} onSelect={onSelect} />
                </td>
                <td>
                  <span className={`cov-badge ${m.cls}`} title={m.tip}>
                    {m.label}
                  </span>
                  {kind === "dissolved" && r.disposition.includes("→") && (
                    <span className="cov-dissolved-target">
                      {" "}
                      {r.disposition.replace(/^dissolved\s*/, "")}
                    </span>
                  )}
                </td>
                <td>
                  <DecisionCell fam={famOf(r)} />
                </td>
                <td>
                  {r.migrator ? (
                    <span className="cov-yes">yes</span>
                  ) : (
                    <span className="muted">{DASH}</span>
                  )}
                </td>
                <td>
                  <span className="cov-writer">{r.source === "app" ? "vhlab" : "NDI"}</span>
                </td>
              </tr>
            );
          })}
          {filtered.length === 0 && (
            <tr>
              <td colSpan={6} className="muted">
                No classes match the current filters.
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}

// The decision cell. Deliberately EMPTY when a class belongs to no decision
// family: most classes are settled and need no marker, and painting every row
// would bury the 18 that are actually in flight.
function DecisionCell({ fam }: { fam: DecisionFamily | undefined }) {
  if (!fam) return <span className="muted">{DASH}</span>;
  const m = DSTATE_META[fam.state];
  const tip = [
    `${fam.name}: ${fam.decision}`,
    "",
    m.tip,
    fam.signoff ? `\nTEAM-SIGN-OFF: ${fam.signoff}` : "",
    fam.plan ? `\nRecorded in ${fam.plan}` : "",
  ]
    .filter(Boolean)
    .join("\n");
  return (
    <span className={`cov-badge ${m.cls}`} title={tip}>
      {m.label}
    </span>
  );
}

// The migration-target cell: the V_eta class(es) the migrator emits, as clickable
// chips. Second-pass classes carry a ✦ marker; carried (pre-existing) classes are
// shown after "· on"; the authored "how" + caveats are a tooltip on the row.
function TargetCell({
  row,
  onSelect,
}: {
  row: CoverageRow;
  onSelect: (c: string) => void;
}) {
  const chip = (c: string, cls: string, marker?: string, key?: string) => (
    <button
      key={key ?? c}
      className={`cov-link enum-chip ${cls}`}
      onClick={() => onSelect(c)}
      title={`Open ${c}`}
    >
      {c}
      {marker}
    </button>
  );
  const empty = row.targets.length === 0 && row.second_pass.length === 0;
  if (empty) {
    return row.gap ? (
      <span className="cov-badge cov-gap">unmapped</span>
    ) : (
      <span className="muted">{DASH}</span>
    );
  }
  return (
    <span className="cov-targets" title={row.how || undefined}>
      {row.targets.map((t) => chip(t, "cov-target-emit"))}
      {row.second_pass.map((t) => chip(t, "cov-target-2pass", "✦", "2p-" + t))}
      {row.carried.length > 0 && (
        <span className="cov-carried">
          {" · on "}
          {row.carried.map((c) => chip(c, "cov-target-carried", undefined, "c-" + c))}
        </span>
      )}
      {row.target_flags && (
        <span className="cov-target-flag" title={row.target_flags}>
          ⓘ
        </span>
      )}
    </span>
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
