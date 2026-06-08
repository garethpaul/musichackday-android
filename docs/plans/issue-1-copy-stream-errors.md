# Issue 1: Handle CopyStream Failures

## Context

GitHub issue: `garethpaul/musichackday-android#1`

`Utils.CopyStream` catches `Exception` and swallows it, so stream read/write failures can leave callers with partial data and no diagnostic signal.

## Plan

1. Catch the expected checked failure type from stream reads and writes.
2. Preserve the exception as the cause of a visible runtime error instead of returning silently.
3. Add a source-level baseline check that rejects broad `Exception` catches in the helper and requires the diagnostic rethrow.

## Verification

- Run `bash scripts/check-baseline.sh`.
- Compile `Utils.java` with `javac`.
- Run `git diff --check`.
