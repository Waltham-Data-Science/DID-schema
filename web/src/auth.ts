// Auth helpers for the prototype: a fine-grained Personal Access Token,
// pasted in by the developer, stored in sessionStorage so it disappears
// when the tab closes. No device flow until we want a smoother UX for
// outside contributors -- see PR discussion for Step 4 of issue #28.
//
// Token scopes the submitter needs (when granting the fine-grained PAT
// on github.com/settings/personal-access-tokens/new):
//   * Resource: only Waltham-Data-Science/DID-schema
//   * Repository permissions:
//       - Contents: Read and write   (push branch with new schema)
//       - Issues: Read and write     (open tracking issue)
//       - Pull requests: Read and write (open draft PR)
//   * Everything else: No access

const STORAGE_KEY = "did-schema:auth";

export interface AuthState {
  token: string;
  login: string;
  avatar_url: string;
}

export function loadAuth(): AuthState | null {
  try {
    const raw = sessionStorage.getItem(STORAGE_KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw) as Partial<AuthState>;
    if (!parsed.token || !parsed.login) return null;
    return {
      token: parsed.token,
      login: parsed.login,
      avatar_url: parsed.avatar_url ?? "",
    };
  } catch {
    return null;
  }
}

export function saveAuth(state: AuthState): void {
  sessionStorage.setItem(STORAGE_KEY, JSON.stringify(state));
}

export function clearAuth(): void {
  sessionStorage.removeItem(STORAGE_KEY);
}

// Validates a PAT by calling /user. api.github.com sends CORS headers,
// so this works from a static site. Returns the AuthState on success or
// throws an Error with a human-readable message.
export async function validateToken(token: string): Promise<AuthState> {
  const trimmed = token.trim();
  if (!trimmed) throw new Error("Token is empty.");
  const res = await fetch("https://api.github.com/user", {
    headers: {
      Authorization: `Bearer ${trimmed}`,
      Accept: "application/vnd.github+json",
      "X-GitHub-Api-Version": "2022-11-28",
    },
  });
  if (res.status === 401) {
    throw new Error("GitHub rejected the token (401). Check that the token is correct and not expired.");
  }
  if (!res.ok) {
    throw new Error(`GitHub returned ${res.status} when validating the token.`);
  }
  const body = (await res.json()) as { login?: string; avatar_url?: string };
  if (!body.login) {
    throw new Error("GitHub response did not include a login.");
  }
  return {
    token: trimmed,
    login: body.login,
    avatar_url: body.avatar_url ?? "",
  };
}
