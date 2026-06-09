# Image Download Guards Plan

status: completed

## Context

`ImageDownload` stores the target `ImageView` in a `WeakReference` before
passing image URLs to Universal Image Loader. If the row view is recycled or the
task is started without a valid URL, the previous code still dereferenced the
weak reference and tried to display a missing URL.

## Objectives

- Preserve the existing Universal Image Loader path.
- Return safely when the async task receives no URL or an invalid URL.
- Return safely when the weak `ImageView` reference has been cleared before
  `onPostExecute`.
- Extend `make check` so future media-loading changes preserve these guards.

## Verification

- `make check`
- `python3 scripts/check-android-baseline.py`
- `git diff --check`
