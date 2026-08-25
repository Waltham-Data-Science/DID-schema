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
  padding:1.1rem 1.2rem;margin-bottom:.7rem;box-shadow:var(--shadow);
  border-left:3px solid var(--rule-2)}
.entry.answered{border-left-color:var(--confirm)}
.entry.answered .q{color:var(--ink-2)}
.entry.parked{border-left-color:var(--passthrough)}
.cls{font-family:var(--mono);font-size:.8rem;font-weight:600;color:var(--ink-3);
  word-break:break-word;letter-spacing:.02em}
.q{font-family:var(--serif);font-size:1.12rem;line-height:1.4;color:var(--ink);
  margin:.15rem 0 .9rem;text-wrap:pretty}
.q code{font-size:.88em}
.opts{display:flex;flex-wrap:wrap;gap:.4rem;margin-bottom:.5rem}
.opt{font-family:var(--sans);font-size:.85rem;cursor:pointer;
  border:1px solid var(--rule-2);background:var(--card);color:var(--ink-2);
  border-radius:2px;padding:.4rem .75rem;text-align:left}
.opt:hover{border-color:var(--accent);color:var(--ink)}
.opt:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.opt[aria-pressed="true"]{background:var(--accent);border-color:var(--accent);
  color:var(--paper);font-weight:600}
.note{width:100%;font-family:var(--sans);font-size:.85rem;color:var(--ink);
  background:var(--sunk);border:1px solid var(--rule-2);border-radius:2px;
  padding:.45rem .6rem;margin-top:.1rem;resize:vertical;min-height:2.4rem}
.note:focus-visible{outline:2px solid var(--accent);outline-offset:1px}
.note[hidden]{display:none}
details.ev{margin-top:.7rem}
details.ev>summary{font-family:var(--mono);font-size:.72rem;letter-spacing:.08em;
  text-transform:uppercase;color:var(--ink-3);cursor:pointer;
  list-style:none;display:inline-flex;align-items:center;gap:.35rem}
details.ev>summary::-webkit-details-marker{display:none}
details.ev>summary::before{content:"▸";font-size:.8em}
details.ev[open]>summary::before{content:"▾"}
details.ev>summary:hover{color:var(--accent)}
details.ev>summary:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.row{font-size:.88rem;color:var(--ink-2);margin-top:.4rem}
.row .k{font-family:var(--mono);font-size:.7rem;letter-spacing:.1em;
  text-transform:uppercase;color:var(--ink-3);margin-right:.5rem}
.bar{position:sticky;bottom:0;background:var(--card);border:1px solid var(--rule-2);
  border-bottom:0;border-radius:3px 3px 0 0;box-shadow:var(--shadow);
  padding:.7rem .9rem;display:flex;gap:.6rem;align-items:center;flex-wrap:wrap;
  margin-top:2rem}
.bar .lbl{font-family:var(--mono);font-size:.78rem;color:var(--ink-3);
  font-variant-numeric:tabular-nums;margin-right:auto}
button.act{font-family:var(--sans);font-size:.85rem;cursor:pointer;
  border:1px solid var(--accent);background:var(--accent);color:var(--paper);
  border-radius:2px;padding:.45rem .9rem;font-weight:600}
button.act.ghost{background:transparent;color:var(--ink-2);border-color:var(--rule-2)}
button.act:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
#export{width:100%;font-family:var(--mono);font-size:.78rem;line-height:1.6;
  color:var(--ink);background:var(--sunk);border:1px solid var(--rule-2);
  border-radius:2px;padding:.7rem;margin-top:.7rem;min-height:14rem}
#export[hidden]{display:none}
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
  // v2, AND v1 IS DELIBERATELY NOT MIGRATED. A v1 tick meant "I have looked at
  // this row"; a v2 entry means "my answer is X". Carrying the ticks forward
  // would turn 'reviewed' into 'confirmed' silently -- inventing agreement
  // nobody gave, which is the exact failure this sheet exists to prevent.
  var KEY='v_eta_confirm_v2';
  var ans={};
  try{ans=JSON.parse(localStorage.getItem(KEY)||'{}')}catch(e){ans={}}
  function save(){try{localStorage.setItem(KEY,JSON.stringify(ans))}catch(e){}}

  var entries=[].slice.call(document.querySelectorAll('.entry[data-cls]'));
  var asked=entries.filter(function(e){return e.dataset.mine==='1'});
  var prog=document.getElementById('progress');
  var barlbl=document.getElementById('barlbl');
  var box=document.getElementById('export');

  function paint(){
    var n=0;
    entries.forEach(function(e){
      var cur=ans[e.dataset.cls]||{};
      var mine=e.dataset.mine==='1';
      if(mine&&cur.a)n++;
      e.classList.toggle('answered',!!cur.a&&cur.a!=='unsure');
      e.classList.toggle('parked',cur.a==='unsure');
      [].forEach.call(e.querySelectorAll('.opt'),function(b){
        b.setAttribute('aria-pressed',String(cur.a===b.dataset.k));
      });
      var note=e.querySelector('.note');
      if(note){
        // The note appears only where it carries weight: a "no" or a "deferral"
        // is useless to the person acting on it without the because.
        var want=cur.a&&cur.a!=='yes'&&cur.a!=='end_state';
        note.hidden=!want;
        if(note.value!==(cur.note||''))note.value=cur.note||'';
      }
    });
    var txt=n+' of '+asked.length+' answered';
    prog.textContent=txt;
    barlbl.textContent=txt+(n<asked.length?'  ·  '+(asked.length-n)+' left':'  ·  complete');
  }

  entries.forEach(function(e){
    [].forEach.call(e.querySelectorAll('.opt'),function(b){
      b.addEventListener('click',function(){
        var cur=ans[e.dataset.cls]||{};
        // Clicking the chosen answer again CLEARS it. Without this there is no
        // way back to "unanswered", and a misclick would be permanent -- which
        // would push the count up while the reader disagrees with it.
        if(cur.a===b.dataset.k){delete cur.a}else{cur.a=b.dataset.k}
        if(!cur.a&&!cur.note){delete ans[e.dataset.cls]}else{ans[e.dataset.cls]=cur}
        save();paint();
      });
    });
    var note=e.querySelector('.note');
    if(note)note.addEventListener('input',function(){
      var cur=ans[e.dataset.cls]||{};
      cur.note=note.value;
      if(!cur.a&&!cur.note){delete ans[e.dataset.cls]}else{ans[e.dataset.cls]=cur}
      save();
    });
  });

  function render(){
    var out=[],by={},n=0;
    asked.forEach(function(e){
      var b=e.dataset.bucket;(by[b]=by[b]||[]).push(e);
    });
    Object.keys(by).forEach(function(b){
      out.push('');out.push(b+' ('+by[b].length+')');
      var miss=[];
      by[b].forEach(function(e){
        var cur=ans[e.dataset.cls]||{};
        if(!cur.a){miss.push(e.dataset.cls);return}
        n++;
        var lbl=e.querySelector('.opt[data-k="'+cur.a+'"]');
        out.push('  '+e.dataset.cls+'  ->  '+(lbl?lbl.textContent.trim():cur.a)
                 +(cur.note?'\\n      because: '+cur.note:''));
      });
      // UNANSWERED IS PRINTED, NOT OMITTED. A silent export would read as a
      // complete set of answers and the missing rows would be invisible.
      if(miss.length)out.push('  UNANSWERED ('+miss.length+'): '+miss.join(', '));
    });
    return ['V_eta confirm sheet -- answers',
            n+' of '+asked.length+' questions answered'].concat(out).join('\\n');
  }

  document.getElementById('show').addEventListener('click',function(){
    box.hidden=false;box.value=render();box.focus();box.select();
  });
  document.getElementById('copy').addEventListener('click',function(){
    box.hidden=false;box.value=render();box.select();
    var b=this;
    function ok(){b.textContent='Copied';setTimeout(function(){
      b.textContent='Copy answers'},1400)}
    // execCommand first: the async clipboard API is blocked in a sandboxed
    // frame, and a silent failure here loses the whole review.
    var done=false;
    try{done=document.execCommand('copy')}catch(e){}
    if(done){ok()}
    else if(navigator.clipboard){navigator.clipboard.writeText(box.value).then(ok,
      function(){b.textContent='Select the text below and copy'})}
    else{b.textContent='Select the text below and copy'}
  });
  paint();
})();
"""


def esc(s):
    return html.escape(str(s or ""))


def code_list(items):
    return ", ".join("<code>%s</code>" % esc(i) for i in items) if items else ""


def question_html(q):
    """`backticked` spans become <code>. Escape FIRST, then mark up.

    Order matters and is the whole reason this is a function: marking up first
    would let a class name containing a bracket escape its own tag.
    """
    parts = esc(q).split("`")
    return "".join(p if i % 2 == 0 else "<code>%s</code>" % p
                   for i, p in enumerate(parts))


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
            mine_to_answer = r.get("answer_from") == "team"
            # THE QUESTION IS THE HEADING. The class name is demoted to a label
            # above it: the reader is answering a question about a class, not
            # reading a record of a class that happens to end in a question.
            bits = ['<div class="cls">%s</div>' % esc(r["v1_class"]),
                    '<p class="q">%s</p>' % question_html(r["question"])]
            opts = r.get("options") or []
            if opts:
                bits.append(
                    '<div class="opts" role="group" aria-label="answer for %s">%s</div>'
                    % (esc(r["v1_class"]),
                       "".join('<button type="button" class="opt" data-k="%s" '
                               'aria-pressed="false">%s</button>'
                               % (esc(o["key"]), esc(o["label"])) for o in opts)))
                bits.append('<textarea class="note" hidden rows="2" '
                            'placeholder="Why — what should it be instead?" '
                            'aria-label="reason for %s"></textarea>'
                            % esc(r["v1_class"]))
            ev = []
            if r["emits"]:
                ev.append('<div class="row"><span class="k">emits today</span>%s</div>'
                          % code_list(r["emits"]))
            if r.get("carried"):
                ev.append('<div class="row"><span class="k">attaches to</span>%s</div>'
                          % code_list(r["carried"]))
            if r.get("second_pass"):
                ev.append('<div class="row"><span class="k">2nd pass</span>%s</div>'
                          % code_list(r["second_pass"]))
            if r["intent"]:
                ev.append('<div class="row"><span class="k">why</span>%s</div>'
                          % esc(r["intent"]))
            if r["caveat"]:
                ev.append('<div class="row"><span class="k">caveat</span>%s</div>'
                          % esc(r["caveat"]))
            ev.append('<div class="chips"><span class="chip %s">%s</span>'
                      '<span class="chip">corpus: %s</span></div>'
                      % (gcls, esc(gov), esc(r["corpus"])))
            bits.append('<details class="ev"><summary>What the migrator does '
                        'today, and why</summary>%s</details>' % "".join(ev))
            ents.append('<article class="entry" data-cls="%s" data-bucket="%s" '
                        'data-mine="%s">%s</article>'
                        % (esc(r["v1_class"]), esc(r["bucket"]),
                           "1" if mine_to_answer else "0", "".join(bits)))
        secs.append(
            '<section id="%s" class="b-%s"><div class="sec-head">'
            '<h2>%s</h2><span class="count">%d</span></div>'
            '<p class="ask">%s</p>%s</section>'
            % (k, k, esc(BUCKET_SHORT[k]), len(mine), esc(BUCKET_ASK[k]),
               "".join(ents)))

    n_team = sum(1 for r in rows if r.get("answer_from") == "team")
    n_other = len(rows) - n_team
    n_confirm = len(by.get("confirm") or [])
    n_pass = len(by.get("passthrough") or [])

    return """<title>V_eta Confirm Sheet</title>
<style>%s</style>
<div class="wrap">
<header class="top">
  <div class="eyebrow">did_v1 → V_eta · %d open questions</div>
  <h1>Nothing on this page is decided. These are the questions the migration is waiting on.</h1>
  <p class="lede">Each class below has a migrator that <strong>consumes its documents
  today</strong> and sends them somewhere. Nobody has ever said whether that
  somewhere is right. <strong>%d questions need an answer from you</strong>, in two
  shapes: %d are <em>“is this the target we want”</em>, %d are <em>“is this tombstone
  the end state, or is a fold still owed”</em>. The remaining %d cannot be put to you
  yet — someone has to read the migrator first, and that is my job, not yours.</p>
  <p class="lede">Answer by clicking. Nothing is sent anywhere; your answers stay in
  this browser until you press <strong>Copy answers</strong> at the bottom and paste
  them back to me. Click a chosen answer again to clear it.</p>
  <p class="den">%s</p>
</header>
<nav class="summary">%s<span class="progress" id="progress"></span></nav>
%s
<div class="bar">
  <span class="lbl" id="barlbl"></span>
  <button type="button" class="act ghost" id="show">Show answers</button>
  <button type="button" class="act" id="copy">Copy answers</button>
  <textarea id="export" hidden readonly aria-label="your answers, ready to paste"></textarea>
</div>
<footer>This page decides nothing and records no signature — the dispositions remain
the team's, and an answer here is your reply to me, not a decision written into the
record. Regenerate with <code>python3 tools/confirm_sheet.py</code>; the evidence
behind each row is in <code>V_eta_OPEN_WORK.md</code>.</footer>
</div>
<script>%s</script>
""" % (CSS, n_team, n_team, n_confirm, n_pass, n_other, esc(den),
       "".join(nav), "".join(secs), JS)


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
