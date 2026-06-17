# Playback Error Redaction

status: planned

## Problem

The background playback preparation path concatenates the caught exception into
an Android error log. Provider and media failures can include request or SDK
context that is not required to diagnose the user-visible outcome and should
not be retained in device logs.

## Scope

- Replace playback exception details with one fixed action-level log message.
- Preserve the existing failed-playback control flow.
- Add a mutation-sensitive static contract and synchronized maintenance
  guidance.
- Do not change queue ordering, player lifecycle, OAuth state, credentials,
  provider requests, dependencies, or Android SDK configuration.

## Implementation Units

### U1: Redact playback diagnostics

Update `app/src/main/java/com/twitterdev/rdio/app/RdioApp.java` so the playback
preparation catch path logs only a fixed message through the class tag and
never includes the exception object, message, or stack trace.

Test scenarios:

- Playback preparation failure emits the fixed redacted message.
- A mutation restoring exception concatenation or exception-bearing logging is
  rejected.
- Successful playback preparation remains unchanged.

### U2: Preserve the redaction contract

Extend `scripts/check-android-baseline.py` and project guidance so the playback
redaction boundary remains visible in local and hosted validation.

Test scenarios:

- All SDK-free Make gates accept the implementation.
- Mutations removing the fixed log, restoring exception details, removing the
  checker contract, or leaving this plan incomplete are rejected.
- The absolute Makefile path continues to run successfully outside the
  checkout.

## Validation

- Run checker compilation and all SDK-free Make gates from the checkout, plus
  the canonical gate through the absolute Makefile path from another directory.
- Run isolated hostile mutations for source, checker, documentation, and
  completed-plan requirements.
- Audit the exact diff, generated artifacts, secrets, conflict markers,
  binaries, large files, and whitespace before committing.

## Risks

- Playback failures retain less diagnostic detail, intentionally matching the
  repository's other provider-error boundaries.
- Android SDK and device execution remain outside the dependency-free Linux
  baseline.
- This change is stacked on the open tweet-adapter error-redaction pull request,
  which must remain open and merge first.
