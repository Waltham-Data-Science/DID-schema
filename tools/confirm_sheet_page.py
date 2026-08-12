#!/usr/bin/env python3
"""Render the confirm sheet as a self-contained page a reviewer can work in.

The markdown sheet needs a markdown reader; this needs a browser. Same data,
same buckets, same order -- built from `confirm_sheet.py --json` so no row is
transcribed by hand.

WHAT IT ADDS OVER THE MARKDOWN, and the reason each is here rather than
decoration: a per-class checkbox that PERSISTS in localStorage, so a review can
be done across several sittings without losing the place; a running answered
count, because "50 confirmations" is only useful if you can see where you are in
them; and the bucket's question stated once at the top of its section instead of
per row.

IT STILL DECIDES NOTHING. No signature, no disposition, no recommendation on any
row -- a tick is a private note to the reader, held in their own browser, and
never leaves it.
"""
import argparse
import html
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

# Ordered cheapest-answer-first, matching confirm_sheet.py. The order carries
# information -- a sitting that runs out of time has cleared the confirmable
# ones -- so the sections are NOT numbered: numbering would imply a sequence
# that must be completed in order, and this one may be stopped anywhere.
BUCKET_KEY = {
    "CONFIRM THE EMITTED SET": "confirm",
    "CONFIRM A PASSTHROUGH": "passthrough",
    "NO EMISSION RECORDED -- INVESTIGATE FIRST": "investigate",
    "ABSENT FROM THE TARGET MAP": "absent",
}
BUCKET_ASK = {
    "confirm": "The migrator emits a new target set and the intent is written "
               "down. The ask is yes or no on that set.",
    "passthrough": "The migrator emits the class under its own v1 name — the "
                   "document survives unchanged, as a tombstone. The ask is "
                   "whether that is the intended end state or a deferral "
                   "nobody wrote down.",
    "investigate": "In the target map with an authored intent, but the call "
                   "graph resolved no emitted class. A question for whoever "
                   "reads the migrator before it reaches you.",
    "absent": "Not in the curated target map at all. Nothing is recorded to "
              "confirm.",
}
BUCKET_SHORT = {"confirm": "Confirm the emitted set",
                "passthrough": "Confirm a passthrough",
                "investigate": "Investigate first",
                "absent": "Absent from the map"}

CSS = """
*,*::before,*::after{box-sizing:border-box}
:root{
  --paper:#f3f5f5; --card:#fff; --sunk:#eceff0;
  --ink:#14181b; --ink-2:#48525a; --ink-3:#78838b;
  --rule:#dce1e2; --rule-2:#c6cdcf;
  --accent:#0f6469;
  --confirm:#37624a; --passthrough:#8a5f0c; --investigate:#9a3f26; --absent:#626c71;
  --shadow:0 1px 2px rgba(20,24,27,.05),0 8px 24px -16px rgba(20,24,27,.28);
  --serif:Iowan Old Style,Palatino Linotype,Palatino,Georgia,serif;
  --sans:system-ui,-apple-system,Segoe UI,Roboto,Helvetica Neue,sans-serif;
  --mono:ui-monospace,SFMono-Regular,SF Mono,Menlo,Consolas,monospace;
}
@media (prefers-color-scheme:dark){
  :root:not([data-theme="light"]){
    --paper:#0e1214; --card:#161b1e; --sunk:#111618;
    --ink:#e9eeef; --ink-2:#a8b3b8; --ink-3:#7d888e;
    --rule:#242c30; --rule-2:#333d42;
    --accent:#5cbfc4;
    --confirm:#82b899; --passthrough:#d6a340; --investigate:#e0836a; --absent:#96a0a5;
    --shadow:0 1px 2px rgba(0,0,0,.4),0 8px 24px -16px rgba(0,0,0,.7);
  }
}
:root[data-theme="dark"]{
  --paper:#0e1214; --card:#161b1e; --sunk:#111618;
  --ink:#e9eeef; --ink-2:#a8b3b8; --ink-3:#7d888e;
  --rule:#242c30; --rule-2:#333d42;
  --accent:#5cbfc4;
  --confirm:#82b899; --passthrough:#d6a340; --investigate:#e0836a; --absent:#96a0a5;
  --shadow:0 1px 2px rgba(0,0,0,.4),0 8px 24px -16px rgba(0,0,0,.7);
}
body{margin:0;background:var(--paper);color:var(--ink);
  font-family:var(--sans);font-size:16px;line-height:1.55;
  -webkit-font-smoothing:antialiased}
.wrap{max-width:60rem;margin:0 auto;padding:0 1.5rem 6rem}
header.top{padding:3.5rem 0 2rem;display:flex;flex-direction:column;gap:1rem}
.eyebrow{font-family:var(--mono);font-size:.72rem;letter-spacing:.13em;
  text-transform:uppercase;color:var(--accent)}
h1{font-family:var(--serif);font-weight:600;font-size:clamp(2rem,4.4vw,2.9rem);
  line-height:1.1;margin:0;text-wrap:balance;letter-spacing:-.015em}
.lede{max-width:38em;color:var(--ink-2);font-size:1.03rem;margin:0}
.lede strong{color:var(--ink);font-weight:600}
.den{font-family:var(--mono);font-size:.78rem;color:var(--ink-3);
  border-top:1px solid var(--rule);padding-top:.9rem;line-height:1.7}
nav.summary{position:sticky;top:0;z-index:5;background:var(--paper);
  border-bottom:1px solid var(--rule);margin-bottom:2.5rem;
  padding:.7rem 0;display:flex;flex-wrap:wrap;gap:.5rem;align-items:center}
nav.summary a{display:inline-flex;align-items:baseline;gap:.45rem;
  text-decoration:none;color:var(--ink-2);border:1px solid var(--rule-2);
  border-radius:2px;padding:.3rem .6rem;font-size:.82rem;background:var(--card)}
nav.summary a:hover{border-color:var(--accent);color:var(--ink)}
nav.summary a:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
nav.summary .n{font-family:var(--mono);font-weight:600;font-variant-numeric:tabular-nums}
.progress{margin-left:auto;font-family:var(--mono);font-size:.78rem;
  color:var(--ink-3);font-variant-numeric:tabular-nums}
section{margin-bottom:3.5rem;scroll-margin-top:4.5rem}
.sec-head{border-top:2px solid var(--ink);padding-top:.8rem;margin-bottom:.4rem;
  display:flex;align-items:baseline;gap:.7rem;flex-wrap:wrap}
h2{font-family:var(--serif);font-size:1.45rem;font-weight:600;margin:0;
  letter-spacing:-.01em}
.count{font-family:var(--mono);font-size:.95rem;color:var(--ink-3);
  font-variant-numeric:tabular-nums}
.ask{color:var(--ink-2);max-width:44em;margin:0 0 1.4rem;font-size:.95rem}
.entry{background:var(--card);border:1px solid var(--rule);border-radius:3px;
  padding:1rem 1.1rem;margin-bottom:.6rem;box-shadow:var(--shadow);
  display:grid;grid-template-columns:auto 1fr;gap:.15rem .85rem}
.entry.done{opacity:.55}
.tick{grid-row:1/span 9;padding-top:.15rem}
.tick input{width:1.05rem;height:1.05rem;accent-color:var(--accent);cursor:pointer}
.tick input:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.cls{font-family:var(--mono);font-size:1rem;font-weight:600;color:var(--ink);
  word-break:break-word}
.row{font-size:.9rem;color:var(--ink-2);margin-top:.35rem}
.row .k{font-family:var(--mono);font-size:.7rem;letter-spacing:.1em;
  text-transform:uppercase;color:var(--ink-3);margin-right:.5rem}
code{font-family:var(--mono);font-size:.85em;background:var(--sunk);
  border:1px solid var(--rule);border-radius:2px;padding:.05em .35em}
.chips{display:flex;flex-wrap:wrap;gap:.4rem;margin-top:.6rem}
.chip{font-family:var(--mono);font-size:.7rem;letter-spacing:.06em;
  border:1px solid var(--rule-2);border-radius:99px;padding:.15rem .55rem;
  color:var(--ink-3)}
.chip.sig{color:var(--confirm);border-color:currentColor}
.chip.unsig{color:var(--ink-3)}
.chip.disputed{color:var(--investigate);border-color:currentColor;font-weight:600}
.b-confirm .sec-head{border-top-color:var(--confirm)}
.b-passthrough .sec-head{border-top-color:var(--passthrough)}
.b-investigate .sec-head{border-top-color:var(--investigate)}
.b-absent .sec-head{border-top-color:var(--absent)}
footer{border-top:1px solid var(--rule);padding-top:1.4rem;color:var(--ink-3);
  font-size:.85rem;max-width:44em}
@media (prefers-reduced-motion:reduce){*{transition:none!important;animation:none!important}}
@media (max-width:34rem){.entry{grid-template-columns:1fr}.tick{grid-row:auto}}
"""

JS = """
(function(){
  var KEY='v_eta_confirm_v1';
  var done={};
  try{done=JSON.parse(localStorage.getItem(KEY)||'{}')}catch(e){done={}}
  var boxes=[].slice.call(document.querySelectorAll('input[type=checkbox][data-cls]'));
  var out=document.getElementById('progress');
  function paint(){
    var n=0;
    boxes.forEach(function(b){
      var on=!!done[b.dataset.cls];
      b.checked=on; b.closest('.entry').classList.toggle('done',on); if(on)n++;
    });
    out.textContent=n+' of '+boxes.length+' marked';
  }
  boxes.forEach(function(b){
    b.addEventListener('change',function(){
      if(b.checked){done[b.dataset.cls]=1}else{delete done[b.dataset.cls]}
      try{localStorage.setItem(KEY,JSON.stringify(done))}catch(e){}
      paint();
    });
  });
  paint();
})();
"""


def esc(s):
    return html.escape(str(s or ""))


def code_list(items):
    return ", ".join("<code>%s</code>" % esc(i) for i in items) if items else ""


def build(blob, den):
    rows = blob["rows"]
    by = {}
    for r in rows:
        by.setdefault(BUCKET_KEY[r["bucket"]], []).append(r)
    for k in by:
        by[k].sort(key=lambda r: r["v1_class"].lower())

    nav = []
    for k in ("confirm", "passthrough", "investigate", "absent"):
        if by.get(k):
            nav.append('<a href="#%s"><span class="n">%d</span> %s</a>'
                       % (k, len(by[k]), esc(BUCKET_SHORT[k])))

    secs = []
    for k in ("confirm", "passthrough", "investigate", "absent"):
        mine = by.get(k) or []
        if not mine:
            continue
        ents = []
        for r in mine:
            gov = r["governance"]
            gcls = ("disputed" if "DISPUT" in gov.upper()
                    else "sig" if gov == "signed" else "unsig")
            bits = ['<div class="tick"><input type="checkbox" data-cls="%s" '
                    'aria-label="mark %s reviewed"></div>'
                    % (esc(r["v1_class"]), esc(r["v1_class"])),
                    '<div class="cls">%s</div>' % esc(r["v1_class"])]
            if r["emits"]:
                bits.append('<div class="row"><span class="k">emits</span>%s</div>'
                            % code_list(r["emits"]))
            if r.get("carried"):
                bits.append('<div class="row"><span class="k">attaches to</span>%s</div>'
                            % code_list(r["carried"]))
            if r.get("second_pass"):
                bits.append('<div class="row"><span class="k">2nd pass</span>%s</div>'
                            % code_list(r["second_pass"]))
            if r["intent"]:
                bits.append('<div class="row"><span class="k">intent</span>%s</div>'
                            % esc(r["intent"]))
            if r["caveat"]:
                bits.append('<div class="row"><span class="k">caveat</span>%s</div>'
                            % esc(r["caveat"]))
            bits.append('<div class="chips"><span class="chip %s">%s</span>'
                        '<span class="chip">corpus: %s</span></div>'
                        % (gcls, esc(gov), esc(r["corpus"])))
            ents.append('<article class="entry">%s</article>' % "".join(bits))
        secs.append(
            '<section id="%s" class="b-%s"><div class="sec-head">'
            '<h2>%s</h2><span class="count">%d</span></div>'
            '<p class="ask">%s</p>%s</section>'
            % (k, k, esc(BUCKET_SHORT[k]), len(mine), esc(BUCKET_ASK[k]),
               "".join(ents)))

    return """<title>V_eta Confirm Sheet</title>
<style>%s</style>
<div class="wrap">
<header class="top">
  <div class="eyebrow">did_v1 → V_eta · review, not a build</div>
  <h1>The migration runs on these classes. Nobody has confirmed where it sends them.</h1>
  <p class="lede">Each class below has a migrator that <strong>consumes its documents
  today</strong>. What is missing is a record that the target it emits is the target
  we want. That is a review, and this is its sheet — sorted by the kind of answer
  each class needs, cheapest first, so a sitting that runs out of time has cleared
  the confirmable ones rather than a random third of the list.</p>
  <p class="den">%s</p>
</header>
<nav class="summary">%s<span class="progress" id="progress"></span></nav>
%s
<footer>Ticks are a private note to you, kept in this browser and sent nowhere. This
page decides nothing and records no signature — the dispositions remain the team's.
Regenerate with <code>python3 tools/confirm_sheet.py</code>; the evidence behind each
row is in <code>V_eta_OPEN_WORK.md</code>.</footer>
</div>
<script>%s</script>
""" % (CSS, esc(den), "".join(nav), "".join(secs), JS)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", dest="src", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--denominator", default="")
    a = ap.parse_args(argv)
    with open(a.src) as fh:
        blob = json.load(fh)
    with open(a.out, "w") as fh:
        fh.write(build(blob, a.denominator))
    print("wrote %s -- %d row(s)" % (a.out, len(blob["rows"])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
