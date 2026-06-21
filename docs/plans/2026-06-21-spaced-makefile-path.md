# Spaced Absolute Makefile Path Verification

status: completed

## Context

GNU Make list functions split a loaded absolute Makefile path at spaces. A
checkout path containing spaces, brackets, and an apostrophe therefore sent
the SDK-free verification gate to a fabricated path under the caller.

## Scope

1. Derive the checkout root from the complete `MAKEFILE_LIST` value.
2. Preserve the authoritative root against command-line and environment input.
3. Reject command-line or environment-preferred `MAKEFILE_LIST` overrides.
4. Exercise all seven Make aliases from an external working directory.
5. Preserve the reviewed-test hash chain and exact test-count contract.

## Verification

- Root and external hostile-path gates passed on supported Python versions.
- All seven Make aliases retained the checkout with no override and with
  command-line or environment `ROOT` input.
- Both tested `MAKEFILE_LIST` override paths failed closed.
- The protected suite passed 94 tests with zero failures, skips, or errors.
- Current-tree secret scanning reported zero findings; historical values were
  neither emitted nor changed.

## Risk And Rollback

This changes SDK-free verification root discovery only. Rollback restores the
previous root expression and the prior 91-test integrity constants.
