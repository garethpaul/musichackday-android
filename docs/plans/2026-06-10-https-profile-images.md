# HTTPS Profile Images

status: completed

## Problem

Twitter profile images are selected through the cleartext-capable Twitter4J
getter, and the loader accepts both HTTP and HTTPS. This permits profile media
to cross the network without transport encryption.

## Scope

- Select Twitter4J's HTTPS bigger-profile-image URL.
- Reject cleartext HTTP and non-web schemes at the image loader boundary.
- Preserve missing-URL and recycled-`ImageView` guards.
- Add static and mutation guardrails without executing the obsolete Android
  toolchain or making network requests.
- Document the transport requirement across project guidance.

## Verification

- `python3 scripts/check-android-baseline.py`
- `make lint`
- `make test`
- `make build`
- `make check`
- mutation checks for source selection and loader scheme enforcement
- `git diff --check`

## Work Completed

- Switched Twitter profile image selection to
  `getBiggerProfileImageURLHttps()` from the vendored Twitter4J API.
- Replaced the broad HTTP(S) loader check with an HTTPS-only URL guard.
- Preserved missing parameter and recycled image-view handling.
- Extended `scripts/check-android-baseline.py` with source-selection, loader,
  plan, changelog, and documentation assertions.
- Documented encrypted profile-media transport as a maintained guardrail.
