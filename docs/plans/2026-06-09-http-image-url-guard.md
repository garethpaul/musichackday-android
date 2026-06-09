# HTTP Image URL Guard

status: completed

## Context

`ImageDownload` guarded missing and broadly invalid image URLs before handing
work to Universal Image Loader. The app only expects remote media URLs, so
non-HTTP(S) schemes such as local files should fail before image loading.

## Objectives

- Restrict image download inputs to HTTP and HTTPS URLs.
- Preserve the existing missing-URL and recycled-`ImageView` guards.
- Extend the static Android baseline so the URL scheme guard remains visible
  without an Android SDK.
- Document the guard in README, vision, security, and changelog surfaces.

## Verification

- `python3 scripts/check-android-baseline.py`
- `make check`
- `git diff --check`
