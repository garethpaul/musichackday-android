# OAuth Callback Path Guard

status: completed

## Context

Twitter login resumes through the configured custom callback URL. The callback
guard already compares the configured scheme and authority, but path-bearing
lookalikes can still reach verifier handling when the configured callback has
no path.

## Objectives

- Compare normalized callback paths before verifier exchange.
- Preserve the existing scheme and authority guard.
- Preserve OAuth verifier query-parameter handling.
- Extend the SDK-free Android baseline and docs for callback path guardrails.

## Verification

- `scripts/check-android-baseline.py`
- `make check`
- `git diff --check`
