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
    "app/libs/rdio-android-sdk.jar",
    "app/libs/signpost-commonshttp4-1.2.1.1.jar",
    "app/libs/signpost-core-1.2.1.1.jar",
    "app/libs/twitter4j-core-4.0.1.jar",
    CONSTANTS_EXAMPLE,
    "docs/plans/2026-06-08-credential-baseline.md",
    "docs/plans/2026-06-08-image-download-guards.md",
    "docs/plans/2026-06-08-musichackday-android-baseline.md",
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
    for expected in ["Constants.java", "Constants.class", "local.properties", "*.jks", "*.keystore", "*.p12"]:
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
    for expected in ["YOUR_TWITTER_API_KEY", "YOUR_RDIO_APP_KEY", "app://twitter-dev"]:
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

    file_cache = read_text("app/src/main/java/com/twitterdev/rdio/app/FileCache.java")
    if "context.getCacheDir()" not in file_cache:
        failures.append("FileCache must use the app-private cache directory")
    if "Environment.getExternalStorageDirectory" in file_cache:
        failures.append("FileCache must not use shared external storage")
    if "url-download" in read_text("app/src/main/java/com/twitterdev/rdio/app/TweetAdapter.java"):
        failures.append("tweet image URLs must not be logged")
    image_download = read_text("app/src/main/java/com/twitterdev/rdio/app/ImageDownload.java")
    if "URLUtil.isValidUrl" not in image_download or "params.length == 0" not in image_download:
        failures.append("ImageDownload must guard missing or invalid image URLs")
    if "ImageView imageView = imageViewReference.get()" not in image_download or "imageView == null" not in image_download:
        failures.append("ImageDownload must guard recycled ImageView references")

    if not os.access(ROOT / "gradlew", os.X_OK):
        failures.append("gradlew must be executable")

    for relative_path in [
        "docs/plans/2026-06-08-credential-baseline.md",
        "docs/plans/2026-06-08-image-download-guards.md",
        "docs/plans/2026-06-08-musichackday-android-baseline.md",
    ]:
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
    if "image download guard" not in changes.lower():
        failures.append("CHANGES must record image download guardrails")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("musichackday-android baseline checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
