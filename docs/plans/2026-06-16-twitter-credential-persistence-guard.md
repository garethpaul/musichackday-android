# Twitter Credential Persistence Guard

Status: completed

## Priority

P1 authentication integrity. A completed provider exchange must not enter the
authenticated app flow unless the returned Twitter credentials were stored.

## Problem

The callback worker writes the OAuth token, secret, and logged-in flag with
`SharedPreferences.Editor.commit()` but ignores its boolean result. If durable
storage fails, the activity still releases callback ownership and launches
`RdioApp`, even though the next process or activity cannot recover the session.

## Approach

- Treat a false `commit()` result as a terminal callback failure.
- Release callback-exchange ownership, emit only sanitized action-level logging,
  and return before UI navigation when persistence fails.
- Preserve callback URI, verifier, request-token, snapshot, concurrency, and
  UI-thread navigation guards.
- Add mutation-sensitive SDK-free contracts, maintained guidance, changelog,
  and completed verification evidence.

## Files

- `app/src/main/java/com/twitterdev/rdio/app/MainActivity.java`
- `scripts/check-android-baseline.py`
- `README.md`
- `SECURITY.md`
- `VISION.md`
- `CHANGES.md`
- `docs/plans/2026-06-16-twitter-credential-persistence-guard.md`

## Verification

- Run all repository and external-directory Make gates.
- Reject isolated unchecked-commit, missing-release, missing-return,
  navigation-order, guidance, changelog, and plan-completion mutations.
- Audit the exact diff, generated artifacts, credentials, conflict markers,
  binaries, large files, and whitespace.

## Scope Boundaries

- Do not change provider endpoints, callback matching, token exchange, request
  token ownership, preference keys, Rdio authorization, or dependency versions.
- Do not log tokens, secrets, exception messages, or raw provider data.
- The obsolete Android toolchain remains unexecuted on Linux; hosted SDK-free
  validation is canonical for the exact pushed head.
- Keep PR #16 and its predecessors open and retain base-first stack ordering.

## Success Criteria

- Failed credential persistence cannot navigate into `RdioApp`.
- Every failed persistence attempt releases callback ownership and remains
  retryable without exposing sensitive values.
- Successful persistence retains the existing UI-thread navigation behavior.

## Verification Completed

- All four Make gates passed from the repository root.
- The absolute Makefile `check` gate passed from an external directory.
- The Python baseline checker compiled with bytecode redirected outside the
  repository.
- Eight isolated hostile mutations were rejected across commit-result checks,
  ownership release, sanitized logging, terminal return, navigation ordering,
  maintained guidance, changelog evidence, and plan completion.
- Exact diff, generated-artifact, credential-pattern, conflict-marker, binary,
  large-file, and whitespace audits passed.
- The Android SDK, emulator, providers, credentials, and browser callback were
  not executed on Linux; the maintained SDK-free baseline passed instead.
