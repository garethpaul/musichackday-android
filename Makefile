.PHONY: check verify static-check

PYTHON ?= python3

check: verify

verify: static-check

static-check:
	$(PYTHON) scripts/check-android-baseline.py
