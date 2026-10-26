"""tools/check_carry_register.py: the carry register's gate (Jess Haley,
2026-10-26, V_eta_go_forward_class_audit.md [carry register], [one correct
reading])."""
import copy
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools"))
import check_carry_register as ccr

DEC = {"document": "V_eta_go_forward_class_audit.md", "tag": "small unread settings"}
DO_NOT = {"line": "do not add OS links to `method`", "class": "method",
          "fields": ["operating_system_id"]}


def row(kind, **kw):
    r = {"id": kw.pop("id", "carry-001"), "v1_class": "sorting_parameters",
         "fields": ["app.os"], "when": "w", "kind": kind, "kind_basis": "stated",
         "decision": dict(DEC)}
    extra = {"awaiting_home": {"open_work": None, "home": "h"},
             "needs_mapping": {"homes": ["a", "b"], "decides": "d", "resolved_by": "r"},
             "not_modelled": {"do_not": copy.deepcopy(DO_NOT)},
             "malformed": {}}.get(kind, {})
    r.update(extra)
    r.update(kw)
    return r


def reg(*rows):
    return {"description": "t", "kinds": list(ccr.KINDS), "rows": list(rows)}


TREE = {
    "base": ({"id", "session_id"}, []),
    "method": ({"term", "software_id"}, ["base"]),
    "interaction": ({"operating_system_id", "software_id"}, ["base"]),
    "calculation": ({"input_id"}, ["interaction"]),
}


def test_the_four_kinds_and_their_keys_pass():
    rows = [row(k, id=f"carry-{i}") for i, k in enumerate(ccr.KINDS)]
    assert ccr.check_shape(reg(*rows)) == []


def test_the_kind_list_is_the_decided_one():
    r = reg(row("malformed"))
    r["kinds"] = ["awaiting_home", "not_modelled", "malformed"]
    assert any(f.startswith("C1 `kinds`") for f in ccr.check_shape(r))


def test_a_row_missing_its_kind_keys_or_with_an_unknown_kind_fails():
    bad = row("needs_mapping")
    del bad["resolved_by"]
    fails = ccr.check_shape(reg(bad, row("orphaned", id="carry-002"),
                                row("malformed", id="carry-001")))
    assert len(fails) == 3, fails
    assert "missing ['resolved_by']" in fails[0]
    assert "kind 'orphaned'" in fails[1]
    assert "used twice" in fails[2]


def test_open_work_is_a_row_number_or_null():
    assert ccr.check_shape(reg(row("awaiting_home", open_work=128))) == []
    fails = ccr.check_shape(reg(row("awaiting_home", open_work="#128")))
    assert len(fails) == 1 and "open_work" in fails[0]


def test_an_unregistered_v1_class_fails():
    fails = ccr.check_v1_classes([row("malformed", v1_class="nosuch")], {"sorting_parameters"})
    assert len(fails) == 1 and "nosuch" in fails[0]


def test_every_decision_must_resolve():
    def resolve(document, tag):
        return {"resolved": tag == "small unread settings", "why": "no line"}
    rows = [row("malformed"), row("malformed", id="carry-002",
                                  decision={"document": DEC["document"], "tag": "invented"})]
    fails, ok = ccr.check_decisions(rows, resolve)
    assert ok == 1 and len(fails) == 1 and "[invented]" in fails[0]


def test_a_not_modelled_line_holds_while_the_class_does_not_declare_the_field():
    fails, n = ccr.check_do_not([row("not_modelled")], TREE)
    assert (fails, n) == ([], 1)


def test_a_class_gaining_a_forbidden_field_fails_quoting_the_do_not_line():
    tree = dict(TREE)
    tree["method"] = ({"term", "operating_system_id"}, ["base"])
    fails, n = ccr.check_do_not([row("not_modelled")], tree)
    assert n == 1 and len(fails) == 1
    assert "method declares 'operating_system_id'" in fails[0]
    assert '"do not add OS links to `method`"' in fails[0]


def test_a_forbidden_field_arriving_by_inheritance_fails():
    tree = dict(TREE)
    tree["method"] = ({"term"}, ["interaction"])
    fails, _ = ccr.check_do_not([row("not_modelled")], tree)
    assert len(fails) == 1 and "inherited from interaction" in fails[0]


def test_a_do_not_naming_no_class_cannot_pass():
    r = row("not_modelled")
    r["do_not"]["class"] = "nosuch"
    fails, n = ccr.check_do_not([r], TREE)
    assert n == 0 and len(fails) == 1 and "cannot be checked" in fails[0]


def test_the_live_register():
    """The committed register: its denominator is non-zero, every kind is one
    of the four, and the gate passes on it."""
    live = ccr._load(ccr.REGISTER)
    rows = live["rows"]
    assert len(rows) > 0
    assert ccr.check_shape(live) == []
    assert {r["kind"] for r in rows} <= set(ccr.KINDS)
    assert any(r["kind"] == "not_modelled" for r in rows)
    tree = ccr.class_tree()
    assert len(tree) > 0
    fails, n = ccr.check_do_not(rows, tree)
    assert fails == [] and n > 0
