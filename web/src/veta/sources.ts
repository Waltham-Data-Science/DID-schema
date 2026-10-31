// THE V_eta VIEWER'S INPUTS, AND THE ONLY PLACE THEY ARE NAMED.
//
// Nothing about a V_eta class is written into this viewer. Every class, field,
// edge, category and tenet it renders is read from the schema tree, the
// generated index and the two markdown files below AT BUILD TIME: Vite
// resolves the glob, the index import and the `?raw` imports while bundling, so editing a class JSON (or re-running
// `tools/regen_final_class_set.py`) and rebuilding is all it takes for the
// viewer to show the change. No copy step, no generated snapshot, no hand edit.
//
// `tools/check_veta_viewer.py` reads THIS FILE to learn what the viewer loads
// (the glob pattern, the index import and the two raw imports) instead of keeping a second copy
// of that list, and `web/scripts/check-veta-bundle.mjs` asserts after a build
// that every file the glob matches really reached the bundle. Keep all three
// inputs as plain string literals here -- Vite requires it, and so does the
// gate.

import VETA_INDEX from "../../../schemas/generated/index.json";

// Every JSON file under schemas/did_v2/ -- class files only, in family folders
// ([schema folders by family]) -- keyed by its path relative to this module
// (e.g. "../../../schemas/did_v2/value/mass.json"), plus the generated index
// (schemas/generated/index.json), keyed the same way so the model finds it by
// its repository path.
const CLASS_FILES = import.meta.glob("../../../schemas/did_v2/**/*.json", {
  eager: true,
  import: "default",
}) as Record<string, unknown>;
export const VETA_FILES: Record<string, unknown> = {
  ...CLASS_FILES,
  "../../../schemas/generated/index.json": VETA_INDEX,
};

// The persist set, grouped into the 7 categories. Generated from the built
// index by tools/regen_final_class_set.py.
export { default as FINAL_CLASS_SET_MD } from "../../../schemas/V_eta_final_class_set.md?raw";

// Brainstorm J's thesis and tenets T1-T15.
export { default as TENETS_MD } from "../../../schemas/V_eta_tenets.md?raw";

// The prefix every VETA_FILES key starts with, so a key can be turned back
// into a repository path ("schemas/did_v2/value/mass.json").
export const VETA_KEY_PREFIX = "../../../";
