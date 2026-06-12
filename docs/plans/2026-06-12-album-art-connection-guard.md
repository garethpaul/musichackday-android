# Album Art Connection Guard

status: completed

## Context

`RdioApp` contains a second album-art download path outside the guarded
`ImageDownload` helper. It logs the full media URL, accepts cleartext URLs,
opens a connection without timeouts, and relies on success-path stream closes.
This can expose URL data, hang a playback refresh, or leak network resources.

## Priorities

1. Reject non-HTTPS album-art URLs before opening a connection.
2. Apply bounded connect and read timeouts.
3. Close input streams and disconnect the HTTP connection in all paths.
4. Keep failure logging generic and free of media URLs or exception details.

## Implementation Units

### Artwork Task

File: `app/src/main/java/com/twitterdev/rdio/app/RdioApp.java`

Use `URLUtil.isHttpsUrl`, `HttpURLConnection`, 10-second timeouts, and a
`finally` block for stream closure and disconnect. Preserve the blank-artwork
fallback and existing UI scaling behavior.

### Static Contract And Documentation

Files:

- `scripts/check-android-baseline.py`
- `README.md`
- `SECURITY.md`
- `VISION.md`
- `CHANGES.md`
- `docs/plans/2026-06-12-album-art-connection-guard.md`

Require the transport, timeout, lifecycle, and sanitized logging contract and
document the SDK-free verification boundary.

## Verification

Completed locally on 2026-06-12:

- `python3 -m py_compile scripts/check-android-baseline.py`
- `make lint`
- `make test`
- `make build`
- `make check`
- hostile mutations removing HTTPS, timeout, cleanup, or sanitized logging
  guards were each rejected by the static contract
- `git diff --check`

The local gate is SDK-free and does not execute the obsolete Android toolchain.

Completed on GitHub Actions for implementation head
`07bc050493d0c703f6ded9c06f09d187b16b52f7`:

- push run `27397446444`: success
- pull-request run `27397447181`: success

## Boundaries

- Do not make live media requests in tests or CI.
- Do not change playback, artwork scaling, or fallback-image behavior.
- Do not claim Android compilation without a compatible legacy SDK/toolchain.
