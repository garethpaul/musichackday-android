.PHONY: build check lint static-check test unit-test verify

override SHELL := /bin/sh
override PATH := /opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin
override PYTHON := $(shell PATH=$(PATH) command -v python3)
RDIO_APP_SHA256 := a93c3d16a4626087bf777b515b0469cb91b445be473e7abbb32cfe1277bf66bc
WORKFLOW_SHA256 := fed29231b61bddaec646f9ef97fb830a9eb4bd3ad880a0b87f98aa5105a97d72
TEST_ANDROID_SHA256 := a8ae01def94e7e74278681ea80ba185dd01a520307a69795aed6d9434aeb9fbd
TEST_REVIEWED_SHA256 := c4c47932788dbab6b9fb4630cce424ee47814fc36605f04edcf59255b2d57a7e
EVIDENCE_PLAN_SHA256 := 1317ee18de95cbf935cb2c3a1b5bc1f6123d125bb7ef212445b3eddbd54f9cdb
EXPECTED_TEST_COUNT := 73

check verify test unit-test:
	@set -eu; test -n "$(PYTHON)"; test -x "$(PYTHON)"; $(PYTHON) -I -B -c 'import sys; raise SystemExit(0 if sys.version_info[:2] in {(3, 12), (3, 14)} else 1)'; tmp=$$(/usr/bin/mktemp -d); trap '/bin/rm -rf "$$tmp"' EXIT; /bin/cp scripts/check-android-baseline.py "$$tmp/verifier.py"; /usr/bin/env -u PYTHONPATH -u PYTHONHOME -u PYTHONSTARTUP -u PYTHONPYCACHEPREFIX -u MHD_NESTED_GATE PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -I -B "$$tmp/verifier.py" --root "$(CURDIR)" --expect-python 3.12,3.14 --gate; /usr/bin/git diff --exit-code; /usr/bin/git diff --cached --exit-code; test -z "$$(/usr/bin/git status --porcelain=v1 --untracked-files=all)"

lint build static-check:
	@set -eu; test -n "$(PYTHON)"; test -x "$(PYTHON)"; $(PYTHON) -I -B -c 'import sys; raise SystemExit(0 if sys.version_info[:2] in {(3, 12), (3, 14)} else 1)'; tmp=$$(/usr/bin/mktemp -d); trap '/bin/rm -rf "$$tmp"' EXIT; /bin/cp scripts/check-android-baseline.py "$$tmp/verifier.py"; /usr/bin/env -u PYTHONPATH -u PYTHONHOME -u PYTHONSTARTUP -u PYTHONPYCACHEPREFIX -u MHD_NESTED_GATE PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -I -B "$$tmp/verifier.py" --root "$(CURDIR)" --expect-python 3.12,3.14 --static
