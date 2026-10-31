# Landing PR #76 without turning the siblings red (option B)

Drafted 2026-09-29. **Step 1 is being REDONE as a tag** (jess, 2026-09-29): a branch
`v_eta-pre73` was created at `0043cbb` through the GitHub API when the session could not push a
tag, and jess then chose the tag instead. This session could not delete the branch either
(same push restriction), so jess deletes it and pushes the tag -- in that order, because a
branch and a tag of one name make `ref:` ambiguous. Step 2's patches are not applied yet;
each needs a person with push rights on that repository.

## Why a merge breaks CI today

DID-schema PR #76 changes only `schemas/V_eta*`, the plan documents and 10 tools
(`git diff --name-only origin/main...HEAD`; `tools/bar2_gap.py` and `tools/coverage.py`
are called across the repo boundary by DID-matlab's corpus run). The migrators still emit
the pre-#73 shape, so any sibling job that validates against did-schema `main` goes red
the moment #76 merges. The jobs that read `main`, measured on DID-matlab `V2` / the V_eta
branches (`47cf8ba`) and NDI-matlab's V_eta branch (`9609273e1`):

| repo | workflow | how it picks did-schema |
|---|---|---|
| DID-matlab | `test-code.yml:46` | `ref: main` (hard pin) |
| DID-matlab | `test-fixtures.yml:35` | `ref: main` (hard pin) |
| DID-matlab | `test-migrators-quick.yml` | same-named branch, else PR #68 branch, else **main** |
| DID-matlab | `test-soph-corpus.yml:58` | input, else `github.ref_name`, else **main** |
| NDI-matlab | `test-eta-migrate-dab.yml:62` | `DID_SCHEMA_REF: main` |
| NDI-matlab | `test-eta-migrate-e2e.yml:79` | `DID_SCHEMA_REF: main` |
| NDI-matlab | `test-eta-migrate-soph.yml:59` | `DID_SCHEMA_REF: main` |

Not affected: DID-matlab `matlab-scratch.yml` and `test-corpus.yml` (same-named branch),
and NDI `test-epsilon-migrate.yml`, `test-vnext.yml`, `test-zeta-migrate.yml` (they read
the V_epsilon / vNext / V_zeta trees, which #76 does not touch). The four DID-matlab files
are identical on `V2` and on the V_eta branch; the three NDI files exist only on NDI's
V_eta branch (PR #836), not on NDI `main`.

## Steps

1. **Freeze the pre-#73 schema.** Delete the interim branch `v_eta-pre73`, then tag
   `0043cbb` (= `origin/main` on 2026-09-29) as `v_eta-pre73` and push the tag.
2. **Pin the siblings to the tag.** Apply the patches from each repo root with
   `patch -p1 < <file>`:
   - `DID-matlab-pin.patch` on DID-matlab `V2` (and any open branch that should stay
     green): `test-code.yml`, `test-fixtures.yml`, the did-schema fallback in
     `test-migrators-quick.yml` (the NDI-matlab fallback beside it is left alone), and
     the default in `test-soph-corpus.yml` -- which must DROP `github.ref_name` from its
     fallback chain, not just replace `main`: on a push `ref_name` is always set (the DID-matlab
     branch name), so a trailing default is never reached. Found on the first pinned run
     (DID-matlab run 36646874292, did-schema checkout failed) and fixed in the patch.
   - `NDI-matlab-pin.patch` on NDI's V_eta branch: the three `test-eta-migrate-*` files.
   Confirm one green run of each pinned workflow before step 3.
3. **Get the #73 sign-offs** (or objections) from the team, then **merge PR #76.**
   Nothing pinned changes behaviour.
4. **Move the pin as the migrators catch up.** Each DID-matlab / NDI PR that implements
   part of the PR #76 checklist runs against a did-schema branch of the same name (the
   workflows already look for one), and the pin moves to `main` once a sibling emits
   the #73 shape for everything its workflows test. Remove the pin and its comments then.
