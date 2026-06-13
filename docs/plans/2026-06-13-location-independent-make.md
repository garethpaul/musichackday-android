# Location-Independent Android Baseline Verification

status: in progress

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
