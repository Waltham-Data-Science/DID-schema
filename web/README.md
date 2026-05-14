# DID schema web app

Browser-based viewer, editor, and submission tool for DID/NDI document
schemas. Targets `schemas/V_delta/`. Tracking issue: #28.

Status: **Steps 1--4 of issue #28 are in.** The site has a working viewer,
a schema editor with live meta-schema validation, "Download JSON", and
GitHub auth via personal access tokens. The end-to-end "Submit for review"
flow (issue + draft PR) is the next step (issue #39).

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
