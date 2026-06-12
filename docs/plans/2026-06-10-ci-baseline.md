# CI Baseline

status: completed

## Context

The portfolio remediation plan calls for lightweight CI on high-priority repos
that already have passing local checks. This legacy Android sample has an
SDK-free static baseline, so CI should run that baseline without requiring the
old Android SDK or credentials.

## Completed Scope

- Added a GitHub Actions workflow for pushes, pull requests, and manual runs.
- Configured CI to run `make check`, which delegates to the SDK-free static
  Android baseline in `scripts/check-android-baseline.py`.
- Extended the baseline checker and docs so the CI gate remains visible.

## Verification

- `make check`
- `git diff --check`
