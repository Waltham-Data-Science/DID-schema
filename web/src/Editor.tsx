import { useEffect, useMemo, useState } from "react";
import Form from "@rjsf/core";
import type { IChangeEvent } from "@rjsf/core";
import validator from "@rjsf/validator-ajv8";
import type { RJSFSchema, UiSchema } from "@rjsf/utils";
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
  onCancel: () => void;
}

export function Editor({ index, onCancel }: EditorProps) {
  const [metaSchema, setMetaSchema] = useState<RJSFSchema | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [formData, setFormData] = useState<unknown>(BLANK_SCHEMA);
  const [errorCount, setErrorCount] = useState<number | null>(null);

  useEffect(() => {
    fetch(`${BASE}schemas/V_delta/stable/did_schema_meta.json`)
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then((raw) => setMetaSchema(prepareMetaSchema(raw, index)))
      .catch((e) => setLoadError(String(e)));
  }, [index]);

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
          <p className="editor-sub">
            Filled-in fields are validated live against the V_delta
            meta-schema. Click <strong>Download JSON</strong> when ready;
            submission to GitHub comes in a later step.
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
  return cloned;
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
  fields: {
    "ui:options": {
      addable: true,
      removable: true,
      orderable: true,
    },
  },
};
