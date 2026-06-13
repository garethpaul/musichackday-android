# Location-Independent Android Baseline Verification

status: completed

## Context

The SDK-free Make aliases invoke `scripts/check-android-baseline.py` relative to
the caller's working directory. An absolute Makefile invocation from another
directory therefore fails or can inspect the wrong tree instead of the checkout.

## Objectives

- Resolve every Make gate from the checkout containing the Makefile.
- Preserve the existing SDK-free alias graph and Python override.
- Lock the rooted recipe, operator guidance, completed status, and verification
  evidence into the active static checker.
- Prove root and external-directory behavior with mutation-sensitive checks.

## Implementation Units

### Make Contract

Files: `Makefile` and `scripts/check-android-baseline.py`.

Derive one absolute checkout root from the loaded Makefile and invoke the
baseline checker by absolute path. Require the exact small Makefile so target
aliases and path resolution cannot drift independently.

### Documentation And Evidence

Files: `README.md`, `CHANGES.md`, and this plan.

Document absolute Makefile invocation and record bounded root, external, and
hostile-mutation verification after it completes.

## Boundaries

- Do not change Android source, manifests, Gradle files, wrappers, jars, tests,
  workflows, or dependency pins.
- Do not supply credentials, execute Gradle or Android SDK tasks, authenticate,
  or fetch remote media.
- Preserve the existing stacked PR chain and exact-head evidence.

## Work Completed

- Rooted every SDK-free Make alias at the checkout containing the loaded
  Makefile while preserving the existing target graph and `PYTHON` override.
- Added exact Makefile, README invocation, completed status, and verification
  evidence contracts to `scripts/check-android-baseline.py`.
- Documented absolute Makefile invocation without changing Android or workflow
  behavior.

## Verification Completed

- Root and external-directory `lint`, `test`, `build`, `verify`, and `check`
  gates passed through the checkout's absolute Makefile path.
- `python3 -m py_compile scripts/check-android-baseline.py` and
  `git diff --check` passed.
- Six isolated hostile mutations covering root derivation, checker resolution,
  alias delegation, the Python override, completed plan evidence, and README
  invocation guidance were rejected by the intended contracts.
- Intended-path, secret-pattern, conflict-marker, generated-artifact, Android,
  Gradle, dependency, workflow, and credential-boundary audits passed.
