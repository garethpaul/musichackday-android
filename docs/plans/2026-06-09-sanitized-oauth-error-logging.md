# Sanitized OAuth Error Logging

status: completed

## Context

`MainActivity` handled Twitter login failures by printing stack traces or
logging exception messages. OAuth provider exceptions can include request or
response details that should not be written to Android logs in a credential
adjacent flow.

## Objectives

- Replace Twitter login stack traces with fixed action-level log messages.
- Avoid logging exception message text from OAuth callback handling.
- Preserve the existing callback URI, path, and verifier guards.
- Extend the SDK-free Android baseline and docs so OAuth failures stay
  sanitized.

## Verification

- `scripts/check-android-baseline.py`
- `make lint`
- `make test`
- `make build`
- `make check`
- `git diff --check`
