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
- Maintain old Android build context for future inspection

Next priorities:

- Add a safe `Constants.java.example` with clearly fake placeholders
- Document Android SDK and Gradle requirements
- Modernize or retire deprecated Twitter/Rdio dependencies in a dedicated pass
- Add tests or manual verification notes for login and API flows

Contribution rules:

- One PR = one focused auth, API, build, or documentation change.
- Do not commit real credentials or generated signing files.
- Verify behavior with local credentials for auth changes.
- Keep the hack-day scope clear and small.

## Security

Canonical security policy and reporting:

- [`SECURITY.md`](SECURITY.md)

Twitter and Rdio credentials must stay out of source control. Callback URLs and
tokens should not be logged or embedded in public examples as real values.

## What We Will Not Merge (For Now)

- Real API keys, secrets, or tokens
- Silent account actions
- Broad Android migration bundled with auth behavior changes
- Private API responses or user account data

This list is a roadmap guardrail, not a permanent rule.
Strong user demand and strong technical rationale can change it.
