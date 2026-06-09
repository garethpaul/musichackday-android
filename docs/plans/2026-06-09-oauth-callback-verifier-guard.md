# OAuth Callback Verifier Guard

status: completed

## Context

Twitter login resumes through a callback URI that carries an
`oauth_verifier` query parameter. The callback URI guard rejects lookalike
endpoints, but a callback with an empty verifier value should also stop before
requesting access tokens.

## Objectives

- Reject missing or blank OAuth verifier values before token exchange.
- Preserve the existing scheme, authority, and path callback guards.
- Preserve the user-facing fallback message for callbacks that cannot resume
  login.
- Extend the SDK-free Android baseline and docs for verifier guardrails.

## Verification

- `scripts/check-android-baseline.py`
- `make check`
- `git diff --check`
