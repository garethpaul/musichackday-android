# Changes

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
