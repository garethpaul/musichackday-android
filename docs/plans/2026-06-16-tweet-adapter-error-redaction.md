# Tweet Adapter Error Redaction

status: completed

## Problem

`TweetAdapter` prints a full stack trace when a search-result row contains
malformed JSON. Android logs can outlive the rendering attempt and may expose
provider or parsing context that is not needed to diagnose a dropped row.

## Scope

- Replace adapter JSON stack traces with a fixed action-level log message.
- Preserve successful row rendering and the current malformed-row fallback.
- Add a mutation-sensitive static contract and synchronized maintenance
  guidance.
- Do not change result ordering, adapter recycling, image loading, OAuth state,
  credentials, or dependency versions.

## Implementation Units

### U1: Redact malformed-row diagnostics

Update `app/src/main/java/com/twitterdev/rdio/app/TweetAdapter.java` so its
`JSONException` path emits only a constant message and never passes exception
details or stack traces to Android logging.

Test scenarios:

- A malformed row reaches the catch path and records the fixed adapter failure
  message.
- A mutation restoring `printStackTrace()` or exception-bearing logging is
  rejected.
- Valid rows retain their existing text and profile-image rendering flow.

### U2: Preserve the redaction contract

Extend `scripts/check-android-baseline.py` and the project guidance so the
adapter-specific redaction remains visible in local and hosted validation.

Test scenarios:

- All SDK-free Make gates accept the completed implementation.
- Mutations removing the fixed log, restoring a stack trace, removing the
  checker contract, or leaving this plan incomplete are rejected.
- The absolute Makefile path continues to run successfully outside the
  checkout.

## Validation

- Run checker compilation and all SDK-free Make gates from the checkout, plus
  the canonical gate through the absolute Makefile path from another directory.
- Run isolated hostile mutations for the source, checker, documentation, and
  completed-plan requirements.
- Audit the exact diff, generated artifacts, secrets, conflict markers,
  binaries, large files, and whitespace before committing.

## Risks

- Malformed rows retain the existing fallback behavior; this change only
  reduces diagnostic detail.
- Android SDK and device execution remain outside the dependency-free Linux
  baseline.
- This change is stacked on the open Rdio credential persistence pull request,
  which must remain open and merge first.

## Work Completed

- Replaced the adapter's malformed-row stack trace with a constant Android log
  message that carries no exception details.
- Added an adapter-specific static contract that rejects stack traces,
  exception messages, exception-bearing log overloads, and missing fixed-log
  behavior.
- Synchronized README, security, vision, and change guidance around the named
  redaction boundary.

## Verification Completed

- All four SDK-free Make gates passed from the checkout, and the canonical
  check passed from an external directory through the absolute Makefile path.
- Six isolated hostile mutations were rejected across restored stack traces,
  exception-bearing logging, missing fixed logging, README guidance, change
  history, and completed plan status.
- Checker compilation, exact diff review, generated-artifact inspection,
  secret-pattern scanning, conflict-marker checks, and binary and large-file
  audits passed.
- The SDK-free Linux baseline did not invoke the Android SDK, emulator, device,
  OAuth providers, Rdio, Twitter, or image downloads.
