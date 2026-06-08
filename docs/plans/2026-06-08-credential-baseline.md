# Credential Baseline Plan

status: completed

## Context

`musichackday-android` is a legacy Android hack-day project that depends on
Twitter OAuth and Rdio credentials. The real `Constants.java` file is ignored,
but the repository did not include a safe template or a local verification gate
for credential hygiene.

## Objectives

- Add a committed `Constants.java.example` with obviously fake placeholders.
- Keep the real `Constants.java` ignored for local credentials.
- Stop logging OAuth access tokens and token secrets.
- Guard callback handling when the OAuth request token is not present.
- Disable library-level verbose image-loader logging.
- Add a host-portable `make check` command that does not require an Android SDK.
- Pin legacy Gradle/support-library coordinates instead of wildcard versions.
- Keep the Gradle wrapper distribution URL on HTTPS.
- Keep the checked-in Gradle wrapper executable.
- Disable Android manifest backup for this credential-adjacent sample app.
- Store image cache files in app-private cache storage and avoid the external
  storage permission.
- Document the local setup and verification path in README, VISION, and changes.

## Verification

- `make check`
- `python3 scripts/check-android-baseline.py`
- `git diff --check`
