---
title: Make Gate Aliases
type: validation
status: completed
date: 2026-06-09
---

# Make Gate Aliases

## Problem Frame

The repository had `make check`, `make verify`, and `make static-check`, but
the fleet pre-push sequence also invokes `make lint`, `make test`, and
`make build`. Those commands should reach the existing SDK-free Android
baseline rather than failing before checks run.

## Scope Boundaries

- Keep the Make gates SDK-free for modern machines without the legacy Android
  Platform 19 and Build Tools 19.0.3 setup.
- Keep Gradle and Android Studio verification documented separately for
  machines with the matching SDK.
- Do not change app behavior or legacy dependency pins.

## Implementation Units

### U1: Expose Standard Make Gates

Files:

- Modify `Makefile`

Approach:

- Add `lint`, `test`, and `build` targets.
- Delegate the new targets to `static-check`.
- Keep `check` and `verify` delegated to the same baseline.

### U2: Pin And Document The Contract

Files:

- Modify `scripts/check-android-baseline.py`
- Modify `README.md`
- Modify `VISION.md`
- Modify `SECURITY.md`
- Modify `CHANGES.md`

Approach:

- Add static checks for the Makefile target contract.
- Document the standard Make gate commands in project docs.

## Verification

- `make lint`
- `make test`
- `make build`
- `make check`
- `make verify`
- `git diff --check`
