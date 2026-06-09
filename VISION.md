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
- Keep the HTTP image URL guard before loading remote media
- Keep memory cache entry guards for cleared references and null writes
- Keep legacy build coordinates pinned for reproducible archaeology
- Maintain old Android build context for future inspection

Next priorities:

- Document Android SDK and Gradle requirements
- Modernize or retire deprecated Twitter/Rdio dependencies in a dedicated pass
- Add tests or manual verification notes for login and API flows

Contribution rules:

- One PR = one focused auth, API, build, or documentation change.
- Do not commit real credentials or generated signing files.
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
Media cache entries should keep using SHA-256 cache filenames so URL-derived
names remain deterministic without short Java hash collisions.

## What We Will Not Merge (For Now)

- Real API keys, secrets, or tokens
- Silent account actions
- Broad Android migration bundled with auth behavior changes
- Private API responses or user account data

This list is a roadmap guardrail, not a permanent rule.
Strong user demand and strong technical rationale can change it.
