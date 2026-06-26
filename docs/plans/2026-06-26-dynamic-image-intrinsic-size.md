# Dynamic Image Intrinsic Size Guard

Status: Completed

## Problem

`DynamicImageView.onMeasure` calculates height whenever a drawable exists, even
when that drawable reports zero or negative intrinsic dimensions. A zero width
can expand the float result to an enormous integer height, while a negative
dimension can publish an invalid measured size.

## Decision

- Use the custom aspect-ratio measurement only when both intrinsic dimensions
  are positive.
- Fall back to `ImageView.onMeasure` for missing or dimensionless drawables.
- Preserve the existing width-driven aspect ratio for valid bitmap drawables.

## Verification

- Add RED static contract tests for missing width and height guards.
- Run the focused tests in the supported Python 3.12 container.
- Run root and external-directory `make check`, `git diff --check`, hosted
  static checks, CodeQL, and exact-head review before merge.

## Results

- RED: all three focused tests failed because the dimension validator did not
  exist.
- GREEN: valid positive dimensions are accepted while weakened width and height
  guards are rejected.
- The protected SDK-free inventory now runs 97 tests.
- No Android SDK or emulator is available locally; hosted static verification
  remains the merge gate and runtime layout behavior remains unclaimed.
