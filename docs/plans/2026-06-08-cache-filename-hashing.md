# Cache Filename Hashing Plan

status: completed

## Context

The image cache already uses app-private storage. Cache file names were still derived from Java `String.hashCode()`, which is short and collision-prone for URL-derived media names.

## Objectives

- Derive media cache filenames with SHA-256.
- Keep image cache files in the app-private cache directory.
- Avoid short Java hash values for URL-derived cache filenames.
- Extend the static baseline and docs to preserve SHA-256 cache filenames.

## Verification

- `scripts/check-android-baseline.py`
- `make check`
- `git diff --check`
