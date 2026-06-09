# Memory Cache Entry Guards

status: completed

## Context

`MemoryCache` stores image bitmaps behind soft references. Cleared references
can remain in the map after memory pressure, and null keys or bitmaps should not
create cache entries.

## Objectives

- Return `null` when a cache key has no soft reference.
- Remove cache entries whose soft references have been cleared.
- Skip writes for null cache keys or null bitmaps.
- Extend the static Android baseline and docs for memory cache entry guards.

## Verification

- `make check`
- `python3 scripts/check-android-baseline.py`
- `git diff --check`
