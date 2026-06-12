# Checkout Credential Boundary

status: completed

## Context

The recorded evidence describes hosted checkout as credential-free, but the
exact PR head still uses the checkout action's default credential persistence.
The Linux job only needs repository contents for the SDK-free static baseline.

## Objectives

- Disable checkout credential persistence without changing validation scope.
- Enforce one workflow, one read-only permission block, one checkout action,
  and one correctly nested non-persisted credential declaration.
- Preserve immutable action pins, Python 3.12, Ubuntu 24.04, timeout,
  concurrency, and `make check`.
- Correct documentation so it matches the exact workflow state.

## Implementation Units

### Workflow And Checker

Files: `.github/workflows/check.yml` and
`scripts/check-android-baseline.py`.

Add `persist-credentials: false` beneath the sole checkout action. Reject
duplicate workflows, permissions, checkout actions, write scopes, misplaced or
contradictory settings, and incomplete plan evidence.

### Documentation

Files: `README.md`, `SECURITY.md`, `VISION.md`, `CHANGES.md`, and this plan.

Record the narrower credential lifetime while retaining the SDK-free boundary.

## Work Completed

- Added `persist-credentials: false` beneath the sole pinned checkout step.
- Added exact workflow, permission, checkout, nesting, contradiction, and plan
  evidence contracts to `scripts/check-android-baseline.py`.
- Updated hosted-validation documentation without changing Android code or the
  legacy toolchain.

## Verification Completed

- `python3 scripts/check-android-baseline.py`
- `make lint`, `make test`, `make build`, and `make check`
- workflow YAML parse and `git diff --check`
- Hostile workflow and plan mutations

The local checks remain SDK-free and do not execute Gradle. Canonical hosted
push and pull-request checks remain required at the exact successor head before
owner merge.

## Boundaries

- Do not change app source, manifests, Gradle files, wrappers, jars, or tests.
- Do not supply credentials, run OAuth, fetch media, or execute Gradle/Android
  SDK tasks.
- Preserve the existing remediation PR and evidence.
