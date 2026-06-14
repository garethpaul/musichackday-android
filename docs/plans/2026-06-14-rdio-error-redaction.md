# Rdio Authorization Error Redaction

status: completed

## Problem

The cancelled Rdio authorization callback logs SDK-provided error code and
description fields verbatim. Provider diagnostics can include request URLs or
other sensitive values that do not belong in application logs.

## Scope

- Replace raw Rdio authorization diagnostics with one stable action-level log.
- Preserve token clearing, playback preparation, success handling, and request
  code routing.
- Extend static, documentation, and completed-evidence contracts.

## Validation

- Run all canonical Make gates from the checkout and an external directory.
- Keep `scripts/check-android-baseline.py` as the active static contract.
- Reject mutations that restore either raw diagnostic read, raw logging, stale
  plan status, or missing guidance.
- Run exact diff, artifact, conflict-marker, intended-path, and secret audits.

## Risks

- Logs intentionally lose provider-specific failure detail; debugging should
  use controlled SDK instrumentation rather than production diagnostics.
- The stacked base PR must merge first.

## Verification Completed

- All four Make gates passed from the checkout and an external directory.
- Five isolated hostile mutations were rejected: raw error-code read, raw
  error-description read, raw diagnostic log, stale plan status, and missing
  guidance.
- Exact diff, artifact, conflict-marker, intended-path, and secret audits
  passed. No Android runtime or provider callback was exercised on Linux.
