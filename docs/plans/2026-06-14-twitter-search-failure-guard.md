# Twitter Search Failure Guard

status: completed

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

- Removed raw query and background-state logs from the Twitter search task.
- Replaced Twitter provider stack traces with one fixed failure message and a
  return before result iteration.
- Replaced JSON formatting stack traces with one fixed message and skipped the
  malformed row.
- Added ordering-sensitive static contracts and project guidance.

## Verification Completed

- All four Make gates passed from the checkout and the canonical check passed
  from an external directory through the absolute Makefile path.
- Seven isolated hostile mutations were rejected: raw query logging, Twitter
  stack traces, JSON formatting stack traces, missing failure return, result
  iteration before the guarded search, missing maintenance guidance, and stale
  plan status.
- Checker compilation, `git diff --check`, and exact intended-path,
  generated-artifact, secret-pattern, conflict-marker, binary, and large-file
  audits passed.
- The SDK-free baseline made no Twitter, Rdio, image, or other live network
  request and did not invoke Android SDK or Gradle builds.
