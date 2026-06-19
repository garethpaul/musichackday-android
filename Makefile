.PHONY: build check lint static-check test unit-test verify

ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))
override SHELL := /bin/sh
override PATH := /opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin
override PYTHON := $(shell PATH=$(PATH) command -v python3)
RDIO_APP_SHA256 := fb91ad06a10932969adf680e877b76db2b4c0559513cf2bccb471fbb5fd1bc3d
WORKFLOW_SHA256 := 3ac196785a75b7a744a1690a396feac24cf1b1fffd189dc2474ff01e6d01b57f
TEST_ANDROID_SHA256 := 6af9ede9e0550f65385bde39a2523cf706db1023e9b0c98476867c5cdcc10dc4
TEST_REVIEWED_SHA256 := 08f52276bd3199d300dadcc3140fb790ea1d7c4b14b3377087b67a662c3a33dd
EVIDENCE_PLAN_SHA256 := a3698f126caa282ffe3242a37dd1bec6e29b0d2fbd086afcf03e324f3937eb3e
EXPECTED_TEST_COUNT := 91

check verify test unit-test:
	@set -eu; test -n "$(PYTHON)"; test -x "$(PYTHON)"; $(PYTHON) -I -B -c 'import sys; raise SystemExit(0 if sys.version_info[:2] in {(3, 12), (3, 14)} else 1)'; tmp=$$(/usr/bin/mktemp -d); trap '/bin/rm -rf "$$tmp"' EXIT; /bin/cp "$(ROOT)/scripts/check-android-baseline.py" "$$tmp/verifier.py"; /usr/bin/env -u PYTHONPATH -u PYTHONHOME -u PYTHONSTARTUP -u PYTHONPYCACHEPREFIX -u MHD_NESTED_GATE PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -I -B "$$tmp/verifier.py" --root "$(ROOT)" --expect-python 3.12,3.14 --gate; /usr/bin/git -C "$(ROOT)" diff --exit-code; /usr/bin/git -C "$(ROOT)" diff --cached --exit-code; test -z "$$(/usr/bin/git -C "$(ROOT)" status --porcelain=v1 --untracked-files=all)"

lint build static-check:
	@set -eu; test -n "$(PYTHON)"; test -x "$(PYTHON)"; $(PYTHON) -I -B -c 'import sys; raise SystemExit(0 if sys.version_info[:2] in {(3, 12), (3, 14)} else 1)'; tmp=$$(/usr/bin/mktemp -d); trap '/bin/rm -rf "$$tmp"' EXIT; /bin/cp "$(ROOT)/scripts/check-android-baseline.py" "$$tmp/verifier.py"; /usr/bin/env -u PYTHONPATH -u PYTHONHOME -u PYTHONSTARTUP -u PYTHONPYCACHEPREFIX -u MHD_NESTED_GATE PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -I -B "$$tmp/verifier.py" --root "$(ROOT)" --expect-python 3.12,3.14 --static
