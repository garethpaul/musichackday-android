# Twitter Navigation UI Thread Handoff

status: in progress

## Context

Twitter request-token creation and access-token exchange run on background
threads, but both success paths call `startActivity` directly from those worker
threads. Android navigation belongs on the activity main thread and can fail or
race with UI lifecycle work when invoked from a worker.

## Requirements

- Keep Twitter network and token operations off the main thread.
- Dispatch authorization-browser launch and successful Rdio navigation through
  `runOnUiThread` before calling `startActivity`.
- Preserve callback-origin, verifier, request-token, and authorization-URL
  validation before either navigation path.
- Preserve generic redacted failure logging and stored token behavior.
- Add method-scoped static contracts and maintenance guidance.

## Implementation

1. Wrap each background-thread navigation success path in an explicit UI-thread
   runnable owned by `MainActivity`.
2. Keep intent creation and `startActivity` together inside each runnable.
3. Extend the baseline checker with ordering-sensitive contracts for both paths.
4. Update operator, security, vision, and changelog guidance.

## Verification

- Run checker compilation and every non-destructive Make gate from the checkout
  plus the canonical rooted gate from an external directory.
- Verify isolated mutations that remove either UI handoff, move navigation
  outside its runnable, bypass prerequisite validation, remove guidance, or
  leave this plan incomplete are rejected.
- Run `git diff --check` and exact intended-path, generated-artifact,
  secret-pattern, conflict-marker, binary, and large-file audits.

## Risks

- Android SDK/Gradle execution is unavailable in this dependency-free Linux
  validation path, so the handoff is enforced structurally rather than on device.
- The stacked base pull request must remain available and merge first.

## Work Completed

- Pending implementation.

## Verification Completed

- Pending validation.
