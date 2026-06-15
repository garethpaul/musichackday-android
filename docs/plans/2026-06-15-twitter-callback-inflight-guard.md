# Guard Concurrent Twitter Callback Exchanges

Status: completed

## Problem

A valid Twitter OAuth callback starts an access-token exchange without claiming
ownership across activity instances. Activity recreation can therefore process
the same callback and static request token again while the first exchange is
still active, creating duplicate provider requests, preference writes, and
navigation attempts.

## Scope

- Reject a valid callback while another access-token exchange is active.
- Acquire ownership on the activity UI thread before starting provider work.
- Preserve ownership across activity recreation with process-wide state.
- Release ownership on sanitized failure and immediately before successful
  navigation.
- Preserve callback origin, verifier, request-token, credential-storage, and UI
  thread boundaries.
- Add mutation-sensitive static contracts and synchronized guidance.

## Verification

- Run checker compilation and all four Make gates from the repository plus the
  canonical check from an external directory with explicit timeouts.
- Reject isolated mutations for missing overlap rejection, missing acquisition,
  instance-only ownership, missing success/failure release, missing guidance,
  and stale plan status.
- Audit the exact diff, generated artifacts, credential patterns, dependency
  files, conflict markers, binaries, large files, and intended paths.

## Risks

- Process death still discards the retired SDK's in-memory request token and is
  outside this narrow concurrency boundary.
- No Android runtime, Twitter provider, credential, or browser flow is
  available in this Linux environment.
- The change must remain stacked on PR #14; neither pull request may be merged
  or closed without explicit owner authorization.

## Work Completed

- Added process-wide access-token exchange ownership after the existing
  callback origin, verifier, active-request, and token-identity checks.
- Rejected duplicate valid callbacks before creating provider work.
- Released ownership on worker failure, setup failure, and immediately before
  successful UI-thread navigation.
- Added ordered static contracts and synchronized maintenance guidance.

## Verification Completed

- All four Make gates passed from the repository and the canonical check passed
  from an external directory through the absolute Makefile path.
- The baseline checker compiled and passed without requiring an Android SDK.
- Eight isolated hostile mutations were rejected for missing overlap rejection,
  missing acquisition, instance-only ownership, missing success release,
  missing worker-failure release, missing setup-failure release, missing
  guidance, and stale plan status.
- Exact diff, generated-artifact, credential-pattern, dependency-file,
  conflict-marker, binary, large-file, whitespace, and intended-path audits
  passed.
- No Twitter, Rdio, credential, browser, or Android runtime was contacted.
