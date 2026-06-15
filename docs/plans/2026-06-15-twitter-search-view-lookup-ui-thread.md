# Twitter Search View Lookup UI Thread

status: completed

## Problem

The Twitter search task builds provider results on an `AsyncTask` worker and
correctly dispatches adapter mutation to `runOnUiThread`, but it resolves the
target `ListView` with `findViewById` before that handoff. Android view-tree
access is not thread-safe, so successful searches can still touch activity UI
state from the background thread.

## Scope

- Resolve the search-results `ListView` inside the existing UI-thread runnable.
- Keep adapter construction and installation in the same runnable.
- Preserve query construction, failure handling, tweet ordering, HTTPS profile
  image selection, adapter type, and credentials.
- Add ordering-sensitive static contracts and synchronized maintenance guidance.

## Implementation

1. Move the single `findViewById(R.id.list)` lookup into `runOnUiThread` before
   constructing and installing the `TweetAdapter`.
2. Extend the baseline checker to require the handoff before view lookup and
   adapter mutation.
3. Record the UI-thread ownership rule in project guidance and changes.

## Verification

- Run checker compilation and all four Make gates from the repository plus the
  canonical gate from an external directory with explicit timeouts.
- Reject isolated mutations that move lookup before the handoff, move adapter
  installation before lookup, duplicate the lookup, remove guidance, or leave
  this plan incomplete.
- Audit the exact diff, generated artifacts, credential patterns, dependency
  files, conflict markers, binaries, large files, and intended paths.

## Risks

- The legacy `AsyncTask` still strongly references its activity; this change is
  limited to removing the demonstrated worker-thread view lookup.
- No provider, credential, or adapter behavior changes.
- The stacked base pull request must remain available and merge first.

## Work Completed

- Moved the single search-result `ListView` lookup into the existing activity
  UI-thread runnable before adapter construction and installation.
- Added an ordering-sensitive contract requiring one lookup after the handoff
  and before adapter mutation.
- Added synchronized maintenance, security, vision, and change guidance.

## Verification Completed

- All four Make gates passed from the repository and the canonical check passed
  from an external directory through the absolute Makefile path.
- The baseline checker compiled and passed without requiring an Android SDK.
- Six isolated hostile mutations were rejected: worker-thread lookup, adapter
  mutation before lookup, duplicate lookup, missing maintenance guidance,
  missing changelog evidence, and stale plan status.
- `git diff --check`, exact intended-path, generated-artifact,
  credential-pattern, dependency-file, conflict-marker, binary, and large-file
  audits passed.
- No Twitter, Rdio, credential, browser, or Android runtime was contacted.
