.PHONY: build check lint static-check test unit-test verify

ifneq ($(origin MAKEFILE_LIST),file)
$(error MAKEFILE_LIST must not be overridden)
endif
override ROOT := $(shell path='$(subst ','"'"',$(MAKEFILE_LIST))'; path=$$(printf '%s\n' "$$path" | sed 's/^ //'); dirname -- "$$path")
override SHELL := /bin/sh
override PATH := /opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin
override PYTHON := $(shell PATH=$(PATH) command -v python3)
RDIO_APP_SHA256 := a71008d19f4811c217a420ff8828f2ebf7f45969055fbd515584c896d67239ec
WORKFLOW_SHA256 := 3ac196785a75b7a744a1690a396feac24cf1b1fffd189dc2474ff01e6d01b57f
TEST_ANDROID_SHA256 := 914a878b27e434d6adc616b18ca2b1e53ba5624699ed467c388c050d88fa6ef9
TEST_REVIEWED_SHA256 := d3a05db5890dcd31039ea4247d63537b5fff02c5013d9fd0383c966acad24b28
EVIDENCE_PLAN_SHA256 := 5ae0ed781d90602a39ec83d7619b1416b5ba4a4629492c164fdc40f8cbb80535
EXPECTED_TEST_COUNT := 98

check verify test unit-test:
	@set -eu; test -n "$(PYTHON)"; test -x "$(PYTHON)"; $(PYTHON) -I -B -c 'import sys; raise SystemExit(0 if sys.version_info[:2] in {(3, 12), (3, 14)} else 1)'; tmp=$$(/usr/bin/mktemp -d); trap '/bin/rm -rf "$$tmp"' EXIT; /bin/cp "$(ROOT)/scripts/check-android-baseline.py" "$$tmp/verifier.py"; /usr/bin/env -u PYTHONPATH -u PYTHONHOME -u PYTHONSTARTUP -u PYTHONPYCACHEPREFIX -u MHD_NESTED_GATE PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -I -B "$$tmp/verifier.py" --root "$(ROOT)" --expect-python 3.12,3.14 --gate; /usr/bin/git -C "$(ROOT)" diff --exit-code; /usr/bin/git -C "$(ROOT)" diff --cached --exit-code; test -z "$$(/usr/bin/git -C "$(ROOT)" status --porcelain=v1 --untracked-files=all)"

lint build static-check:
	@set -eu; test -n "$(PYTHON)"; test -x "$(PYTHON)"; $(PYTHON) -I -B -c 'import sys; raise SystemExit(0 if sys.version_info[:2] in {(3, 12), (3, 14)} else 1)'; tmp=$$(/usr/bin/mktemp -d); trap '/bin/rm -rf "$$tmp"' EXIT; /bin/cp "$(ROOT)/scripts/check-android-baseline.py" "$$tmp/verifier.py"; /usr/bin/env -u PYTHONPATH -u PYTHONHOME -u PYTHONSTARTUP -u PYTHONPYCACHEPREFIX -u MHD_NESTED_GATE PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -I -B "$$tmp/verifier.py" --root "$(ROOT)" --expect-python 3.12,3.14 --static
