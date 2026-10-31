# V_eta: linked and ingested sessions in a dataset

Written 2026-10-09 at Jess Haley's request; signed by Jess Haley the same day
(the TEAM-SIGN-OFF line at the end). The class it proposes, `linked_session`,
is built in `draft/`.

## What v1 did

v1's `ndi.dataset` (NDI-matlab `main`, `src/ndi/+ndi/dataset.m`) keeps one
`session_in_a_dataset` document per session in the dataset's database: the
session's id and reference, `is_linked`, and how to open it (its class and
folder path).

- **Ingested** (`add_ingested_session`, `is_linked` 0): every document of the
  session (`ndi.query('', 'isa', 'base')`, `extract_docs_files.m:87-89`) and
  every file attached to them is copied into the dataset, ids unchanged. The
  session must first be fully ingested itself (`session.isIngested`: its raw
  recordings read into its own database). `open_session` opens it from the
  dataset's folder. The original session folder is left in place.
- **Linked** (`add_linked_session`, `is_linked` 1): nothing is copied; the
  dataset stores the folder, and `database_search` searches the dataset's own
  database and then each linked session's.
- Every pointer goes from the dataset to its sessions. A session opened from its
  own folder does not know its dataset.

V_eta has no `session_in_a_dataset`: the migrator turns it into a `dataset`
entity and a session `part_of` relation.

## The proposal

`session_in_a_dataset` recorded two different facts. V_eta records them apart.

1. **Membership is a relation.** The session is `part_of` the dataset, or
   `part_of` a study that is `part_of` the dataset: a `directed_relation`, child
   the session's `entity` document, parent the dataset's or the study's. It is
   stored in the dataset's database and is the same for both kinds. A session
   that is `part_of` a study needs no relation to the dataset itself: the study
   is (each fact stated once, T17).

2. **Where a linked session lives is configuration.** The signed rule
   (`did_v2_entity_composition_plan.md`, 2026-10-08): "configuration is what the
   software needs to read the data: its own class off `base`, with no
   statements." A folder path is exactly that, so it is a document of its own,
   `linked_session`, never an assertion about the session: a path describes a
   disk, it changes when a folder moves while the session does not, and the
   dataset must read it before the session's own database is open.

### `linked_session` (`draft/`)

| | |
|---|---|
| superclass | `base` |
| stored in | the dataset's database (`base.session_id` the dataset's own session id) |
| `path` (char, required) | the session's folder: relative to the dataset's folder when inside it, else absolute |
| edge `entity_id` (required) | the session's `entity` document (type session), which lives in the linked folder |

- Its presence means linked; an ingested session has none.
- The edge is `entity_id`, the name V_eta gives a document's one entity edge
  (`statement`, `method_parameters`, `undirected_relation`). Not `session_id`:
  every NDI document already has a `base.session_id` holding the session id, a
  different value from the session entity document's id.
- There is no `session_id` field. A first draft had one (the id NDI opens the
  session with), and `check_duplicate_field_declarations` refused it beside
  `base.session_id`. It was redundant as well: finding the `entity_id` document
  in `path` shows the folder holds this session, and that document's own
  `base.session_id` is the id to open it with.
- `must_refer_to_document_class` cannot require type `session` (every entity is
  class `entity`); the reader checks the type when it opens the link.
- The dataset check resolves `entity_id` by opening `path`, not in its own
  database.

### How NDI would use it

- **List** a dataset's sessions: those `part_of` it, directly or through a study.
- **Open** one: if a `linked_session` names it, open `path` and find the
  `entity_id` document there (a folder without it holds another session, and is
  reported); else it is ingested, opened from the dataset's database.
- **Search**: the dataset's database, then each linked session's.
- **Linked to ingested**: copy the documents in, delete the `linked_session`.
  **Ingested to linked**: write the documents out to a folder, add one.
- **Files**, separately, per file (the existing `ingest` flag on each file):
  copied into the dataset's store, or by location. A step that copies every
  by-location file in makes a dataset self-contained, before it is shared.

### Not decided here

- **Merging shared entities** when a session made on its own (with its own
  strain, people, software) joins a dataset: for an ingested session, merge and
  move the pointers inside the dataset; for a linked one, rewrite pointers inside
  the session's folder, or keep both and relate them. A later decision.
- **NDI changes** (listing from `part_of`, opening and searching linked
  sessions, add / convert, the self-contained step): built after this is signed.

To be signed: membership of a session in a dataset is a part_of relation (to the dataset or a study of it); a linked session's location is a `linked_session` configuration document (path, entity_id)
TEAM-SIGN-OFF: jess / 2026-10-09 -- membership of a session in a dataset is a part_of relation (to the dataset or a study of it); a linked session's location is a linked_session configuration document (path, entity_id)

Decided by Jess Haley, 2026-10-25 [linked_session withdrawn]: ("I don't think we want a linked_session. That's an old decision. Sessions are always entities"; "Yes, record both") the second half of the 2026-10-09 sign-off above is withdrawn: there is no `linked_session` document. Whether a session is linked or ingested, and a linked session's location, are the method of its `part_of` membership relation (did_v2_go_forward_class_audit.md [session membership records linked or ingested]). The first half (membership is a part_of relation) stands. `draft/linked_session.json` is removed. Built: NDI-matlab 915bbb3 (#1103: `writeDataset` and the dataset helpers write the relation's method instead; `datasetDatabaseFiles.m` and `datasetSessions.m` read it, falling back to an older `linked_session`); DID-matlab writes none (checked at V2 3c6c4d70); did-schema (`draft/linked_session.json` removed, the name in RETIRED_CLASSES).

Decided by Jess Haley, 2026-10-23 [nested studies]: a study may be included_in a parent study (Haley #144), and a session filed under a study at any depth is in the dataset; membership follows included_in up through every study to the dataset ("yes, do it", after the full Haley import left the 28 sessions of large_single_patch and small_single_patch, both filed under single_patch_assays, unlisted). Amends [the TEAM-SIGN-OFF of 2026-10-09 above], whose "to the dataset or a study of it" read one study deep. Built: NDI-matlab d1f1358c6

Decided by Jess Haley, 2026-10-31 [older linked_session reader deleted]: ("No. You can delete both", asked whether any dataset written 2026-10-09..10-14 by the Haley import, which then wrote `linked_session` documents by default, is still in use, and if not whether to delete both the NDI-matlab test `TestLinkedSessions/testAnOlderLinkedSessionDocumentIsStillRead` and the NDI code that reads an older `linked_session` document) no dataset holding a `linked_session` document is in use, so NDI-matlab no longer reads one: the fallback kept by the build of [linked_session withdrawn] is deleted, with its test. Answers docs/V2_PLAN.md L1. Build pending: NDI-matlab (delete the test and the `linked_session` reads in `+ndi/+setup/+V2/datasetDatabaseFiles.m`, `+ndi/+v2/datasetSessions.m` and `ndi.dataset` `v2EntityIdOf`)
