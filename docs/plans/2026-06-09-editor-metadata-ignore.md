# Editor Metadata Ignore

status: completed

## Context

The legacy Android Studio project still tracked `.idea` workspace files and
`.iml` module files. Those files capture machine-local IDE state and can drift
independently of the preserved Android hack-day source.

## Objectives

- Remove tracked `.idea` and `.iml` metadata from source control.
- Ignore Android Studio, VS Code, and module metadata going forward.
- Extend `scripts/check-android-baseline.py` so editor metadata cannot return
  unnoticed.
- Document the guardrail in the README, security notes, vision, and changelog.

## Verification

- `scripts/check-android-baseline.py`
- `make lint`
- `make test`
- `make build`
- `make check`
- `git diff --check`
