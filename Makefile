.PHONY: build check lint static-check test verify

PYTHON ?= python3

check: verify

verify: static-check

lint test build: static-check

static-check:
	$(PYTHON) scripts/check-android-baseline.py
