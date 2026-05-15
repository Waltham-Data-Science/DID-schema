import { useState } from "react";
import { clearAuth, saveAuth, validateToken } from "./auth";
import type { AuthState } from "./auth";

const PAT_NEW_URL =
  "https://github.com/settings/personal-access-tokens/new";

interface AuthPanelProps {
  auth: AuthState | null;
  onAuth: (state: AuthState | null) => void;
}

export function AuthPanel({ auth, onAuth }: AuthPanelProps) {
  const [expanded, setExpanded] = useState(false);
  const [token, setToken] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (auth) {
    return (
      <div className="auth-panel signed-in">
        {auth.avatar_url ? (
          <img
            className="auth-avatar"
            src={auth.avatar_url}
            alt=""
            width={20}
            height={20}
          />
        ) : null}
        <span className="auth-user">
          Signed in as <strong>@{auth.login}</strong>
        </span>
        <button
          className="auth-signout"
          onClick={() => {
            clearAuth();
            onAuth(null);
          }}
        >
          Sign out
        </button>
      </div>
    );
  }

  if (!expanded) {
    return (
      <div className="auth-panel">
        <button className="auth-signin" onClick={() => setExpanded(true)}>
          Sign in to GitHub
        </button>
      </div>
    );
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setBusy(true);
    try {
      const state = await validateToken(token);
      saveAuth(state);
      onAuth(state);
      setToken("");
      setExpanded(false);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <form className="auth-panel auth-form" onSubmit={handleSubmit}>
      <label className="auth-label" htmlFor="auth-token">
        Personal access token
      </label>
      <input
        id="auth-token"
        type="password"
        autoComplete="off"
        spellCheck={false}
        placeholder="github_pat_…"
        value={token}
        onChange={(e) => setToken(e.target.value)}
        disabled={busy}
      />
      <p className="auth-help">
        Prototype auth: paste a fine-grained PAT scoped to{" "}
        <code>Waltham-Data-Science/DID-schema</code> with{" "}
        <strong>Contents</strong>, <strong>Issues</strong>, and{" "}
        <strong>Pull requests</strong> set to <em>Read and write</em>. The
        token stays in this tab's sessionStorage and disappears when the
        tab closes.{" "}
        <a href={PAT_NEW_URL} target="_blank" rel="noreferrer">
          Create a token →
        </a>
      </p>
      {error ? <div className="auth-error">{error}</div> : null}
      <div className="auth-form-actions">
        <button type="submit" disabled={busy || !token.trim()}>
          {busy ? "Verifying…" : "Sign in"}
        </button>
        <button
          type="button"
          onClick={() => {
            setExpanded(false);
            setToken("");
            setError(null);
          }}
          disabled={busy}
        >
          Cancel
        </button>
      </div>
    </form>
  );
}
