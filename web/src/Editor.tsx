import { useEffect, useMemo, useRef, useState } from "react";
import Form from "@rjsf/core";
import type { IChangeEvent } from "@rjsf/core";
import validator from "@rjsf/validator-ajv8";
import type { FieldProps, RJSFSchema, UiSchema } from "@rjsf/utils";
import type { IndexEntry } from "./types";

const BASE = import.meta.env.BASE_URL;

// Starter document satisfying the meta-schema's top-level "required" keys.
// All fields are intentionally blank/minimal so the form opens cleanly and
// the user can fill in real values.
const BLANK_SCHEMA = {
  document_class: {
    class_name: "",
    class_version: "0.1.0",
    superclasses: [{ class_name: "base" }],
    maturity_level: "draft",
  },
  depends_on: [],
  fields: [],
};

interface EditorProps {
  index: IndexEntry[];
  /** The schema set being browsed. The editor authors FOR this set, so it must
   *  validate against THIS set's meta-schema -- see the note below. */
  version: string | null;
  onCancel: () => void;
}

export function Editor({ index, version, onCancel }: EditorProps) {
  const [metaSchema, setMetaSchema] = useState<RJSFSchema | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [formData, setFormData] = useState<unknown>(BLANK_SCHEMA);
  const [errorCount, setErrorCount] = useState<number | null>(null);

  // THIS FETCH WAS PINNED TO `V_delta` while every other panel followed the
  // set-version selector, so the editor validated new V_eta schemas against a
  // meta-schema two sets old.
  //
  // It is not a cosmetic mismatch. V_eta's meta-schema is a strict SUPERSET of
  // V_delta's -- 46 paths added, 0 removed -- and the additions are precisely
  // what this migration built: `min_count` / `max_count` (edge-family
  // cardinality), `ndi_mustBeNonEmpty` on a dependency, `referent_unique_by`,
  // and the whole `binding` constraint. V_delta's `dependency_object` declares
  // `additionalProperties: false`, so a dependency carrying any of the first
  // four is not merely unhinted, it is reported as an ILLEGAL PROPERTY.
  //
  //     DENOMINATOR: 245 V_eta schema files; 55 use at least one of the four
  //       ndi_mustBeNonEmpty  43    min_count  14    max_count  2
  //       referent_unique_by   3
  //
  // So 55 of the classes already in the tree could not have been authored in
  // this editor -- including `subject_interaction`, `subject_observation` and
  // `epoch`, three of the spine classes a new author is most likely to imitate.
  // The editor would have taught the schema's own rules wrong.
  //
  // All four sets carrying an `index.json` ship `stable/did_schema_meta.json`
  // (V_delta, V_epsilon, V_zeta, V_eta), so following the selector cannot 404
  // on any set the version picker can reach. If a future set omits one, the
  // error surfaces in the panel below rather than silently falling back to an
  // older meta-schema -- a wrong validator is worse than a missing one,
  // because only one of the two announces itself.
  useEffect(() => {
    if (!version) return;
    let cancelled = false;
    fetch(`${BASE}schemas/${version}/stable/did_schema_meta.json`)
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then((raw) => {
        if (!cancelled) setMetaSchema(prepareMetaSchema(raw, index));
      })
      .catch((e) => {
        if (!cancelled) setLoadError(`${version}: ${String(e)}`);
      });
    return () => {
      cancelled = true;
    };
  }, [index, version]);

  const filename = useMemo(() => {
    const name =
      (formData as { document_class?: { class_name?: string } })
        ?.document_class?.class_name ?? "";
    return name ? `${name}.json` : "new_schema.json";
  }, [formData]);

  const handleChange = (e: IChangeEvent) => {
    setFormData(e.formData);
    setErrorCount(e.errors?.length ?? 0);
  };

  const handleDownload = () => {
    const text = JSON.stringify(formData, null, 2);
    const blob = new Blob([text], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  if (loadError) {
    return (
      <div className="editor">
        <div className="editor-header">
          <h2>New schema</h2>
          <button onClick={onCancel}>Cancel</button>
        </div>
        <div className="fatal">Failed to load meta-schema: {loadError}</div>
      </div>
    );
  }

  if (!metaSchema) {
    return (
      <div className="editor">
        <div className="editor-header">
          <h2>New schema</h2>
          <button onClick={onCancel}>Cancel</button>
        </div>
        <div className="loading">Loading meta-schema...</div>
      </div>
    );
  }

  const valid = errorCount === 0;
  return (
    <div className="editor">
      <div className="editor-header">
        <div>
          <h2>New schema</h2>
          {/* NAMES THE SET IT ACTUALLY USED. The old copy read "the V_delta
              meta-schema" as a fixed string; once the fetch follows the
              selector, a fixed name here would be a caption describing a
              different validator from the one that produced the errors below
              it -- which is worse than the pinning it replaced, because it
              reads as confirmation. */}
          <p className="editor-sub">
            Filled-in fields are validated live against the{" "}
            <strong>{version ?? "—"}</strong> meta-schema. Click{" "}
            <strong>Download JSON</strong> when ready; submission to GitHub
            comes in a later step.
          </p>
        </div>
        <div className="editor-header-actions">
          <span
            className={`editor-status ${
              errorCount === null
                ? "pending"
                : valid
                  ? "valid"
                  : "invalid"
            }`}
          >
            {errorCount === null
              ? "Not validated yet"
              : valid
                ? "Valid"
                : `${errorCount} validation error${errorCount === 1 ? "" : "s"}`}
          </span>
          <button onClick={handleDownload} className="btn-primary">
            Download JSON
          </button>
          <button onClick={onCancel}>Cancel</button>
        </div>
      </div>
      <div className="editor-form">
        <Form
          schema={metaSchema}
          uiSchema={UI_SCHEMA}
          formData={formData}
          validator={validator}
          fields={{ JsonValue: JsonValueField }}
          onChange={handleChange}
          liveValidate
          showErrorList="bottom"
        >
          {/* Suppress rjsf's own submit button -- we use "Download JSON" instead. */}
          <></>
        </Form>
      </div>
    </div>
  );
}

// Prepare the meta-schema for rjsf:
//   * Inject the list of existing class_names as an enum on
//     `superclass_reference.class_name` so users get a dropdown of real
//     superclasses instead of free-text. Submitters can still propose
//     a new superclass by editing the JSON directly after download.
//   * Inject a `default: true` on `field_definition.queryable` so newly
//     added fields start queryable. This said "the common case for V_delta
//     schemas", naming a set two behind the default one; re-measured against
//     V_eta 2026-08-11 -- 450 field definitions across 245 files, 409
//     queryable (91%) -- so the default is still right and only the wording
//     was stale.
//   * Otherwise leave the meta-schema untouched -- rjsf understands the
//     standard JSON Schema vocabulary used here.
function prepareMetaSchema(
  raw: unknown,
  index: IndexEntry[],
): RJSFSchema {
  const cloned = JSON.parse(JSON.stringify(raw)) as RJSFSchema & {
    $defs?: Record<string, RJSFSchema>;
  };
  const superRef = cloned.$defs?.superclass_reference as
    | { properties?: { class_name?: RJSFSchema } }
    | undefined;
  const classNameField = superRef?.properties?.class_name;
  if (classNameField) {
    const names = index
      .map((e) => e.class_name)
      .filter((n) => n !== "did_schema_meta")
      .sort();
    classNameField.enum = names;
  }
  const fieldDef = cloned.$defs?.field_definition as
    | { properties?: Record<string, RJSFSchema> }
    | undefined;
  const queryable = fieldDef?.properties?.queryable;
  if (queryable) {
    queryable.default = true;
  }
  return cloned;
}

// Custom field for `blank_value` and `default_value`: the meta-schema
// places no `type` constraint on these (they accept any JSON value), and
// rjsf's default renderer bails on "no type" with an "Unsupported field
// schema" message. This field renders a text input that holds a JSON
// literal; the value flows back as a parsed JSON value on every keystroke
// that successfully parses. Empty input clears the value to undefined.
function JsonValueField(props: FieldProps) {
  const { formData, onChange, schema, name, required } = props;
  // Local text buffer so partial edits ("[1, ") don't get overwritten by
  // round-trip serialization of an old formData. We sync from formData
  // only when formData changed from a source other than our own keystroke.
  const [text, setText] = useState<string>(() => serializeJsonValue(formData));
  const [parseError, setParseError] = useState<string | null>(null);
  const lastEmittedRef = useRef<string>(text);

  useEffect(() => {
    const incoming = serializeJsonValue(formData);
    if (incoming !== lastEmittedRef.current) {
      setText(incoming);
      setParseError(null);
      lastEmittedRef.current = incoming;
    }
  }, [formData]);

  const handle = (raw: string) => {
    setText(raw);
    lastEmittedRef.current = raw;
    if (raw.trim() === "") {
      setParseError(null);
      onChange(undefined, []);
      return;
    }
    try {
      const parsed = JSON.parse(raw);
      setParseError(null);
      onChange(parsed, []);
    } catch (err) {
      setParseError((err as Error).message);
      // Don't propagate; leave formData at its previous valid value
      // so meta-schema validation reflects last good state.
    }
  };

  const label = humanLabel(name);
  return (
    <div className="json-value-field">
      <label>
        {label}
        {required ? <span className="req">*</span> : null}
      </label>
      <input
        type="text"
        value={text}
        spellCheck={false}
        placeholder='e.g. "" or 0 or null or [] or {}'
        onChange={(e) => handle(e.target.value)}
      />
      {parseError ? (
        <div className="json-value-error">Invalid JSON: {parseError}</div>
      ) : null}
      {schema.description ? (
        <div className="field-description">
          {schema.description} Enter as a JSON literal (strings in quotes,
          arrays as <code>[...]</code>, objects as <code>{`{...}`}</code>).
        </div>
      ) : null}
    </div>
  );
}

function serializeJsonValue(v: unknown): string {
  if (v === undefined) return "";
  try {
    return JSON.stringify(v);
  } catch {
    return "";
  }
}

function humanLabel(name: string): string {
  return name
    .split("_")
    .map((s) => (s ? s[0].toUpperCase() + s.slice(1) : ""))
    .join(" ");
}

// Recursive uiSchema fragment for `fields`. Applied at the top level of
// the document and inside any nested `structure`-type field, up to a fixed
// depth that comfortably covers realistic schema nesting.
function buildFieldsUiSchema(depth: number): UiSchema {
  if (depth <= 0) return {};
  return {
    "ui:options": { addable: true, removable: true, orderable: true },
    items: {
      blank_value: { "ui:field": "JsonValue" },
      default_value: { "ui:field": "JsonValue" },
      fields: buildFieldsUiSchema(depth - 1),
    },
  };
}

const UI_SCHEMA: UiSchema = {
  "ui:submitButtonOptions": { norender: true },
  document_class: {
    class_name: {
      "ui:help": "snake_case identifier. Must match ^[a-zA-Z][a-zA-Z0-9_]*$.",
    },
    class_version: {
      "ui:help": "Semantic version (e.g. 0.1.0).",
    },
    superclasses: {
      items: {
        "ui:options": { label: false },
        class_name: {
          "ui:placeholder": "Select a superclass",
        },
      },
    },
  },
  depends_on: {
    "ui:options": {
      addable: true,
      removable: true,
      orderable: false,
    },
  },
  fields: buildFieldsUiSchema(6),
};
