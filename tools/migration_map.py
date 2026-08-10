#!/usr/bin/env python3
"""One page that answers "what happens to this v1 class?" for all 102 of them.

WHY THIS EXISTS
---------------
Everything needed to answer that question already existed, spread across three
generated artifacts and fifty-four plan documents. What did not exist was one
place a person could open and read down. The cost of that was not abstract: the
question "what happens to every v1 class?" could not be answered for a team
without a git checkout and an afternoon.

So this joins what is already generated -- it invents nothing:

    V_eta_coverage_ledger.json    one row per v1 SOURCE class: disposition,
                                  targets, and (for 65 of them) a curated
                                  one-line `how`
    V_eta_decisions.json          the 18 decision families, their members, and
                                  the TEAM-SIGN-OFF text for each
    V_eta_migration_targets.json  the curated source -> target map the ledger
                                  reads (used here only for its provenance note)

EVERY ROW STATES WHERE ITS ANSWER CAME FROM. That is the whole point. A class
gets one of three provenances, and they are not interchangeable:

    per-class   a curated one-liner written for THIS class, in
                V_eta_migration_targets.json, cross-checked against the migrator
    family      no per-class line, but the class belongs to a decision family
                whose TEAM-SIGN-OFF covers it -- the answer is real but stated at
                family granularity
    none        no per-class line and no signed family. These are the genuine
                gaps, and the page says so rather than rendering silence as calm

A page that showed only the first bucket would look finished and be a lie. A page
that merged all three would hide which answers are specific and which are
inherited. So the bucket is the primary structure of the document.

Usage:  python3 tools/migration_map.py            # writes the HTML
        python3 tools/migration_map.py --check    # fails if it is stale
"""

import argparse
import html
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
SCHEMAS = os.path.join(REPO, "schemas")
LEDGER = os.path.join(SCHEMAS, "V_eta_coverage_ledger.json")
TARGETS = os.path.join(SCHEMAS, "V_eta_migration_targets.json")
DECISIONS = os.path.join(SCHEMAS, "V_eta_decisions.json")
OUT = os.path.join(SCHEMAS, "V_eta_migration_map.html")


def load():
    with open(LEDGER, encoding="utf-8") as fh:
        led = json.load(fh)
    rows = led["rows"] if isinstance(led, dict) and "rows" in led else led
    with open(DECISIONS, encoding="utf-8") as fh:
        dec = json.load(fh)
    # `decided_targets` lives in the curated map, NOT the ledger, and that is
    # deliberate: coverage.py must never read a decided target as an emitted one
    # (test_no_passthrough_row_claims_a_migrator_emits_it exists to stop exactly
    # that). This page can show both, as long as it labels which is which.
    with open(TARGETS, encoding="utf-8") as fh:
        tgt = json.load(fh).get("classes", {})
    return rows, dec, tgt


def family_index(dec):
    """class_name -> (family name, state label, signoff text)."""
    idx = {}
    for fam in dec.get("families", []):
        for m in fam.get("members", []):
            cn = m.get("class_name")
            if cn:
                idx[cn] = (fam.get("name"), fam.get("state_label") or fam.get("state"),
                           fam.get("signoff") or "", fam.get("decision") or "")
    return idx


def classify(rows, fams, tgt):
    """Assign each v1 class its provenance bucket. Returns (buckets, counts)."""
    out = []
    for r in rows:
        v1 = r["v1_class"]
        how = (r.get("how") or "").strip()
        # A class is matched to a family by EITHER spelling: the ledger keys on
        # the did_v1 name (camelCase for NDI classes) while the families were
        # written against V_eta names (snake_case). Checking only one silently
        # drops rows into "no decision" -- the demo_ndi/demoNDI failure again.
        fam = fams.get(v1) or fams.get(r.get("veta_class") or "")
        if how:
            prov = "per-class"
        elif fam:
            prov = "family"
        else:
            prov = "none"
        out.append({
            "v1": v1,
            "veta": r.get("veta_class") or "",
            "disposition": r.get("disposition") or "",
            "targets": r.get("targets") or [],
            "carried": r.get("carried") or [],
            "second_pass": r.get("second_pass") or [],
            "decided_targets": (tgt.get(r["v1_class"], {}) or {}).get("decided_targets") or [],
            "how": how,
            "flags": (r.get("target_flags") or "").strip(),
            "migrator": bool(r.get("migrator")),
            "source": r.get("source") or "",
            "family": fam[0] if fam else "",
            "family_state": fam[1] if fam else "",
            "signoff": fam[2] if fam else "",
            "prov": prov,
        })
    out.sort(key=lambda d: d["v1"].lower())
    counts = {
        "total": len(out),
        "per-class": sum(1 for d in out if d["prov"] == "per-class"),
        "family": sum(1 for d in out if d["prov"] == "family"),
        "none": sum(1 for d in out if d["prov"] == "none"),
        "migrator": sum(1 for d in out if d["migrator"]),
    }
    return out, counts


E = html.escape


def chip(text, kind):
    return '<span class="chip chip--%s">%s</span>' % (kind, E(text))


def render_row(d):
    targets = d["targets"]
    if targets:
        becomes = " + ".join('<code>%s</code>' % E(t) for t in targets)
    elif d["second_pass"]:
        becomes = ("<em>deferred to the NDI second pass &rarr;</em> "
                   + " + ".join('<code>%s</code>' % E(t) for t in d["second_pass"]))
    elif d["decided_targets"]:
        # "WILL BECOME", never "becomes". These come from `decided_targets` in the
        # curated map -- a signed decision that no migrator implements yet -- and
        # rendering them in the same voice as an emitted target is precisely how a
        # migration reads as further along than it is.
        becomes = ('<span class="willbe">will become</span> '
                   + " + ".join('<code>%s</code>' % E(t) for t in d["decided_targets"]))
    else:
        becomes = '<em class="muted">no target recorded</em>'

    if d["prov"] == "per-class":
        account = E(d["how"])
        note = chip("per-class account", "ok")
    # BUILD STATE IS SEPARATE FROM ANSWER QUALITY. A class can have a precise,
    # signed account and no migrator at all -- 30 of them do. Rendering those two
    # as one status is exactly the "looks further along than it is" error the
    # operating rules exist to prevent, so the build state gets its own chip on
    # every row, driven by the ledger's `migrator` flag rather than by prose.
    elif d["prov"] == "family":
        account = ('<span class="muted">No per-class summary written yet. '
                   'The signed decision for the <strong>%s</strong> family covers it:</span>'
                   '<blockquote>%s</blockquote>'
                   % (E(d["family"]), E(d["signoff"][:600])))
        note = chip("family decision: %s" % d["family"], "warn")
    else:
        account = ('<span class="muted">No per-class summary and no signed decision '
                   'family. This is a real gap, not a formatting one.</span>')
        note = chip("no decision recorded", "open")

    build = (chip("migrator exists", "ok") if d["migrator"]
             else chip("no migrator yet", "warn"))

    extra = ""
    if d["carried"]:
        extra += ('<div class="sub"><span class="k">attaches to</span> '
                  + " ".join('<code>%s</code>' % E(c) for c in d["carried"]) + "</div>")
    if d["second_pass"] and targets:
        extra += ('<div class="sub"><span class="k">second pass adds</span> '
                  + " ".join('<code>%s</code>' % E(c) for c in d["second_pass"]) + "</div>")
    if d["flags"]:
        extra += '<div class="sub sub--flag"><span class="k">caveat</span> %s</div>' % E(d["flags"])

    return """
    <article class="row" data-prov="%s" data-name="%s">
      <div class="row__id">
        <h3><code>%s</code></h3>
        <div class="row__meta">%s%s%s</div>
      </div>
      <div class="row__body">
        <div class="becomes"><span class="k">%s</span> %s</div>
        <div class="account">%s</div>
        %s
      </div>
    </article>""" % (
        d["prov"],
        E((d["v1"] + " " + d["veta"] + " " + " ".join(d["targets"])).lower()),
        E(d["v1"]),
        chip(d["disposition"], "plain"),
        note,
        build,
        "today" if (d["targets"] or d["second_pass"]) else "decided",
        becomes,
        account,
        extra,
    )


BUCKETS = [
    ("per-class", "Answered class by class",
     "A one-line account written for this class specifically. THE ACCOUNT AND THE "
     "BUILD ARE TWO DIFFERENT THINGS, and the second chip on every row says which "
     "you are looking at: \u201cmigrator exists\u201d means code implements this "
     "today; \u201cno migrator yet\u201d means the account states a signed "
     "decision that has not been built. Both are real answers to \u201cwhat "
     "happens to this class\u201d; only one of them is running."),
    ("family", "Decided, but only at family granularity",
     "The team has signed a decision that covers these classes; nobody has yet "
     "written the one-line per-class summary. The decision is real — the "
     "sign-off text is reproduced on every row — but a reader has to do the "
     "translation from family to class themselves. This is the gap that makes "
     "the question hard to answer quickly, and closing it is writing, not deciding."),
    ("none", "No decision on record",
     "No per-class account and no signed decision family. READ THE DISPOSITION "
     "CHIP ON EACH ROW BEFORE READING THIS AS ALARM \u2014 the group is not "
     "uniform. `base` and `session` persist unchanged and need no decision; "
     "three are NDI\u2019s own test/demo scaffolding; `animalsubject` dissolved "
     "into `subject` before this work began. The ones that genuinely strand today "
     "are the three marked UNVERIFIED: `generic_file`, `imageCollection` and "
     "`valid_interval` \u2014 each has no V_eta home and no migrator, and two of "
     "the three have live production writers in NDI."),
]


def render(rows, counts, dec):
    signed = sum(1 for f in dec.get("families", []) if f.get("state") == "signed_awaiting_build")
    famtotal = len(dec.get("families", []))

    sections = []
    for key, title, blurb in BUCKETS:
        group = [d for d in rows if d["prov"] == key]
        sections.append("""
    <section class="bucket" id="bucket-%s">
      <header class="bucket__head">
        <h2>%s</h2>
        <p class="bucket__count"><strong>%d</strong> of %d classes</p>
        <p class="bucket__blurb">%s</p>
      </header>
      %s
    </section>""" % (key, E(title), len(group), counts["total"], E(blurb),
                     "\n".join(render_row(d) for d in group) or
                     '<p class="muted">None.</p>'))

    page = """<title>What happens to every v1 class</title>
<style>
:root {
  --ground:      #FAF9F6;
  --panel:       #FFFFFF;
  --panel-edge:  #E2E0D8;
  --ink:         #1B1F24;
  --ink-soft:    #4E5964;
  --ink-faint:   #808B96;
  --accent:      #1F6F6A;
  --accent-soft: #E4EFED;
  --ok:          #2F6B4F;
  --ok-soft:     #E5F0E8;
  --warn:        #8A6414;
  --warn-soft:   #F6EEDB;
  --open:        #9B3F32;
  --open-soft:   #F7E7E3;
  --rule:        #E8E6DE;
  --code-bg:     #F1EFE8;
  --mono: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace;
  --sans: ui-sans-serif, system-ui, -apple-system, "Segoe UI", Helvetica, Arial, sans-serif;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --ground:#12151A; --panel:#171B21; --panel-edge:#252B33;
    --ink:#E8E9EA; --ink-soft:#A6B0BB; --ink-faint:#75808C;
    --accent:#5FBDB2; --accent-soft:#17302F;
    --ok:#7FC79C; --ok-soft:#152A20;
    --warn:#DCB25E; --warn-soft:#2C2415;
    --open:#E08877; --open-soft:#31201C;
    --rule:#242A31; --code-bg:#1D222A;
  }
}
:root[data-theme="dark"] {
  --ground:#12151A; --panel:#171B21; --panel-edge:#252B33;
  --ink:#E8E9EA; --ink-soft:#A6B0BB; --ink-faint:#75808C;
  --accent:#5FBDB2; --accent-soft:#17302F;
  --ok:#7FC79C; --ok-soft:#152A20;
  --warn:#DCB25E; --warn-soft:#2C2415;
  --open:#E08877; --open-soft:#31201C;
  --rule:#242A31; --code-bg:#1D222A;
}
* { box-sizing: border-box; }
body {
  margin:0; background: var(--ground); color: var(--ink);
  font-family: var(--sans); line-height:1.55;
  -webkit-font-smoothing: antialiased;
}
.wrap { max-width: 62rem; margin:0 auto; padding: 3rem 1.5rem 6rem; }
header.masthead { border-bottom: 2px solid var(--ink); padding-bottom:1.5rem; margin-bottom:2rem; }
.eyebrow {
  font-family: var(--mono); font-size:.72rem; letter-spacing:.14em;
  text-transform: uppercase; color: var(--accent); margin:0 0 .6rem;
}
h1 { font-size: clamp(1.8rem, 4vw, 2.7rem); line-height:1.1; margin:0 0 .6rem;
     letter-spacing:-.02em; text-wrap: balance; }
.standfirst { font-size:1.05rem; color: var(--ink-soft); max-width:44rem; margin:0; }

.summary { margin:0; display:grid; grid-template-columns: repeat(auto-fit, minmax(11rem,1fr));
           gap:1px; background: var(--rule); border:1px solid var(--rule);
           margin: 2rem 0; }
.stat { background: var(--panel); padding:1rem 1.1rem; }
.stat__n { font-family: var(--mono); font-size:1.9rem; font-weight:600;
           font-variant-numeric: tabular-nums; letter-spacing:-.03em; display:block; }
.stat__l { font-size:.78rem; color: var(--ink-soft); display:block; margin-top:.15rem; }
.stat--ok  .stat__n { color: var(--ok); }
.stat--warn .stat__n { color: var(--warn); }
.stat--open .stat__n { color: var(--open); }

h2.sec { font-size:.82rem; font-family: var(--mono); letter-spacing:.12em;
         text-transform:uppercase; color: var(--ink-soft); margin:2rem 0 .7rem;
         font-weight:600; }
.note { font-size:.9rem; color: var(--ink-soft); max-width:44rem; margin:.9rem 0 0; }
.denominator { font-family: var(--mono); font-size:.78rem; color: var(--ink-faint);
               border-left:3px solid var(--accent); padding:.5rem 0 .5rem .8rem;
               margin: 0 0 2.5rem; }

.filter { display:flex; gap:.6rem; align-items:center; flex-wrap:wrap;
          position:sticky; top:0; background: var(--ground); padding:.9rem 0;
          border-bottom:1px solid var(--rule); z-index:5; margin-bottom:1.5rem; }
.filter input {
  flex:1 1 16rem; font-family: var(--mono); font-size:.9rem; padding:.55rem .7rem;
  border:1px solid var(--panel-edge); background: var(--panel); color: var(--ink);
  border-radius:2px;
}
.filter input:focus-visible { outline:2px solid var(--accent); outline-offset:1px; }
.filter__n { font-family: var(--mono); font-size:.8rem; color: var(--ink-faint);
             font-variant-numeric: tabular-nums; }

.bucket { margin: 3rem 0; }
.bucket__head { border-top:2px solid var(--ink); padding-top:1rem; margin-bottom:1.5rem; }
.bucket__head h2 { font-size:1.35rem; margin:0; letter-spacing:-.01em; }
.bucket__count { font-family: var(--mono); font-size:.85rem; color: var(--ink-soft);
                 margin:.3rem 0 .5rem; font-variant-numeric: tabular-nums; }
.bucket__blurb { font-size:.92rem; color: var(--ink-soft); max-width:44rem; margin:0; }

.row { display:grid; grid-template-columns: minmax(0,15rem) minmax(0,1fr); gap:1.2rem;
       padding:1.1rem 0; border-bottom:1px solid var(--rule); }
@media (max-width: 46rem) { .row { grid-template-columns: 1fr; gap:.5rem; } }
.row__id h3 { margin:0 0 .45rem; font-size:1rem; }
.row__meta { display:flex; flex-direction:column; gap:.3rem; align-items:flex-start; }
.row__body { min-width:0; }
code { font-family: var(--mono); font-size:.85em; background: var(--code-bg);
       padding:.1em .35em; border-radius:2px; word-break: break-word; }
.row__id code { background:none; padding:0; font-size:1rem; font-weight:600; color: var(--ink); }
.becomes { margin-bottom:.5rem; }
.willbe { font-style:italic; color: var(--warn); }
.k { font-family: var(--mono); font-size:.7rem; letter-spacing:.1em;
     text-transform:uppercase; color: var(--ink-faint); margin-right:.5rem; }
.account { font-size:.94rem; color: var(--ink); }
.muted { color: var(--ink-soft); }
blockquote { margin:.5rem 0 0; padding:.6rem .9rem; background: var(--panel);
             border-left:3px solid var(--warn); font-size:.88rem; color: var(--ink-soft); }
.sub { margin-top:.4rem; font-size:.86rem; color: var(--ink-soft); }
.sub--flag { color: var(--open); }
.chip { display:inline-block; font-family: var(--mono); font-size:.68rem;
        letter-spacing:.05em; padding:.18em .55em; border-radius:2px; white-space:nowrap;
        max-width:100%; overflow:hidden; text-overflow:ellipsis; }
.chip--plain { background: var(--code-bg); color: var(--ink-soft); }
.chip--ok    { background: var(--ok-soft);   color: var(--ok); }
.chip--warn  { background: var(--warn-soft); color: var(--warn); }
.chip--open  { background: var(--open-soft); color: var(--open); }
footer { margin-top:4rem; border-top:1px solid var(--rule); padding-top:1.2rem;
         font-size:.83rem; color: var(--ink-faint); }
.row[hidden] { display:none; }
</style>

<div class="wrap">
<header class="masthead">
  <p class="eyebrow">did_v1 &rarr; V_eta &middot; migration coverage</p>
  <h1>What happens to every v1 class</h1>
  <p class="standfirst">One row for each of the @TOTAL@ did_v1 source classes, and for each
  one: what it becomes, and <em>where that answer comes from</em>. Generated from the
  checked-in artifacts &mdash; nothing here is written by hand.</p>
</header>

<h2 class="sec">Can we say what happens to it?</h2>
<div class="summary">
  <div class="stat"><span class="stat__n">@TOTAL@</span><span class="stat__l">did_v1 source classes</span></div>
  <div class="stat stat--ok"><span class="stat__n">@PERCLASS@</span><span class="stat__l">answered class by class</span></div>
  <div class="stat stat--warn"><span class="stat__n">@FAMILY@</span><span class="stat__l">decided, family-level only</span></div>
  <div class="stat stat--open"><span class="stat__n">@NONE@</span><span class="stat__l">no decision on record</span></div>
  <div class="stat"><span class="stat__n">@SIGNED@/@FAMTOTAL@</span><span class="stat__l">decision families signed</span></div>
</div>

<h2 class="sec">Is it built?</h2>
<div class="summary">
  <div class="stat stat--ok"><span class="stat__n">@MIGRATOR@</span><span class="stat__l">a migrator implements this today</span></div>
  <div class="stat stat--warn"><span class="stat__n">@NOMIG@</span><span class="stat__l">no migrator yet</span></div>
</div>
<p class="note">These two questions have different answers, and conflating them is
how a migration looks finished before it is. A signed decision with no migrator is
a real answer to &ldquo;what happens to this class&rdquo; and an unfinished piece of
work at the same time. Every row carries both states.</p>

<p class="denominator">DENOMINATOR: @TOTAL@ source classes read from V_eta_coverage_ledger.json
(91 NDI production templates on origin/main + 11 vhlab app classes with no template).
@MIGRATOR@ have a bespoke migrator. Family state read from V_eta_decisions.json:
@SIGNED@ of @FAMTOTAL@ families carry a TEAM-SIGN-OFF line.</p>

<div class="filter">
  <input id="q" type="search" placeholder="Filter by class or target name&hellip;"
         aria-label="Filter classes" autocomplete="off">
  <span class="filter__n" id="count"></span>
</div>

@SECTIONS@

<footer>
  Generated by <code>tools/migration_map.py</code> from
  <code>V_eta_coverage_ledger.json</code> and <code>V_eta_decisions.json</code>.
  Re-run it after any schema or migrator change; the inputs are themselves generated
  and CI-checked for staleness.
</footer>
</div>

<script>
(function () {
  var q = document.getElementById('q');
  var count = document.getElementById('count');
  var rows = Array.prototype.slice.call(document.querySelectorAll('.row'));
  function apply() {
    var term = q.value.trim().toLowerCase();
    var shown = 0;
    rows.forEach(function (r) {
      var hit = !term || r.dataset.name.indexOf(term) !== -1;
      r.hidden = !hit;
      if (hit) shown++;
    });
    count.textContent = shown + ' of ' + rows.length + ' shown';
  }
  q.addEventListener('input', apply);
  apply();
})();
</script>"""
    subs = {
        "@TOTAL@":    str(counts["total"]),
        "@PERCLASS@": str(counts["per-class"]),
        "@FAMILY@":   str(counts["family"]),
        "@NONE@":     str(counts["none"]),
        "@MIGRATOR@": str(counts["migrator"]),
        "@SIGNED@":   str(signed),
        "@FAMTOTAL@": str(famtotal),
        "@NOMIG@":    str(counts["total"] - counts["migrator"]),
        "@SECTIONS@": "\n".join(sections),
    }
    for k, v in subs.items():
        page = page.replace(k, v)
    return page


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true",
                    help="exit non-zero if the checked-in page is stale")
    args = ap.parse_args()

    rows, dec, tgt = load()
    fams = family_index(dec)
    classified, counts = classify(rows, fams, tgt)

    # DENOMINATOR FIRST (Operating Rule 5), and it is load-bearing: a ledger that
    # failed to load would otherwise render an empty, calm-looking page.
    print("DENOMINATOR: %d v1 source class(es) read; %d decision families"
          % (counts["total"], len(dec.get("families", []))))
    if counts["total"] == 0:
        print("NO CLASSES READ -- refusing to write an empty map.")
        return 1
    print("  answered class by class      : %d" % counts["per-class"])
    print("  decided, family-level only   : %d" % counts["family"])
    print("  no decision on record        : %d" % counts["none"])

    page = render(classified, counts, dec)
    if args.check:
        if not os.path.exists(OUT):
            print("STALE: %s does not exist" % os.path.relpath(OUT, REPO))
            return 1
        with open(OUT, encoding="utf-8") as fh:
            if fh.read() != page:
                print("STALE: %s differs -- re-run tools/migration_map.py"
                      % os.path.relpath(OUT, REPO))
                return 1
        print("%s is current." % os.path.relpath(OUT, REPO))
        return 0

    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(page)
    print("wrote %s" % os.path.relpath(OUT, REPO))
    return 0


if __name__ == "__main__":
    sys.exit(main())
