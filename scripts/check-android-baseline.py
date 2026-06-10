#!/usr/bin/env python3
"""Static baseline checks for the Music Hack Day Android project."""

from pathlib import Path
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
CONSTANTS_EXAMPLE = "app/src/main/java/com/twitterdev/rdio/app/Constants.java.example"
REQUIRED_FILES = [
    "README.md",
    "SECURITY.md",
    "VISION.md",
    "CHANGES.md",
    "Makefile",
    "app/build.gradle",
    "build.gradle",
    "gradle/wrapper/gradle-wrapper.properties",
    "app/src/main/AndroidManifest.xml",
    "app/src/main/java/com/twitterdev/rdio/app/FileCache.java",
    "app/src/main/java/com/twitterdev/rdio/app/ImageDownload.java",
    "app/src/main/java/com/twitterdev/rdio/app/MemoryCache.java",
    "app/libs/rdio-android-sdk.jar",
    "app/libs/signpost-commonshttp4-1.2.1.1.jar",
    "app/libs/signpost-core-1.2.1.1.jar",
    "app/libs/twitter4j-core-4.0.1.jar",
    CONSTANTS_EXAMPLE,
    "docs/plans/2026-06-08-credential-baseline.md",
    "docs/plans/2026-06-08-cache-filename-hashing.md",
    "docs/plans/2026-06-08-image-download-guards.md",
    "docs/plans/2026-06-08-musichackday-android-baseline.md",
    "docs/plans/2026-06-09-memory-cache-entry-guards.md",
    "docs/plans/2026-06-09-http-image-url-guard.md",
    "docs/plans/2026-06-09-make-gate-aliases.md",
    "docs/plans/2026-06-09-oauth-callback-uri-guard.md",
    "docs/plans/2026-06-09-oauth-callback-path-guard.md",
    "docs/plans/2026-06-09-oauth-callback-verifier-guard.md",
    "docs/plans/2026-06-09-sanitized-oauth-error-logging.md",
    "docs/plans/2026-06-09-editor-metadata-ignore.md",
    "docs/plans/2026-06-10-oauth-callback-token-guard.md",
]
TOKEN_LOG_PATTERNS = [
    re.compile(r"Log\.[a-z]\([^;]*(accessToken|accessTokenSecret|getToken\(|getTokenSecret\()", re.IGNORECASE),
    re.compile(r"Access token(?: secret)?:\s*\"\s*\+"),
    re.compile(r"Twitter OAuth Token"),
]


def read_text(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8", errors="replace")


def android_attr(name: str) -> str:
    return f"{{http://schemas.android.com/apk/res/android}}{name}"


def main() -> int:
    failures = []

    for relative_path in REQUIRED_FILES:
        if not (ROOT / relative_path).is_file():
            failures.append(f"required file missing: {relative_path}")

    gitignore = read_text(".gitignore")
    for expected in [
        ".idea/",
        ".vscode/",
        "*.iml",
        "Constants.java",
        "Constants.class",
        "local.properties",
        "*.jks",
        "*.keystore",
        "*.p12",
    ]:
        if expected not in gitignore:
            failures.append(f".gitignore must keep {expected} out of source control")

    tracked_constants = subprocess.run(
        ["git", "ls-files", "--", "app/src/main/java/com/twitterdev/rdio/app/Constants.java"],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        check=False,
    ).stdout.strip()
    if tracked_constants:
        failures.append("real app/src/main/java/com/twitterdev/rdio/app/Constants.java must not be tracked")
    tracked_editor_files = subprocess.run(
        ["git", "ls-files", "--", ".idea", ".vscode", "*.iml"],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        check=False,
    ).stdout.splitlines()
    if tracked_editor_files:
        failures.append("IDE metadata must not be tracked: " + ", ".join(tracked_editor_files))
    tracked = subprocess.run(
        ["git", "ls-files"],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        check=False,
    ).stdout.splitlines()
    generated = [
        path for path in tracked
        if path.endswith((".apk", ".class", ".dex")) or "/build/" in path or path.startswith("build/")
    ]
    if generated:
        failures.append("generated Android artifacts must not be tracked: " + ", ".join(generated))

    wrapper = read_text("gradle/wrapper/gradle-wrapper.properties")
    if "distributionUrl=https\\://services.gradle.org/distributions/gradle-1.10-all.zip" not in wrapper:
        failures.append("Gradle wrapper distribution must use HTTPS for gradle-1.10-all.zip")

    root_gradle = read_text("build.gradle")
    makefile = read_text("Makefile")
    for target in [
        ".PHONY: build check lint static-check test verify",
        "check: verify",
        "verify: static-check",
        "lint test build: static-check",
    ]:
        if target not in makefile:
            failures.append(f"Makefile must expose target contract: {target}")

    if "com.android.tools.build:gradle:0.8.3" not in root_gradle:
        failures.append("Android Gradle plugin must be pinned to 0.8.3")
    if "https://dl.google.com/dl/android/maven2/" not in root_gradle:
        failures.append("Google Maven repository must stay configured for legacy Android support artifacts")
    app_gradle = read_text("app/build.gradle")
    if "com.android.support:appcompat-v7:19.1.0" not in app_gradle:
        failures.append("appcompat-v7 must be pinned to 19.1.0")
    dynamic_dependency = re.compile(r"(classpath|compile)\s+['\"][^'\"]+:\+['\"]")
    for relative_path, text in [("build.gradle", root_gradle), ("app/build.gradle", app_gradle)]:
        if dynamic_dependency.search(text):
            failures.append(f"dynamic Maven dependency remains in {relative_path}")

    try:
        manifest = ET.parse(ROOT / "app/src/main/AndroidManifest.xml").getroot()
        if manifest.attrib.get("package") != "com.twitterdev.rdio.app":
            failures.append("manifest package must remain com.twitterdev.rdio.app")
        permissions = {
            node.attrib.get(android_attr("name"))
            for node in manifest.findall("uses-permission")
        }
        for permission in [
            "android.permission.INTERNET",
            "android.permission.ACCESS_NETWORK_STATE",
        ]:
            if permission not in permissions:
                failures.append(f"manifest must request {permission}")
        if "android.permission.WRITE_EXTERNAL_STORAGE" in permissions:
            failures.append("image cache must not require WRITE_EXTERNAL_STORAGE")
        application = manifest.find("application")
        if application is None:
            failures.append("manifest must include an application element")
        elif application.attrib.get(android_attr("allowBackup")) != "false":
            failures.append("android:allowBackup must stay false because OAuth tokens are stored locally")
    except ET.ParseError as exc:
        failures.append(f"manifest XML must parse: {exc}")

    constants = read_text(CONSTANTS_EXAMPLE)
    for expected in ["YOUR_TWITTER_API_KEY", "YOUR_RDIO_APP_KEY", "app://twitter-dev", "URL_TWITTER_OAUTH_TOKEN"]:
        if expected not in constants:
            failures.append(f"{CONSTANTS_EXAMPLE} must include placeholder {expected}")
    for name, value in re.findall(r"public static final String\s+(\w+)\s*=\s*\"([^\"]*)\"", constants):
        if name in {"API_KEY", "API_SECRET", "appKey", "appSecret"} and not value.startswith("YOUR_"):
            failures.append(f"{CONSTANTS_EXAMPLE} must use a YOUR_ placeholder for {name}")

    for relative_path in [
        "app/src/main/java/com/twitterdev/rdio/app/App.java",
        "app/src/main/java/com/twitterdev/rdio/app/MainActivity.java",
        "app/src/main/java/com/twitterdev/rdio/app/RdioApp.java",
        "app/src/main/java/com/twitterdev/rdio/app/TweetAdapter.java",
    ]:
        text = read_text(relative_path)
        for pattern in TOKEN_LOG_PATTERNS:
            if pattern.search(text):
                failures.append(f"token-bearing log pattern remains in {relative_path}: {pattern.pattern}")

    app_source = read_text("app/src/main/java/com/twitterdev/rdio/app/App.java")
    if ".enableLogging()" in app_source:
        failures.append("image loader verbose logging must stay disabled")

    main_activity = read_text("app/src/main/java/com/twitterdev/rdio/app/MainActivity.java")
    if "uri.toString().startsWith(Constants.CALLBACKURL)" in main_activity:
        failures.append("Twitter OAuth callbacks must not use broad string-prefix matching")
    if (
        "private boolean isTwitterCallback(Uri uri)" not in main_activity
        or "Uri callbackUri = Uri.parse(Constants.CALLBACKURL)" not in main_activity
        or "expectedScheme.equals(uri.getScheme())" not in main_activity
        or "expectedAuthority.equals(uri.getAuthority())" not in main_activity
    ):
        failures.append("MainActivity must validate OAuth callbacks by exact scheme and authority")
    if (
        "private String normalizedPath(Uri uri)" not in main_activity
        or "String expectedPath = normalizedPath(callbackUri)" not in main_activity
        or "String actualPath = normalizedPath(uri)" not in main_activity
        or "expectedPath.equals(actualPath)" not in main_activity
    ):
        failures.append("MainActivity must validate OAuth callbacks by exact normalized path")
    if (
        "private boolean hasOAuthVerifier(String verifier)" not in main_activity
        or "verifier.trim().length() > 0" not in main_activity
        or "!hasOAuthVerifier(verifier)" not in main_activity
    ):
        failures.append("MainActivity must reject blank OAuth verifier values before token exchange")
    if (
        "final String callbackToken = uri" not in main_activity
        or "Constants.URL_TWITTER_OAUTH_TOKEN" not in main_activity
        or "private boolean matchesRequestToken(String callbackToken, RequestToken activeRequestToken)" not in main_activity
        or "!matchesRequestToken(callbackToken, requestToken)" not in main_activity
        or "activeRequestToken.getToken()" not in main_activity
    ):
        failures.append("MainActivity must bind OAuth callbacks to the active request token")
    if (
        "private void logTwitterLoginFailure(String action)" not in main_activity
        or 'Log.e("Twitter Login Error", action + " failed")' not in main_activity
        or "e.printStackTrace()" in main_activity
        or "e.getMessage()" in main_activity
    ):
        failures.append("MainActivity OAuth errors must use sanitized action-level logging")

    file_cache = read_text("app/src/main/java/com/twitterdev/rdio/app/FileCache.java")
    if "context.getCacheDir()" not in file_cache:
        failures.append("FileCache must use the app-private cache directory")
    if "Environment.getExternalStorageDirectory" in file_cache:
        failures.append("FileCache must not use shared external storage")
    if 'MessageDigest.getInstance("SHA-256")' not in file_cache or "cacheFileName(url)" not in file_cache:
        failures.append("FileCache must derive image cache filenames with SHA-256")
    if "url.hashCode()" in file_cache:
        failures.append("FileCache must not use short Java hashCode values for URL cache filenames")
    if "url-download" in read_text("app/src/main/java/com/twitterdev/rdio/app/TweetAdapter.java"):
        failures.append("tweet image URLs must not be logged")
    image_download = read_text("app/src/main/java/com/twitterdev/rdio/app/ImageDownload.java")
    if "isHttpImageUrl" not in image_download or "URLUtil.isHttpUrl" not in image_download or "URLUtil.isHttpsUrl" not in image_download or "params.length == 0" not in image_download:
        failures.append("ImageDownload must guard missing and non-HTTP(S) image URLs")
    if "ImageView imageView = imageViewReference.get()" not in image_download or "imageView == null" not in image_download:
        failures.append("ImageDownload must guard recycled ImageView references")
    memory_cache = read_text("app/src/main/java/com/twitterdev/rdio/app/MemoryCache.java")
    if "cache.remove(id)" not in memory_cache or "if(id==null || bitmap==null)" not in memory_cache:
        failures.append("MemoryCache must prune cleared references and skip null cache writes")

    if not os.access(ROOT / "gradlew", os.X_OK):
        failures.append("gradlew must be executable")

    for relative_path in [
        "docs/plans/2026-06-08-credential-baseline.md",
        "docs/plans/2026-06-08-cache-filename-hashing.md",
        "docs/plans/2026-06-08-image-download-guards.md",
        "docs/plans/2026-06-08-musichackday-android-baseline.md",
        "docs/plans/2026-06-09-memory-cache-entry-guards.md",
        "docs/plans/2026-06-09-http-image-url-guard.md",
        "docs/plans/2026-06-09-make-gate-aliases.md",
        "docs/plans/2026-06-09-oauth-callback-uri-guard.md",
        "docs/plans/2026-06-09-oauth-callback-path-guard.md",
        "docs/plans/2026-06-09-oauth-callback-verifier-guard.md",
        "docs/plans/2026-06-09-sanitized-oauth-error-logging.md",
        "docs/plans/2026-06-09-editor-metadata-ignore.md",
        "docs/plans/2026-06-10-oauth-callback-token-guard.md",
    ]:
        if not (ROOT / relative_path).is_file():
            continue
        plan = read_text(relative_path)
        if "status: completed" not in plan:
            failures.append(f"{relative_path} must record completed status")
        if "scripts/check-android-baseline.py" not in plan:
            failures.append(f"{relative_path} must reference the active baseline checker")

    readme = read_text("README.md")
    vision = read_text("VISION.md")
    security = read_text("SECURITY.md")
    changes = read_text("CHANGES.md")
    for relative_path, text in [("README.md", readme), ("VISION.md", vision), ("SECURITY.md", security)]:
        if "image download guard" not in text.lower():
            failures.append(f"{relative_path} must document image download guardrails")
        if "sha-256 cache filenames" not in text.lower():
            failures.append(f"{relative_path} must document SHA-256 cache filenames")
        if "memory cache entry guards" not in text.lower():
            failures.append(f"{relative_path} must document memory cache entry guards")
        if "http image url guard" not in text.lower():
            failures.append(f"{relative_path} must document HTTP image URL guardrails")
        if "oauth callback uri guard" not in text.lower():
            failures.append(f"{relative_path} must document OAuth callback URI guardrails")
        if "oauth callback path guard" not in text.lower():
            failures.append(f"{relative_path} must document OAuth callback path guardrails")
        if "oauth callback verifier guard" not in text.lower():
            failures.append(f"{relative_path} must document OAuth callback verifier guardrails")
        if "oauth callback token guard" not in text.lower():
            failures.append(f"{relative_path} must document OAuth callback token guardrails")
        if "sanitized oauth error logging" not in text.lower():
            failures.append(f"{relative_path} must document sanitized OAuth error logging")
        if "local editor metadata" not in text.lower():
            failures.append(f"{relative_path} must document local editor metadata guardrails")
        if "make lint" not in text or "make test" not in text or "make build" not in text or "make check" not in text:
            failures.append(f"{relative_path} must document standard Make gate targets")
    if "image download guard" not in changes.lower():
        failures.append("CHANGES must record image download guardrails")
    if "sha-256 cache filenames" not in changes.lower():
        failures.append("CHANGES must record SHA-256 cache filenames")
    if "memory cache entry guards" not in changes.lower():
        failures.append("CHANGES must record memory cache entry guards")
    if "http image url guard" not in changes.lower():
        failures.append("CHANGES must record HTTP image URL guardrails")
    if "oauth callback uri guard" not in changes.lower():
        failures.append("CHANGES must record OAuth callback URI guardrails")
    if "oauth callback path guard" not in changes.lower():
        failures.append("CHANGES must record OAuth callback path guardrails")
    if "oauth callback verifier guard" not in changes.lower():
        failures.append("CHANGES must record OAuth callback verifier guardrails")
    if "oauth callback token guard" not in changes.lower():
        failures.append("CHANGES must record OAuth callback token guardrails")
    if "sanitized oauth error logging" not in changes.lower():
        failures.append("CHANGES must record sanitized OAuth error logging")
    if "local editor metadata" not in changes.lower():
        failures.append("CHANGES must record local editor metadata guardrails")
    if "make lint" not in changes or "make test" not in changes or "make build" not in changes or "make check" not in changes:
        failures.append("CHANGES must record standard Make gate aliases")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("musichackday-android baseline checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
