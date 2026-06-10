# OAuth Callback Token Guard

status: completed

## Context

Twitter login resumes through a callback URI that carries both an
`oauth_token` and an `oauth_verifier`. The existing callback guards validate
the URI shape and verifier value, but the callback should also prove that it
belongs to the request token created by the current local login attempt.

## Objectives

- Read the callback `oauth_token` before exchanging verifier values.
- Reject callbacks whose token does not match the active Twitter request token.
- Preserve the existing callback URI, path, verifier, and sanitized logging
  guardrails.
- Extend the SDK-free Android baseline and docs for request-token binding.

## Verification

- `scripts/check-android-baseline.py`
- `make check`
- `git diff --check`
