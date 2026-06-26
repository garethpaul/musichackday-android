## Music Hack Day Android Vision

This document explains the current state and direction of the project.
Project overview and developer docs: [`README.md`](README.md)

Music Hack Day Android is a legacy Android hack-day app combining Twitter and
Rdio integration.

The repository is useful as a preserved short-form Android experiment with old
Gradle, Twitter OAuth, Rdio SDK jars, and local constants configuration. Project
context lives in [`README.md`](README.md).

The goal is to keep the hack understandable while making API credentials and
legacy dependency constraints explicit.

The current focus is:

Priority:

- Preserve the Twitter and Rdio integration structure
- Keep `Constants.java` local and untracked for real credentials
- Avoid committing OAuth tokens, API keys, or private callback configuration
- Keep OAuth access tokens and media-fetch debug details out of Android log output
- Keep media cache entries on SHA-256 cache filenames in app-private storage
- Keep image download guards around media URLs and recycled row image views
- Keep dynamic image measurement guarded by positive intrinsic dimensions
- Keep the HTTP image URL guard before loading remote media
- Keep the HTTPS profile image guard at both Twitter URL selection and image loading
- Keep the album art connection guard around playback artwork networking
- Keep album-art redirects disabled after the initial HTTPS validation
- Keep the stream copy failure guard around utility stream transfers
- Keep credential-free checkout and location-independent Make verification
- Keep memory cache entry guards for cleared references and null writes
- Keep `make lint`, `make test`, `make build`, and `make check` on the
  SDK-free static baseline
- Keep that SDK-free baseline pinned and read-only in hosted Linux validation
- Keep the OAuth callback URI guard exact before exchanging verifier values
- Keep the OAuth callback path guard exact before exchanging verifier values
- Keep the OAuth callback verifier guard strict before exchanging access tokens
- Keep the OAuth callback token guard bound to the active request token
- Keep sanitized OAuth error logging for Twitter login failures
- Keep Twitter and Rdio authorization state, credential persistence, UI-thread,
  playback, and rendering redaction guards in place
- Keep local editor metadata out of the shared Android project baseline
- Keep legacy build coordinates pinned for reproducible archaeology
- Maintain old Android build context for future inspection

Next priorities:

- Document Android SDK and Gradle requirements
- Modernize or retire deprecated Twitter/Rdio dependencies in a dedicated pass
- Add tests or manual verification notes for login and API flows

Contribution rules:

- One PR = one focused auth, API, build, or documentation change.
- Do not commit real credentials or generated signing files.
- Run `make lint`, `make test`, `make build`, and `make check` before pushing
  baseline, Gradle, credential, or media-loading changes.
- Verify behavior with local credentials for auth changes.
- Keep the hack-day scope clear and small.
- Preserve image download guards when changing media loading.

## Security

Canonical security policy and reporting:

- [`SECURITY.md`](SECURITY.md)

Twitter and Rdio credentials must stay out of source control. Callback URLs and
tokens should not be logged or embedded in public examples as real values.
Image download guards should keep invalid media URLs and recycled image views
from reaching the loader.
The HTTP image URL guard should keep local or non-web URI schemes out of image
loading.
The HTTPS profile image guard should keep profile media on encrypted transport
from Twitter URL selection through the loader boundary.
The album art connection guard should keep playback artwork on HTTPS with
bounded waits, disabled redirects, sanitized failures, and deterministic
network cleanup.
The stream copy failure guard should keep utility stream transfers from
silently accepting failed or partial copies.
Credential-free checkout and location-independent Make verification should keep
hosted and local validation scoped to the reviewed checkout.
Media cache entries should keep using SHA-256 cache filenames so URL-derived
names remain deterministic without short Java hash collisions.
The OAuth callback URI guard should keep Twitter verifier exchanges limited to
the configured callback scheme and authority.
The OAuth callback path guard should keep Twitter verifier exchanges limited to
the configured callback path.
The OAuth callback verifier guard should reject missing or blank verifier values
before exchanging for access tokens.
The OAuth callback token guard should keep verifier exchange bound to the
request token created by the local login attempt.
Sanitized OAuth error logging should keep Twitter login failures out of
exception-detail and stack-trace logs.
Twitter and Rdio authorization state, credential persistence, UI-thread,
playback, and rendering redaction guards should keep provider handoffs bounded
and sanitized.
Local editor metadata should stay ignored so IDE workspace choices do not
change the preserved Android project baseline.

## What We Will Not Merge (For Now)

- Real API keys, secrets, or tokens
- Silent account actions
- Broad Android migration bundled with auth behavior changes
- Private API responses or user account data

This list is a roadmap guardrail, not a permanent rule.
Strong user demand and strong technical rationale can change it.
