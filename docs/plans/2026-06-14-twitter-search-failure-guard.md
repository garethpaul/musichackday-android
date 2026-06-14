# Twitter Search Failure Guard

Status: planned

## Problem

The background Twitter search logs the raw search value, prints provider stack
traces, and continues with a null `QueryResult` after `TwitterException`. A
failed provider call can therefore expose user-controlled search context and
then crash while iterating `result.getTweets()`.

## Scope

- Remove raw Twitter search-value logging.
- Replace provider stack traces with a fixed action-level failure message.
- Return before result iteration when the Twitter search fails.
- Replace JSON formatting stack traces with a fixed message while preserving
  successful tweet rendering.
- Add mutation-sensitive static contracts and project guidance.
- Do not change credentials, query construction, result ordering, image URLs,
  adapter behavior, or dependency versions.

## Implementation

1. Remove the verbose background/search-value logs from the search task.
2. Keep `QueryResult` assignment inside the existing try block; on
   `TwitterException`, log one constant message and return before iteration.
3. Replace `JSONException.printStackTrace()` with a constant formatting-error
   message.
4. Extend `scripts/check-android-baseline.py`, README, security, vision, and
   changelog contracts.

## Validation

- Run checker compilation and all four SDK-free Make gates from the checkout
  plus the canonical gate from an external directory.
- Verify isolated mutations that restore raw query logging, either stack trace,
  remove the failure return, move iteration before the guarded search, remove
  maintenance guidance, or leave this plan incomplete are rejected.
- Run `git diff --check` and exact intended-path, generated-artifact,
  secret-pattern, conflict-marker, binary, and large-file audits.
- Record that Android SDK/Gradle execution is intentionally outside this
  dependency-free baseline on the current host.

## Risks

- Failed searches continue to produce no rows; the change only makes that path
  redacted and non-crashing.
- The stacked base PR must remain available and merge before this change.

## Work Completed

Pending implementation.

## Verification Completed

Pending validation.
