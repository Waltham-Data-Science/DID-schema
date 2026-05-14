# DID schema web app

Browser-based viewer, editor, and submission tool for DID/NDI document
schemas. Targets `schemas/V_delta/`. Tracking issue: #28.

Status: **Step 1 -- scaffolding only.** No viewer or editor functionality yet.

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

## Configuration

The site is served at `https://waltham-data-science.github.io/DID-schema/`, so
Vite's `base` is `/DID-schema/`. Override with the `VITE_BASE_PATH` env var if
deploying elsewhere (e.g. a preview environment).
