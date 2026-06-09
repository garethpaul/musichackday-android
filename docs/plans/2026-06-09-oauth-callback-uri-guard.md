# OAuth Callback URI Guard

status: completed

## Context

Twitter login resumes from a custom callback URL after the browser redirects
back to the app. The previous callback check used a string prefix match against
the configured callback, which was broader than the actual scheme and authority
contract.

## Objectives

- Match OAuth callback intents by exact configured scheme and authority.
- Avoid exchanging verifier values for lookalike callback URLs.
- Preserve the existing Twitter verifier exchange and Rdio handoff.
- Extend the SDK-free Android baseline and docs for callback guardrails.

## Verification

- `scripts/check-android-baseline.py`
- `make check`
- `git diff --check`
