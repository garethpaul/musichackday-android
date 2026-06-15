# Twitter Callback State Snapshot

Status: planned

## Problem

The OAuth callback validates its token against the current static
`requestToken`, then starts a worker that reads the static `twitter` and
`requestToken` fields later. The login button remains able to start a fresh
request-token flow while callback exchange is active. That flow can replace
both static fields after callback validation but before access-token exchange,
binding the verifier to different OAuth state.

## Approach

- Snapshot the validated `Twitter` and `RequestToken` objects before callback
  exchange ownership is acquired.
- Use only those final snapshots inside the access-token worker.
- Reject new request-token login acquisition while callback exchange ownership
  is active, before mutating login state or OAuth dependencies.
- Preserve callback URI, verifier, token, origin, duplicate-callback,
  UI-thread navigation, failure-release, credential storage, and Rdio behavior.

## Files

- `app/src/main/java/com/twitterdev/rdio/app/MainActivity.java`
- `scripts/check-android-baseline.py`
- `README.md`
- `SECURITY.md`
- `VISION.md`
- `CHANGES.md`
- `docs/plans/2026-06-15-twitter-callback-state-snapshot.md`

## Verification

- Add ordering-sensitive static contracts for snapshot timing, snapshot-only
  worker use, and callback-before-login ownership checks.
- Run the SDK-free lint, test, build, and check aliases plus external-directory
  verification.
- Reject isolated snapshot, worker-use, login-guard, ordering, guidance, and
  plan-status mutations.
- Audit the exact diff, dependencies, generated artifacts, binaries, large
  files, modes, credentials, conflicts, and whitespace.

## Scope Boundaries

- Do not change Twitter4J, OAuth callback parameters, credential persistence,
  provider origins, Rdio flow, dependencies, Gradle files, or the manifest.
- No Android SDK, emulator/device, provider, credential, or browser flow is
  available locally; keep verification SDK-free and record that limitation.
- Do not merge or close stacked pull requests without explicit authorization.

## Success Criteria

- The callback worker exchanges the verifier against the exact Twitter and
  request-token objects that passed callback validation.
- Login cannot replace callback OAuth dependencies while exchange ownership is
  active.
- Every existing terminal callback ownership release remains intact.
