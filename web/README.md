# DID schema web app

Browser-based viewer, editor, and submission tool for DID/NDI document
schemas. Targets `schemas/V_delta/`. Tracking issue: #28.

Status: **Steps 1--4 of issue #28 are in.** The site has a working viewer,
a schema editor with live meta-schema validation, "Download JSON", and
GitHub auth via personal access tokens. The end-to-end "Submit for review"
flow (issue + draft PR) is the next step (issue #39).

## V_eta shape panel (issue #72)

The **◈ V_eta shape** button opens a panel that renders the go-forward V_eta
class set as an inheritance tree starting from `base` -- a class with several
superclasses appears under each one and says where else it sits. Selecting a
class shows its fields and value shapes, superclasses and subclasses,
`depends_on` edges, and disposition / abstract flags. Classes outside
`schemas/V_eta_final_class_set.md`'s persist set are hidden unless asked for
(an ancestor of a shown class stays, dimmed), and a class's final-set category
is shown as a badge on its card. A **Tenets T1–T14** tab renders
`schemas/V_eta_tenets.md` for skimming: it opens as the 14 one-line headings;
an opened tenet shows its opening text and then its bold lead-ins as a
collapsed outline; tenet numbers in the text link to the tenet; and each tenet
lists the classes it shaped (from `public/tenets.json`, `tools/tenet_map.py`),
linked into the tree. The text is the document's own, only re-grouped.

Nothing is copied in. `src/veta/sources.ts` globs `schemas/V_eta/**/*.json`
and imports the two markdown files `?raw`, so Vite reads them at build time:
edit a class JSON, rebuild, and the panel follows with no code change.
`src/veta/grammar.json` is the one description of how the two markdown files
are parsed; the viewer and the gate both read it.

Two gates keep it honest:

- `python3 tools/check_veta_viewer.py` (a step in `tools/gates.py`, so it runs
  in `tests.yml`): the inputs agree -- 7 categories and 14 tenets parse, every
  class in the tree is placed exactly once, every placed name is in the tree,
  every category's `(n)` matches its list, and no class name is written into
  the viewer's source.
- `node scripts/check-veta-bundle.mjs` (after `npm run build`, in
  `web-build.yml` and `deploy-web.yml`): every JSON file under
  `schemas/V_eta/` and every line of the two markdown files reached the
  bundle.

## Develop

```sh
cd web
npm install
npm run dev
```

## Build

```sh
npm run build
```

Outputs a static bundle to `web/dist/`. The bundle is deployed to GitHub Pages
automatically on push to `main` by `.github/workflows/deploy-web.yml`.

## GitHub auth (prototype)

Sign-in uses a fine-grained personal access token while we prototype. A
device-flow GitHub App is registered (Client ID `Iv23liakOnQKoiLEhxDy`)
for later, but device flow requires a CORS proxy that we are not
deploying yet -- so PAT-paste is the only path for now.

To sign in:

1. Open <https://github.com/settings/personal-access-tokens/new>.
2. **Resource owner**: `Waltham-Data-Science`. **Repository access**:
   only `Waltham-Data-Science/DID-schema`.
3. **Repository permissions**:
   - Contents: Read and write
   - Issues: Read and write
   - Pull requests: Read and write
   - Everything else: No access.
4. Generate the token, copy it, and paste it into the "Sign in to GitHub"
   panel in the web app's left sidebar.

The token is held in `sessionStorage`, so it disappears when the tab
closes -- the next session will need a fresh paste (or the same PAT,
until it expires).

## Configuration

The site is served at `https://waltham-data-science.github.io/DID-schema/`, so
Vite's `base` is `/DID-schema/`. Override with the `VITE_BASE_PATH` env var if
deploying elsewhere (e.g. a preview environment).
