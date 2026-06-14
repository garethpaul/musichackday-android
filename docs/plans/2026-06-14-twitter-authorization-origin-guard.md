# Twitter Authorization Origin Guard

status: completed

## Summary

Require the browser-bound Twitter OAuth authorization URI to use the expected
HTTPS Twitter origin and authenticate path before launching an external intent.

## Problem Frame

The login flow currently sends `RequestToken.getAuthenticationURL()` directly
to `Intent.ACTION_VIEW`. Twitter4J normally constructs the canonical URL, but
the application does not enforce that trust boundary if configuration or
library behavior drifts.

## Requirements

- Accept only HTTPS authorization URIs on `api.twitter.com` with the default
  port and `/oauth/authenticate` path.
- Reject null, malformed, cleartext, alternate-host, and alternate-path URIs
  before launching the browser.
- Preserve the existing request-token creation, callback binding, sanitized
  logging, and logged-in navigation behavior.
- Protect the boundary with the SDK-free checker and maintained documentation.

## Key Technical Decisions

- Parse the library-provided authorization URL once and validate its scheme,
  host, and path with an explicit helper before constructing the intent.
- Use the existing sanitized OAuth failure logger without exposing the rejected
  URL or request token.

## Implementation Units

### U1: Enforce the authorization origin

**Files:** `app/src/main/java/com/twitterdev/rdio/app/MainActivity.java`,
`scripts/check-android-baseline.py`

**Approach:** Add a focused URI predicate and require it immediately before
the outbound browser intent.

**Execution note:** Add the failing static contract before changing Java.

**Test scenarios:**

- The checker requires the exact HTTPS scheme, Twitter host, authenticate path,
  and guard before `startActivity`.
- Removing or weakening any origin component fails the SDK-free baseline.

**Verification:** The checker first fails against the unguarded flow, then all
Make aliases pass after implementation.

### U2: Document and preserve the boundary

**Files:** `README.md`, `SECURITY.md`, `VISION.md`, `CHANGES.md`,
`docs/plans/2026-06-14-twitter-authorization-origin-guard.md`

**Approach:** Record the browser-launch trust boundary and completed validation
without claiming an unavailable Android runtime or live OAuth exchange.

**Test scenarios:**

- Targeted hostile mutations reject missing documentation and incomplete plan
  evidence.

**Verification:** Documentation, plan, diff, artifact, and credential gates pass.

## Scope Boundaries

- Do not perform live Twitter authentication or introduce credentials.
- Do not upgrade the obsolete Android, Gradle, Twitter4J, or vendored SDK stack.
- Do not change callback URI semantics or token persistence.

## Work Completed

- Added a null-safe authorization URI predicate for the canonical HTTPS Twitter
  host, default port, and authenticate path.
- Required that predicate before constructing the external browser intent and
  reused the validated URI for launch.
- Extended the SDK-free baseline and maintained documentation with the outbound
  OAuth trust boundary.

## Verification Completed

- `make lint`, `make test`, `make build`, and `make check` passed from the
  checkout, and the absolute Makefile check passed from an external directory.
- The static contract failed against the original unguarded browser launch and
  passed after implementation.
- Eight hostile mutations covering scheme, host, port, path, pre-launch guard,
  intent URI reuse, documentation, and completed plan evidence were rejected.
- No Android SDK build, emulator run, credential use, or live OAuth exchange was
  performed.
