# Guard the Rdio Authorization Flow

status: completed

## Problem

`RdioApp` starts OAuth authorization directly from both `onCreate` and
`LoadMoreTracks`. On a first run, `onCreate` launches authorization for missing
credentials and then immediately calls `playPause`; the empty queue reaches
`LoadMoreTracks` and launches a second authorization activity. The result
handler also calls `prepareForPlayback` after cancellation or malformed success
data, even though no valid credential pair was established.

## Requirements

- Route every Rdio authorization launch through one helper with an explicit
  in-flight guard.
- Preserve in-flight ownership across activity recreation while the OAuth
  activity is returning.
- Mark authorization in flight before launching and clear it for every returned
  result.
- Accept a successful result only when both token extras are present and
  nonblank.
- Save credentials, install them in the SDK, and prepare playback only after a
  valid successful result.
- On cancellation or malformed success, clear transient credentials, log only
  a fixed action-level message, and do not prepare playback.
- Preserve cached-credential startup, anonymous fallback behavior, request code,
  SDK integration, Twitter changes, and dependency versions.

## Implementation Units

### U1: Centralized authorization launch

Files:

- `app/src/main/java/com/twitterdev/rdio/app/RdioApp.java`

Add a private in-flight flag and a helper that creates the existing
`OAuth1WebViewActivity` intent only when no authorization request is active.
Use the helper from startup and queue-depletion paths.

### U2: Fail-closed result handling

Files:

- `app/src/main/java/com/twitterdev/rdio/app/RdioApp.java`

Clear the in-flight flag at the result boundary. Require both returned token
values to be nonblank before persisting or preparing playback; otherwise clear
transient values and return without SDK preparation.

### U3: Portable contracts and guidance

Files:

- `scripts/check-android-baseline.py`
- `README.md`
- `SECURITY.md`
- `VISION.md`
- `CHANGES.md`
- `docs/plans/2026-06-15-rdio-authorization-flow-guard.md`

Require centralized launch ordering, both call sites, strict result validation,
fail-closed preparation, completed evidence, and maintenance documentation.

## Verification

- Compile and run the dependency-free checker plus all four Make gates from the
  checkout and the canonical check from an external directory.
- Reject isolated mutations that bypass the launch helper, remove the in-flight
  guard, accept blank tokens, prepare after failure, remove guidance, or reopen
  the plan.
- Audit the exact diff, Java/checker structure, Gradle/project integrity,
  generated artifacts, credential patterns, conflict markers, binaries, large
  files, and intended paths before commit.

## Risks

- The vendored Rdio SDK is obsolete and cannot be live-tested without retired
  service credentials; this change preserves its existing API surface.
- Authorization cancellation remains recoverable through the next explicit
  playback attempt because the in-flight flag is cleared on result.
- The stacked base pull request must remain available and merge first.

## Work Completed

- Added one guarded Rdio authorization launcher and routed both startup and
  queue-depletion paths through it.
- Saved and restored authorization ownership across activity recreation.
- Cleared the static SDK reference after lifecycle cleanup so recreation builds
  a live Rdio instance instead of reusing a cleaned object.
- Cleared authorization ownership at the result boundary and on launch failure.
- Rejected cancellation, missing result data, and blank token pairs before
  persistence, SDK credential installation, or playback preparation.
- Preserved cached-credential startup, the existing SDK request code and intent
  extras, anonymous fallback behavior, dependencies, and Twitter flows.
- Added portable static contracts and project guidance for launch ownership and
  fail-closed result handling.

## Verification Completed

- The checker compiled and passed. All four Make gates passed from the checkout,
  and the canonical check passed from an external directory through the absolute
  Makefile path.
- Eight isolated hostile mutations were rejected: bypassed launch helper,
  removed in-flight guard, dropped recreation state, retained a cleaned SDK
  reference, accepted blank tokens, prepared playback after failure, removed
  guidance, and stale plan status.
- `git diff --check`, exact intended-path, Java/checker structure,
  Gradle/project integrity, generated-artifact, credential-pattern,
  conflict-marker, binary, and large-file audits passed.
- No live Twitter, Rdio, OAuth, media, or other external service was contacted.
