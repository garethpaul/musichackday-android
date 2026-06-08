# Music Hack Day Android Baseline Plan

status: completed

## Context

`musichackday-android` is a legacy Android hack-day app that combines Twitter
OAuth, Rdio playback, bundled SDK jars, and a local `Constants.java` credential
file that is intentionally not committed.

## Risks

- Real Twitter and Rdio keys must remain outside source control.
- OAuth access tokens and auth events were logged after successful login and
  Rdio authorization, and image-loader debug logging could expose fetched media
  URLs.
- The Gradle wrapper used an HTTP distribution URL and build files used dynamic
  dependency versions.
- The checked-in Gradle stack is too old to assume a modern machine can build it
  without a matching Android SDK, so the repo needs an SDK-free baseline check.

## Work Completed

- Added a safe `Constants.java.example` with fake placeholders and documented
  the copy-to-local workflow.
- Kept real `Constants.java`, signing keys, local properties, and generated
  Android artifacts ignored.
- Removed token, token-secret, auth-event, and image-loader debug log output.
- Disabled Android backup for the app manifest baseline.
- Moved image cache files to app-private storage and dropped the external
  storage permission.
- Pinned legacy Gradle/support dependencies and moved the wrapper URL to HTTPS.
- Added `make check` and `scripts/check-android-baseline.py` for XML, Gradle, manifest,
  credential, logging, and documentation guardrails.

## Verification

- `make check`
- `python3 scripts/check-android-baseline.py`
- `git diff --check`
