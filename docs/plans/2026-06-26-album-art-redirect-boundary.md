# Album-Art Redirect Boundary

Status: Completed

## Problem

The album-art task verifies that its initial URL uses HTTPS, but Android's
`HttpURLConnection` follows redirects by default. The final destination can
therefore fall outside the URL that passed the transport guard.

## Decision

- Disable redirects on the album-art connection before `connect()`.
- Keep the existing HTTPS, timeout, cleanup, fallback, and sanitized logging
  behavior unchanged.
- Fail closed on redirect responses instead of implementing an unreviewed
  redirect-validation loop in this legacy sample.

## Evidence

Android documents that `HttpURLConnection` follows redirects by default and
that `setInstanceFollowRedirects(false)` disables that behavior per connection:
https://developer.android.com/reference/java/net/HttpURLConnection

## Verification

- Add a RED contract requiring redirect disabling before connect.
- Run the complete protected SDK-free Python 3.12/3.14 test inventory.
- Run repository and external-directory `make check`.
- Require hosted static checks and CodeQL on the exact PR head.

## Results

- RED: the focused test failed because no redirect policy was set.
- GREEN: the focused runtime-order contract passed after redirects were disabled
  before `connect()`.
- Python 3.12.12 and Python 3.14.6 each passed repository and
  external-directory `make check` with all 98 protected tests, exact reviewed
  bytes, clean-tree enforcement, and no skips.
- `git diff --check` and credential-pattern review passed.
- Hosted results will be recorded after the pull-request head completes.

## Boundaries

- No live image request, Android SDK build, emulator, or device was exercised.
- Redirect support is intentionally not added; this path fails closed instead.
