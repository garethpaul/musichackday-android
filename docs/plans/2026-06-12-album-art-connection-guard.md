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
3. Disable automatic redirects so initial HTTPS validation remains authoritative.
4. Close input streams and disconnect the HTTP connection in all paths.
5. Keep failure logging generic and free of media URLs or exception details.

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

## Work Completed

- Required HTTPS before opening the album-art connection.
- Added 10-second connect and read timeouts.
- Disabled automatic redirects before connecting.
- Closed the buffered input stream and disconnected the HTTP connection from
  the `finally` path.
- Replaced URL and exception-bearing failure logs with a generic message.

## Verification Completed

### Canonical Evidence

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

Completed on GitHub Actions for verified predecessor/implementation head
`1fd944d8b02118d817f98603aed3050bceb6dc32`:

- push run `27397456751`: success
- pull-request run `27397458335`: success

This verified predecessor/implementation head is not the final evidence-only head.

The verified implementation preserves `URLUtil.isHttpsUrl(artworkUrl)`,
`connection.setInstanceFollowRedirects(false)`,
`connection.setConnectTimeout(10000)`, `connection.setReadTimeout(10000)`,
`bufferedInputStream.close()`, `connection.disconnect()`, and the sanitized
`Album art download failed` message.

### Reviewed Byte Contract

The following raw bytes were reviewed together:

- `app/src/main/java/com/twitterdev/rdio/app/RdioApp.java`
  SHA-256: `a71008d19f4811c217a420ff8828f2ebf7f45969055fbd515584c896d67239ec`
- `.github/workflows/check.yml`
  SHA-256: `3ac196785a75b7a744a1690a396feac24cf1b1fffd189dc2474ff01e6d01b57f`

Future legitimate changes require explicit review and coordinated updates to the protected file, checker constant, independent test constant, and this contract stanza.

## Boundaries

- Do not make live media requests in tests or CI.
- Do not change playback, artwork scaling, or fallback-image behavior.
- Do not claim Android compilation without a compatible legacy SDK/toolchain.
