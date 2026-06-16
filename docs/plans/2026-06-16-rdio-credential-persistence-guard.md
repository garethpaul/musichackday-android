# Rdio Credential Persistence Guard

## Status: Planned

## Context

The Rdio authorization result stores the returned token pair with synchronous
`SharedPreferences.Editor.commit()`, but ignores the boolean result and then
installs the credentials and prepares playback. A storage failure can therefore
create an authenticated in-memory state that disappears after restart.

## Objectives

- Require successful credential persistence before installing the Rdio token
  pair or preparing playback.
- Clear in-memory credential ownership and return on persistence failure.
- Keep failure logging action-level and free of token values.
- Make commit-result handling and terminal ordering mutation-sensitive in the
  SDK-free baseline.

## Scope

- Update the Rdio authorization result path in `RdioApp.java`.
- Extend `scripts/check-android-baseline.py` with persistence and ordering
  contracts.
- Update maintained security guidance and change history.

## Verification

- Python checker compilation and focused SDK-free baseline
- Repository-root and external-directory `make check`
- Isolated mutations removing or reordering commit-result handling
- Exact diff, artifact, secret-like addition, conflict-marker, whitespace, and
  file-mode audits

## Risks

- Credential values must never appear in failure logs.
- Failed persistence must stop before SDK credential installation and playback.
- Existing successful authorization behavior must remain unchanged.

## Out Of Scope

- Provider endpoints, OAuth credential formats, encrypted storage migration,
  dependency upgrades, and live Rdio/Twitter authentication.
