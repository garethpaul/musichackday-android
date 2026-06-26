# Changes

## 2026-06-26 10:25 PDT - P1 - Disable album-art redirects

### Summary

Disabled automatic redirects on the direct album-art `HttpURLConnection` so
the reviewed HTTPS URL remains the only network destination for that request.

### Files changed

- `RdioApp.java` — disabled per-connection redirects before connect.
- `tests/test_android_baseline.py` — required the redirect guard before connect.
- `scripts/check-android-baseline.py`, `tests/test_reviewed_hashes.py`, and
  `Makefile` — synchronized reviewed bytes and the protected test inventory.
- `README.md`, `SECURITY.md`, `VISION.md`, and the implementation plans —
  documented the fail-closed redirect boundary.

### Tests

- RED: the focused contract failed because redirects were left at their default.
- Full SDK-free verification will be recorded in the implementation plan.

### Findings

- Android documents that `HttpURLConnection` follows redirects by default.
- The existing HTTPS check covered only the initial URL, not a redirected target.

### Blockers

- No legacy Android SDK/emulator is available; runtime media behavior remains
  outside the static verification claim.

### Next action

- Require exact-head hosted static checks and CodeQL before merge.

## 2026-06-26

- Guarded `DynamicImageView` aspect-ratio measurement behind positive drawable
  intrinsic dimensions, falling back to platform measurement otherwise.
- Added three mutation-sensitive contract tests for valid, zero-width, and
  zero-height guard behavior; the protected SDK-free suite now runs 97 tests.
- Updated README, security guidance, roadmap, and the completed implementation
  plan. Android runtime layout verification remains unavailable in this legacy
  SDK-free environment.

## 2026-06-21

- Preserved the complete checkout root for absolute Makefile paths containing
  spaces, brackets, or apostrophes, and rejected `MAKEFILE_LIST` overrides.
- Expanded the protected SDK-free baseline from 91 to 94 tests with hostile
  path and root-override regression coverage.

## 2026-06-10

- Added an album art connection guard with HTTPS-only transport, 10-second
  connect/read timeouts, sanitized failures, and deterministic cleanup.
- Added a stream copy failure guard so `Utils.CopyStream` reports read/write
  failures instead of silently accepting partial copies.
- Added credential-free checkout and location-independent Make verification
  while preserving the protected SDK-free baseline.
- Added Twitter authorization origin, login in-flight, callback exchange
  in-flight, callback state snapshot, UI-thread navigation, and credential
  persistence guards.
- Added Rdio authorization in-flight, credential persistence, sanitized
  authorization/API/playback failures, and cleanup lifecycle guards.
- Added Twitter search failure handling, UI-thread list lookup, and TweetAdapter
  rendering error redaction.
- Added an HTTPS profile image guard so Twitter media uses the encrypted URL
  field and cleartext HTTP is rejected by the image loader.
- Added pinned, read-only Linux hosted validation for the SDK-free Android
  baseline without executing the obsolete Gradle toolchain.
- Added an OAuth callback token guard so callback tokens must match the active
  request token before Twitter verifier exchange.

## 2026-06-09

- Added `make lint`, `make test`, and `make build` aliases so the standard
  gate commands run the same SDK-free static baseline as `make check`.
- Added an HTTP image URL guard so image downloads only accept HTTP(S) media
  URLs.
- Added memory cache entry guards for cleared soft references and null cache
  writes.
- Added an OAuth callback URI guard so Twitter verifier exchange only resumes
  for the configured callback scheme and authority.
- Added an OAuth callback path guard so lookalike callback paths do not resume
  Twitter verifier exchange.
- Added an OAuth callback verifier guard so missing or blank verifier values do
  not trigger Twitter access-token exchange.
- Added sanitized OAuth error logging so Twitter login failures do not write
  exception messages or stack traces to Android logs.
- Removed tracked local editor metadata and added a baseline guard so `.idea`,
  `.vscode`, and `.iml` files stay out of source control.

## 2026-06-08

- Added a credential hygiene baseline for the legacy Android app.
- Added a safe `Constants.java.example` template for local Twitter/Rdio values.
- Removed OAuth event logs, OAuth access token/token secret values, and image-loader debug logging from Android log output.
- Disabled Universal Image Loader verbose logging in the application setup.
- Moved image cache files to app-private storage and removed the external
  storage permission.
- Switched URL-derived image cache names to SHA-256 cache filenames to avoid
  short Java hash collisions.
- Added image download guards for invalid media URLs and recycled row image views.
- Guarded callback handling when a Twitter OAuth request is not active.
- Pinned legacy Gradle/support-library versions, switched the wrapper URL to
  HTTPS, restored the wrapper executable bit, and disabled manifest backup.
- Added `make check` and a static Android baseline verifier.
- Kept signing artifacts ignored and checked that generated Android outputs are not tracked.
