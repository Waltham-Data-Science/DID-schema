"""The canonical-unit list: each dimensioned value kind's canonical slot(s) and
the registered unit term each slot is in (tenet T14; Jess Haley 2026-10-22
[units bound], V_eta_data_body_model_plan.md).

T14 named this list `_DIM_CANON` in tools/build_v_eta.py; that script was
deleted 2026-10-21 (OPEN_WORK #128) and the list with it. It is restored here as
data, and tools/check_term_registry.py reads it (rule R11) to check that:

  * every field typed with a value kind below declares exactly these canonical
    slots, in this order, before `source_unit` (a new slot or a renamed one is
    a change to this list, made on purpose);
  * every unit term named here with a node is in the term registry under that
    node and that name;
  * every entry `unit` (covariates, conditions, method parameters) and every
    `response_unit` / fit-entry `unit` is a bound term.

A slot whose unit has no registered term yet carries node "". It is LISTED by
R11, never failed and never filled in here: choosing a unit's CURIE is a
registry decision (T19), and the canonical slot name already says the unit.

Usage: python3 tools/canonical_units.py      # print the list
"""

# kind -> [(canonical slot, unit name, unit node)]; node "" = no registered term yet
CANONICAL_UNITS = {
    "time": [("seconds", "second", "om:second-Time")],
    "volume": [("liters", "litre", "om:litre")],
    "mass": [("grams", "gram", "om:gram")],
    "length": [("meters", "metre", "om:metre")],
    "voltage": [("volts", "volt", "om:volt")],
    "current": [("amperes", "ampere", "om:ampere")],
    "frequency": [("hertz", "hertz", "om:hertz")],
    "temperature": [("celsius", "degree Celsius", "om:degreeCelsius")],
    "pressure": [("mmhg", "millimetre of mercury", "om:millimetreOfMercury")],
    # concentration has no single canonical: each slot is filled when the source
    # unit is computable into it. Ratio slots are named by unit (Jess Haley
    # 2026-10-22 [ratio slots named by unit]).
    "concentration": [("molar", "molar", "om:molar"), ("grams_per_liter", "gram per litre", "om:gramPerLitre"),
                      ("grams_per_gram", "gram per gram", "om:gramPerGram"), ("liters_per_liter", "Liter Per Liter", "NCIT:C105495"),
                      ("particles_per_liter", "reciprocal litre", "om:reciprocalLitre"), ("osmolar", "Unit of Osmotic Concentration", "NCIT:C67425"),
                      ("optical_density", "Absorbance Unit", "NCIT:C73686")],
    "velocity": [("meters_per_second", "metre per second", "om:metrePerSecond-Time")],
    "acceleration": [("meters_per_second_squared", "metre per second squared", "om:metrePerSecond-TimeSquared")],
    "area": [("square_meters", "square metre", "om:squareMetre")],
    "angle": [("degrees", "degree", "om:degree")],
    "angular_velocity": [("degrees_per_second", "Degrees Per Second", "NCIT:C166097")],
    "force": [("newtons", "newton", "om:newton")],
    "energy": [("joules", "joule", "om:joule")],
    "power": [("watts", "watt", "om:watt")],
    "charge": [("coulombs", "coulomb", "om:coulomb")],
    "resistance": [("ohms", "ohm", "om:ohm")],
    "conductance": [("siemens", "siemens", "om:siemens")],
    "capacitance": [("farads", "farad", "om:farad")],
    "substance_amount": [("moles", "mole", "om:mole")],
    "intensity": [("arbitrary_units", "Arbitrary Unit", "NCIT:C75765")],
    "irradiance": [("watts_per_square_meter", "watt per square metre", "om:wattPerSquareMetre")],
    # a part of a whole (Jess Haley 2026-10-26 [fraction value kind]); a percent is
    # kept as its source_value with source_unit om:percent.
    "fraction": [("fraction", "one", "om:one")],
    "ph": [("ph", "pH", "UO:0000196")],
    "gain": [("decibels", "decibel", "om:decibel")],
    "humidity": [("percent_relative_humidity", "percent", "om:percent")],
}

# The entry and response `unit` slots that must be bound terms (C2 [units bound],
# M1 [remaining units bound]): (class, dotted field path).
BOUND_UNIT_FIELDS = [
    ("statement", "conditions.unit"), ("data_body", "conditions.unit"),
    ("interaction", "method.parameters.unit"), ("method", "parameters.unit"),
    ("relation", "method.parameters.unit"),
    ("clock_alignment_configuration", "method.parameters.unit"),
    ("data", "covariates.unit"), ("acquisition_epoch", "covariates.unit"),
    ("tuning_curve", "value.response_unit"), ("contrast_sensitivity", "value.response_unit"),
    ("model_fit", "value.independent_variables.unit"), ("model_fit", "value.dependent_variable.unit"),
    ("tuning_curve", "value.model_fit.independent_variables.unit"),
    ("tuning_curve", "value.model_fit.dependent_variable.unit"),
    ("contrast_sensitivity", "value.model_fit.independent_variables.unit"),
    ("contrast_sensitivity", "value.model_fit.dependent_variable.unit"),
]


def _walk(fields, path=""):
    for f in fields or []:
        p = path + f["name"]
        yield p, f
        yield from _walk(f.get("fields"), p + ".")


def check(classes, terms):
    """classes: {name: class json}; terms: registry rows.
    Returns (failures, listed, counts)."""
    by_node = {(t.get("node") or "").lower(): t for t in terms if t.get("node")}
    fails, listed = [], []
    n_cells = 0
    for cn, d in sorted(classes.items()):
        for path, f in _walk(d.get("fields")):
            if f.get("type") not in CANONICAL_UNITS:
                continue
            n_cells += 1
            cell = f.get("fields")
            if not cell:
                # A reference ([quantity reference type], Jess Haley 2026-10-27):
                # the field names its value class and the cell is read from it.
                src = classes.get(f["type"]) or {}
                cell = next((x.get("fields") for x in src.get("fields", [])
                             if x["name"] == "value"), None) or []
            subs = [x["name"] for x in cell]
            got = subs[:subs.index("source_unit")] if "source_unit" in subs else subs
            want = [s for s, _, _ in CANONICAL_UNITS[f["type"]]]
            if got != want:
                fails.append(f"R11 {cn}.{path} ({f['type']}): canonical slots {got}, "
                             f"the list says {want}")
    n_units = 0
    for kind, slots in CANONICAL_UNITS.items():
        for slot, name, node in slots:
            n_units += 1
            if not node:
                listed.append(f"{kind}.{slot}: unit '{name}' has no registered term")
                continue
            t = by_node.get(node.lower())
            if t is None:
                fails.append(f"R11 {kind}.{slot}: unit {node} is not in the term registry")
            elif t["name"] != name:
                fails.append(f"R11 {kind}.{slot}: unit {node} is registered as "
                             f"{t['name']!r}, the list says {name!r}")
    for cn, path in BOUND_UNIT_FIELDS:
        d = classes.get(cn)
        f = dict(_walk(d.get("fields"))).get(path) if d else None
        if f is None:
            fails.append(f"R11 {cn}.{path}: no such field")
        elif f.get("type") != "ontology_term" or not (f.get("constraints") or {}).get("binding"):
            fails.append(f"R11 {cn}.{path}: not a bound term")
    return fails, listed, {"cells": n_cells, "units": n_units,
                           "bound_unit_fields": len(BOUND_UNIT_FIELDS)}


if __name__ == "__main__":
    for kind, slots in CANONICAL_UNITS.items():
        for slot, name, node in slots:
            print(f"{kind:18} {slot:28} {name:28} {node or '(no registered term)'}")
