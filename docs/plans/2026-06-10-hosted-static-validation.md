# Hosted Static Validation

status: completed

## Context

The repository has an SDK-free baseline for credentials, OAuth callbacks,
image downloads, cache behavior, manifest metadata, vendored jars, and the
legacy Gradle wrapper, but no hosted validation. The Android build depends on
Gradle 1.10 and Android plugin 0.8.3, which are not a credible modern CI target.

## Priorities

1. Run the canonical SDK-free `make check` gate on hosted Linux.
2. Pin third-party actions, Python, permissions, runner, and timeout.
3. Enforce the workflow contract from the baseline checker.
4. Keep credentials, OAuth exchange, media downloads, Android SDK setup, and
   obsolete Gradle execution outside hosted validation.

## Implementation Units

Files:

- `.github/workflows/check.yml`
- `scripts/check-android-baseline.py`
- `README.md`
- `VISION.md`
- `SECURITY.md`
- `CHANGES.md`

Add push, pull-request, and manual triggers; read-only permissions; concurrency
cancellation; a bounded `ubuntu-24.04` job; commit-pinned checkout and Python
setup; and `make check`. Require that contract from the baseline.

## Verification

- `make lint`
- `make test`
- `make build`
- `make check`
- workflow YAML parse
- `git diff --check`
- successful hosted Linux `Check` workflow for the pushed commit

## Boundaries

- Do not provide Twitter/Rdio credentials or perform OAuth exchange.
- Do not download Android SDK components or execute the obsolete Gradle build.
