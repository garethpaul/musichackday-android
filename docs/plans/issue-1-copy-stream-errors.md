# Issue 1: Stream Copy Failure Guard

status: completed

## Context

GitHub issue: `garethpaul/musichackday-android#1`

`Utils.CopyStream` caught `Exception` and swallowed read/write failures, so a
partial copy could look successful to the caller.

## Work Completed

- Replaced the broad swallowed exception with an explicit `IOException`
  boundary.
- Preserved the original `IOException` as the cause of a visible runtime
  failure.
- Added mutation-sensitive coverage to `scripts/check-android-baseline.py` so
  the SDK-free gate rejects restored broad catches, empty catches, or missing
  diagnostic rethrows.

## Verification Completed

- `python3 -B tests/test_android_baseline.py UtilsCopyStreamContractTests`
- `make check`
- `git diff --check`

## Boundaries

- `Utils.CopyStream` does not close either stream; callers retain stream
  ownership.
- This guard changes silent copy failures into visible runtime failures.
