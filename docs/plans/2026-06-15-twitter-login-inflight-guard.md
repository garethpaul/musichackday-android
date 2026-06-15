# Guard Concurrent Twitter Login Attempts

Status: Planned

## Summary

Prevent repeated login taps from starting overlapping Twitter request-token
threads and launching duplicate authorization browser intents.

## Problem

`loginToTwitter()` starts a worker for every tap while logged out. Concurrent
workers share the static Twitter and request-token fields, so a later worker can
replace the token associated with an earlier browser handoff and make the OAuth
callback fail identity validation.

## Requirements

- Reject a new logged-out login attempt while request-token creation is active.
- Acquire attempt ownership on the activity UI thread before starting work.
- Release ownership on request-token failure, rejected authorization origin,
  and immediately before the validated browser navigation.
- Keep network and token work off the UI thread and preserve existing origin,
  callback-token, sanitized logging, and navigation-thread boundaries.
- Add ordered, mutation-sensitive static contracts and matching documentation.

## Implementation

- Add an activity-owned in-flight flag and a UI-thread release helper.
- Guard and acquire the flag before constructing the request-token worker.
- Route failure paths through the release helper and release successful
  ownership inside the existing UI navigation runnable.
- Extend the dependency-free checker, guidance, changelog, and plan evidence.

## Verification

- Run repository and external-directory `make check`.
- Reject isolated mutations removing the guard, acquisition, successful release,
  failure release, ordering, documentation, or completed-plan status.
- Audit the exact diff, checker syntax, whitespace, generated artifacts,
  conflict markers, and changed-line credential patterns.

## Risks

- Android SDK, emulator/device, Twitter, Rdio, and live OAuth behavior are not
  available in this Linux environment and must remain unclaimed.
- The change must remain stacked on PR #11; neither pull request may be merged
  or closed without explicit owner authorization.
