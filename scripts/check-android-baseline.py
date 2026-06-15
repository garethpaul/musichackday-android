#!/usr/bin/env python3
"""Static baseline checks for the Music Hack Day Android project."""

from pathlib import Path
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_MAKEFILE = """ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))

.PHONY: build check lint static-check test verify

PYTHON ?= python3

check: verify

verify: static-check

lint test build: static-check

static-check:
\t$(PYTHON) "$(ROOT)/scripts/check-android-baseline.py"
"""
CONSTANTS_EXAMPLE = "app/src/main/java/com/twitterdev/rdio/app/Constants.java.example"
REQUIRED_FILES = [
    ".github/workflows/check.yml",
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
    "docs/plans/2026-06-10-hosted-static-validation.md",
    "docs/plans/2026-06-10-https-profile-images.md",
    "docs/plans/2026-06-12-album-art-connection-guard.md",
    "docs/plans/2026-06-12-checkout-credential-boundary.md",
    "docs/plans/2026-06-13-location-independent-make.md",
    "docs/plans/2026-06-14-twitter-authorization-origin-guard.md",
    "docs/plans/2026-06-14-twitter-search-failure-guard.md",
    "docs/plans/2026-06-15-twitter-navigation-ui-thread.md",
    "docs/plans/2026-06-15-twitter-login-inflight-guard.md",
    "docs/plans/2026-06-15-rdio-authorization-flow-guard.md",
    "docs/plans/2026-06-15-twitter-search-view-lookup-ui-thread.md",
    "docs/plans/2026-06-15-twitter-callback-inflight-guard.md",
    "docs/plans/2026-06-15-twitter-callback-state-snapshot.md",
]
TOKEN_LOG_PATTERNS = [
    re.compile(r"Log\.[a-z]\([^;]*(accessToken|accessTokenSecret|getToken\(|getTokenSecret\()", re.IGNORECASE),
    re.compile(r"Access token(?: secret)?:\s*\"\s*\+"),
    re.compile(r"Twitter OAuth Token"),
]


def read_text(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8", errors="replace")


def markdown_section(text: str, heading: str) -> str:
    match = re.search(
        rf"(?ms)^## {re.escape(heading)}\s*$\n(.*?)(?=^## |\Z)",
        text,
    )
    return match.group(1).strip() if match else ""


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
    if makefile != EXPECTED_MAKEFILE:
        failures.append(
            "Makefile must exactly preserve rooted SDK-free aliases and the Python override"
        )

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
    if (
        "private boolean isTrustedTwitterAuthenticationUri(Uri uri)" not in main_activity
        or '"https".equals(uri.getScheme())' not in main_activity
        or '"api.twitter.com".equals(uri.getHost())' not in main_activity
        or "uri.getPort() == -1" not in main_activity
        or '"/oauth/authenticate".equals(uri.getPath())' not in main_activity
        or "if (!isTrustedTwitterAuthenticationUri(authenticationUri))" not in main_activity
        or "new Intent(Intent.ACTION_VIEW, authenticationUri)" not in main_activity
    ):
        failures.append("MainActivity must restrict outbound Twitter authorization to the canonical HTTPS origin")
    token_exchange = main_activity.split("accessToken = callbackTwitter.getOAuthAccessToken", 1)[1].split("} catch (Exception e)", 1)[0]
    token_handoff_index = token_exchange.find("MainActivity.this.runOnUiThread(new Runnable()")
    token_navigation_index = token_exchange.find("startActivity(myIntent)")
    authorization_thread = main_activity.split("requestToken = twitter", 1)[1].split("} catch (Exception e)", 1)[0]
    authorization_validation_index = authorization_thread.find("if (!isTrustedTwitterAuthenticationUri(authenticationUri))")
    authorization_handoff_index = authorization_thread.find("MainActivity.this.runOnUiThread(new Runnable()")
    authorization_navigation_index = authorization_thread.find("MainActivity.this.startActivity(new Intent(Intent.ACTION_VIEW, authenticationUri))")
    if not (0 <= token_handoff_index < token_navigation_index):
        failures.append("Twitter access-token success navigation must run on the activity UI thread")
    callback_block = main_activity.split("if (isTwitterCallback(uri))", 1)[1].split("private boolean isTwitterLoggedInAlready()", 1)[0]
    callback_validation_index = callback_block.find("!matchesRequestToken(callbackToken, requestToken)")
    callback_twitter_snapshot_index = callback_block.find("final Twitter callbackTwitter = twitter")
    callback_token_snapshot_index = callback_block.find("final RequestToken callbackRequestToken = requestToken")
    callback_guard_index = callback_block.find("if (twitterCallbackExchangeInFlight)")
    callback_acquire_index = callback_block.find("twitterCallbackExchangeInFlight = true")
    callback_thread_index = callback_block.find("Thread thread = new Thread")
    callback_success_release_index = callback_block.find("twitterCallbackExchangeInFlight = false", callback_thread_index)
    callback_success_navigation_index = callback_block.find("startActivity(myIntent)", callback_success_release_index)
    callback_worker_failure_index = callback_block.find('logTwitterLoginFailure("Access token exchange")')
    callback_worker_release_index = callback_block.rfind("finishTwitterCallbackExchange()", 0, callback_worker_failure_index)
    callback_setup_failure_index = callback_block.find('logTwitterLoginFailure("OAuth callback handling")')
    callback_setup_release_index = callback_block.rfind("finishTwitterCallbackExchange()", 0, callback_setup_failure_index)
    if not (
        "private static boolean twitterCallbackExchangeInFlight;" in main_activity
        and 0 <= callback_validation_index < callback_twitter_snapshot_index < callback_token_snapshot_index
        and callback_token_snapshot_index < callback_guard_index < callback_acquire_index < callback_thread_index
    ):
        failures.append("Twitter callbacks must reject overlapping access-token exchanges after identity validation")
    if (
        "accessToken = callbackTwitter.getOAuthAccessToken(\n                                        callbackRequestToken, verifier);" not in callback_block
        or "accessToken = twitter.getOAuthAccessToken" in callback_block
        or "accessToken = callbackTwitter.getOAuthAccessToken(\n                                        requestToken, verifier);" in callback_block
    ):
        failures.append("Twitter callback workers must exchange only the validated OAuth state snapshots")
    if not (
        0 <= callback_success_release_index < callback_success_navigation_index
        and 0 <= callback_worker_release_index < callback_worker_failure_index
        and callback_worker_failure_index < callback_setup_release_index < callback_setup_failure_index
        and "private void finishTwitterCallbackExchange()" in main_activity
    ):
        failures.append("Twitter callback exchange ownership must release on every terminal path")
    if not (
        0 <= authorization_validation_index < authorization_handoff_index < authorization_navigation_index
    ):
        failures.append("Twitter authorization browser navigation must run on the UI thread after origin validation")
    login_method = main_activity.split("private void loginToTwitter()", 1)[1].split("private void finishTwitterLoginAttempt()", 1)[0]
    login_guard_index = login_method.find("if (twitterCallbackExchangeInFlight || twitterLoginInFlight)")
    login_acquire_index = login_method.find("twitterLoginInFlight = true")
    login_thread_index = login_method.find("Thread thread = new Thread")
    invalid_origin_index = login_method.find("if (!isTrustedTwitterAuthenticationUri(authenticationUri))")
    invalid_origin_release_index = login_method.find("finishTwitterLoginAttempt()", invalid_origin_index)
    success_release_index = login_method.find("twitterLoginInFlight = false", invalid_origin_release_index)
    success_navigation_index = login_method.find("MainActivity.this.startActivity", success_release_index)
    request_failure_index = login_method.find('logTwitterLoginFailure("Request token creation")')
    request_failure_catch_index = login_method.rfind("} catch (Exception e)", 0, request_failure_index)
    request_failure_release_index = login_method.rfind("finishTwitterLoginAttempt()", 0, request_failure_index)
    setup_failure_index = login_method.find('logTwitterLoginFailure("Request token setup")')
    setup_failure_catch_index = login_method.rfind("} catch (Exception e)", 0, setup_failure_index)
    setup_release_index = login_method.rfind("twitterLoginInFlight = false", 0, setup_failure_index)
    if not (
        "private boolean twitterLoginInFlight;" in main_activity
        and 0 <= login_guard_index < login_acquire_index < login_thread_index
    ):
        failures.append("Twitter login must reject overlapping request-token workers before acquiring ownership")
    if not (
        0 <= invalid_origin_index < invalid_origin_release_index
        and 0 <= request_failure_catch_index < request_failure_release_index < request_failure_index
        and 0 <= setup_failure_catch_index < setup_release_index < setup_failure_index
    ):
        failures.append("Twitter login failures must release request-token ownership")
    if not (0 <= success_release_index < success_navigation_index):
        failures.append("Twitter login success must release ownership before browser navigation")
    finish_login_method = main_activity.split("private void finishTwitterLoginAttempt()", 1)[1].split("private void logTwitterLoginFailure", 1)[0]
    if (
        "MainActivity.this.runOnUiThread(new Runnable()" not in finish_login_method
        or "twitterLoginInFlight = false;" not in finish_login_method
    ):
        failures.append("Twitter login failure release must return to the activity UI thread")

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
    if "isHttpsImageUrl" not in image_download or "URLUtil.isHttpsUrl" not in image_download or "URLUtil.isHttpUrl" in image_download or "params.length == 0" not in image_download:
        failures.append("ImageDownload must guard missing URLs and accept only HTTPS images")
    rdio_app = read_text("app/src/main/java/com/twitterdev/rdio/app/RdioApp.java")
    if (
        'Log.w(TAG, "Rdio authorization failed")' not in rdio_app
        or "EXTRA_ERROR_CODE" in rdio_app
        or "EXTRA_ERROR_DESCRIPTION" in rdio_app
        or 'Log.v(TAG, "ERROR: "' in rdio_app
    ):
        failures.append("Rdio authorization errors must use sanitized action-level logging")
    rdio_authorization_method = rdio_app.split(
        "private void startRdioAuthorization()", 1
    )[1].split("private boolean hasRdioCredential", 1)[0]
    rdio_launch_guard_index = rdio_authorization_method.find("if (rdioAuthorizationInFlight)")
    rdio_launch_acquire_index = rdio_authorization_method.find("rdioAuthorizationInFlight = true")
    rdio_launch_index = rdio_authorization_method.find(
        "startActivityForResult(authorizationIntent, RDIO_AUTHORIZATION_REQUEST)"
    )
    if not (
        "private boolean rdioAuthorizationInFlight;" in rdio_app
        and "private static final int RDIO_AUTHORIZATION_REQUEST = 1;" in rdio_app
        and "STATE_RDIO_AUTHORIZATION_IN_FLIGHT" in rdio_app
        and "savedInstanceState.getBoolean(STATE_RDIO_AUTHORIZATION_IN_FLIGHT, false)" in rdio_app
        and "outState.putBoolean(STATE_RDIO_AUTHORIZATION_IN_FLIGHT, rdioAuthorizationInFlight)" in rdio_app
        and "rdio.cleanup();\n            rdio = null;" in rdio_app
        and rdio_app.count("startRdioAuthorization();") == 2
        and rdio_app.count("startActivityForResult(") == 1
        and 0 <= rdio_launch_guard_index < rdio_launch_acquire_index < rdio_launch_index
        and "rdioAuthorizationInFlight = false;" in rdio_authorization_method
    ):
        failures.append("Rdio authorization launches must be centralized and reject overlap")
    rdio_result_method = rdio_app.split(
        "public void onActivityResult(int requestCode, int resultCode, Intent data)", 1
    )[1].split("private void startRdioAuthorization()", 1)[0]
    rdio_result_release_index = rdio_result_method.find("rdioAuthorizationInFlight = false")
    rdio_result_status_guard_index = rdio_result_method.find(
        "if (resultCode != RESULT_OK || data == null)"
    )
    rdio_result_token_index = rdio_result_method.find(
        'String returnedToken = data.getStringExtra("token")'
    )
    rdio_result_token_guard_index = rdio_result_method.find(
        "if (!hasRdioCredential(returnedToken) || !hasRdioCredential(returnedTokenSecret))"
    )
    rdio_result_install_index = rdio_result_method.find(
        "rdio.setTokenAndSecret(accessToken, accessTokenSecret)"
    )
    rdio_result_prepare_index = rdio_result_method.find("rdio.prepareForPlayback()")
    if not (
        0 <= rdio_result_release_index < rdio_result_status_guard_index
        < rdio_result_token_index < rdio_result_token_guard_index
        < rdio_result_install_index < rdio_result_prepare_index
        and rdio_result_method.count("return;") >= 3
        and rdio_result_method.count('Log.w(TAG, "Rdio authorization failed")') == 2
        and "value != null && value.trim().length() > 0" in rdio_app
        and rdio_result_method.count("rdio.prepareForPlayback()") == 1
    ):
        failures.append("Rdio authorization results must validate both credentials before playback preparation")
    if "getBiggerProfileImageURLHttps()" not in rdio_app or "getBiggerProfileImageURL()" in rdio_app:
        failures.append("RdioApp must select Twitter profile images from the HTTPS URL field")
    search_task = rdio_app.split("private class getSearch", 1)[1]
    search_call_index = search_task.find("result = twitter.search(query)")
    search_catch_index = search_task.find("catch (TwitterException e)")
    search_log_index = search_task.find('Log.e(TAG, "Twitter search failed")')
    search_return_index = search_task.find("return null;", search_catch_index)
    search_iteration_index = search_task.find("for (twitter4j.Status status : result.getTweets())")
    if (
        not (0 <= search_call_index < search_catch_index < search_log_index < search_return_index < search_iteration_index)
        or 'Log.v("Search for ", params[0])' in search_task
        or 'Log.v("LoggedIn", "getUser..doInBackground")' in search_task
        or "e.printStackTrace()" in search_task
    ):
        failures.append("Twitter search failures must use redacted logging and return before result iteration")
    if (
        'Log.e(TAG, "Twitter result formatting failed")' not in search_task
        or search_task.find('Log.e(TAG, "Twitter result formatting failed")') > search_task.find("continue;")
    ):
        failures.append("Twitter result formatting failures must use redacted logging and skip malformed rows")
    search_ui_handoff_index = search_task.find("runOnUiThread(new Runnable()")
    search_view_lookup_index = search_task.find("findViewById(R.id.list)")
    search_adapter_index = search_task.find("listView.setAdapter(a)")
    if not (
        search_task.count("findViewById(R.id.list)") == 1
        and 0 <= search_ui_handoff_index < search_view_lookup_index < search_adapter_index
    ):
        failures.append("Twitter search view lookup and adapter mutation must run on the activity UI thread")
    artwork_task = rdio_app.split("// Fetch album art in the background", 1)[1].split("artworkTask.execute(track)", 1)[0]
    if (
        "URLUtil.isHttpsUrl(artworkUrl)" not in artwork_task
        or "HttpURLConnection connection" not in artwork_task
        or "connection.setConnectTimeout(10000)" not in artwork_task
        or "connection.setReadTimeout(10000)" not in artwork_task
    ):
        failures.append("album art downloads must require HTTPS and bounded connection timeouts")
    if "finally {" not in artwork_task or "bufferedInputStream.close()" not in artwork_task or "connection.disconnect()" not in artwork_task:
        failures.append("album art downloads must close streams and disconnect in all paths")
    if "Downloading album art:" in artwork_task or 'Log.e(TAG, "Album art download failed", e)' in artwork_task:
        failures.append("album art failure logging must not include media URLs or exception details")
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
        "docs/plans/2026-06-10-hosted-static-validation.md",
        "docs/plans/2026-06-10-https-profile-images.md",
        "docs/plans/2026-06-12-album-art-connection-guard.md",
        "docs/plans/2026-06-12-checkout-credential-boundary.md",
        "docs/plans/2026-06-14-rdio-error-redaction.md",
    ]:
        if not (ROOT / relative_path).is_file():
            continue
        plan = read_text(relative_path)
        if "status: completed" not in plan:
            failures.append(f"{relative_path} must record completed status")
        if "scripts/check-android-baseline.py" not in plan:
            failures.append(f"{relative_path} must reference the active baseline checker")

    album_art_plan = read_text("docs/plans/2026-06-12-album-art-connection-guard.md")
    album_art_status = re.findall(r"(?mi)^status:\s*(.+?)\s*$", album_art_plan)
    album_art_work = markdown_section(album_art_plan, "Work Completed")
    album_art_verification = markdown_section(album_art_plan, "Verification Completed")
    if album_art_status != ["completed"] or not album_art_work:
        failures.append("album art connection guard plan must record one completed status and completed work")
    if not album_art_verification or re.search(
        r"(?i)\b(?:pending|todo|tbd|not run)\b", album_art_verification
    ):
        failures.append("album art connection guard plan must record completed verification")
    for evidence in [
        "python3 -m py_compile scripts/check-android-baseline.py",
        "make lint",
        "make test",
        "make build",
        "make check",
        "git diff --check",
        "27397456751",
        "27397458335",
        "1fd944d8b02118d817f98603aed3050bceb6dc32",
        "URLUtil.isHttpsUrl(artworkUrl)",
        "connection.setConnectTimeout(10000)",
        "connection.setReadTimeout(10000)",
        "bufferedInputStream.close()",
        "connection.disconnect()",
        "Album art download failed",
    ]:
        if evidence not in album_art_verification:
            failures.append(f"album art verification must record {evidence}")

    workflow = read_text(".github/workflows/check.yml")
    workflow_files = [
        *sorted((ROOT / ".github/workflows").glob("*.yml")),
        *sorted((ROOT / ".github/workflows").glob("*.yaml")),
    ]
    for expected in [
        "permissions:\n  contents: read",
        "cancel-in-progress: true",
        "runs-on: ubuntu-24.04",
        "timeout-minutes: 10",
        "actions/checkout@df4cb1c069e1874edd31b4311f1884172cec0e10",
        "actions/setup-python@a309ff8b426b58ec0e2a45f0f869d46889d02405",
        'python-version: "3.12"',
        "run: make check",
    ]:
        if expected not in workflow:
            failures.append(f"Check workflow must keep {expected}")

    checkout_action = (
        "actions/checkout@df4cb1c069e1874edd31b4311f1884172cec0e10"
    )
    checkout_blocks = re.findall(
        rf"(?m)^(?P<indent> *)- +uses: +{re.escape(checkout_action)}[^\n]*\n"
        rf"(?P=indent)  with:\n"
        rf"(?P=indent)    persist-credentials: +false *$",
        workflow,
    )
    checkout_actions = re.findall(
        r"(?m)^\s*-\s+uses:\s+actions/checkout@",
        workflow,
    )
    if not (
        len(workflow_files) == 1
        and workflow.count("permissions:") == 1
        and workflow.count("contents: read") == 1
        and not re.search(r"(?m)^\s*[A-Za-z-]+:\s*write\s*$", workflow)
        and len(checkout_actions) == 1
        and workflow.count(checkout_action) == 1
        and len(checkout_blocks) == 1
        and workflow.count("persist-credentials: false") == 1
        and "persist-credentials: true" not in workflow
    ):
        failures.append(
            "Check workflow must keep one read-only permission block and one "
            "pinned, credential-free checkout"
        )

    checkout_plan = read_text(
        "docs/plans/2026-06-12-checkout-credential-boundary.md"
    )
    location_independent_make_plan = read_text(
        "docs/plans/2026-06-13-location-independent-make.md"
    )
    checkout_status = re.findall(r"(?mi)^status:\s*(.+?)\s*$", checkout_plan)
    checkout_work = markdown_section(checkout_plan, "Work Completed")
    checkout_verification = markdown_section(
        checkout_plan, "Verification Completed"
    )
    if not (
        checkout_status == ["completed"]
        and checkout_work
        and "make check" in checkout_verification
    ):
        failures.append(
            "checkout credential plan must record one completed status, "
            "completed work, and make check verification"
        )

    readme = read_text("README.md")
    vision = read_text("VISION.md")
    security = read_text("SECURITY.md")
    changes = read_text("CHANGES.md")
    authorization_origin_plan = read_text("docs/plans/2026-06-14-twitter-authorization-origin-guard.md")
    if "make -f /path/to/musichackday-android/Makefile check" not in readme:
        failures.append("README must document location-independent Makefile invocation")
    if not all(
        evidence in location_independent_make_plan.lower()
        for evidence in [
            "status: completed",
            "root and external-directory",
            "six isolated hostile mutations",
        ]
    ):
        failures.append(
            "location-independent Make plan must record completed root, external, and mutation verification"
        )
    for relative_path, text in [("README.md", readme), ("VISION.md", vision), ("SECURITY.md", security)]:
        if "image download guard" not in text.lower():
            failures.append(f"{relative_path} must document image download guardrails")
        if "sha-256 cache filenames" not in text.lower():
            failures.append(f"{relative_path} must document SHA-256 cache filenames")
        if "memory cache entry guards" not in text.lower():
            failures.append(f"{relative_path} must document memory cache entry guards")
        if "http image url guard" not in text.lower():
            failures.append(f"{relative_path} must document HTTP image URL guardrails")
        if "https profile image guard" not in text.lower():
            failures.append(f"{relative_path} must document HTTPS profile image guardrails")
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
        if "album art connection guard" not in text.lower():
            failures.append(f"{relative_path} must document the album art connection guard")
        if "twitter authorization origin guard" not in text.lower():
            failures.append(f"{relative_path} must document the Twitter authorization origin guard")
        if "twitter login in-flight guard" not in text.lower():
            failures.append(f"{relative_path} must document the Twitter login in-flight guard")
        if "twitter callback state snapshot" not in text.lower():
            failures.append(f"{relative_path} must document the Twitter callback state snapshot")
        if "rdio authorization flow guard" not in text.lower():
            failures.append(f"{relative_path} must document the Rdio authorization flow guard")
        if "twitter search view lookup ui thread" not in text.lower():
            failures.append(f"{relative_path} must document the Twitter search view lookup UI thread rule")
    if "image download guard" not in changes.lower():
        failures.append("CHANGES must record image download guardrails")
    if "sha-256 cache filenames" not in changes.lower():
        failures.append("CHANGES must record SHA-256 cache filenames")
    if "memory cache entry guards" not in changes.lower():
        failures.append("CHANGES must record memory cache entry guards")
    if "http image url guard" not in changes.lower():
        failures.append("CHANGES must record HTTP image URL guardrails")
    if "https profile image guard" not in changes.lower():
        failures.append("CHANGES must record HTTPS profile image guardrails")
    if "album art connection guard" not in changes.lower():
        failures.append("CHANGES must record album art connection guardrails")
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
    if "twitter authorization origin guard" not in changes.lower():
        failures.append("CHANGES must record the Twitter authorization origin guard")
    if "rdio authorization flow guard" not in changes.lower():
        failures.append("CHANGES must record the Rdio authorization flow guard")
    if "twitter search view lookup ui thread" not in changes.lower():
        failures.append("CHANGES must record the Twitter search view lookup UI thread rule")
    for relative_path in ["README.md", "VISION.md", "SECURITY.md", "CHANGES.md"]:
        if "twitter search failure guard" not in read_text(relative_path).lower():
            failures.append(f"{relative_path} must document the Twitter search failure guard")
        if "twitter navigation ui thread handoff" not in read_text(relative_path).lower():
            failures.append(f"{relative_path} must document the Twitter navigation UI thread handoff")
    search_failure_plan = read_text("docs/plans/2026-06-14-twitter-search-failure-guard.md")
    search_failure_verification = markdown_section(search_failure_plan, "Verification Completed")
    if (
        "status: completed" not in search_failure_plan
        or "All four Make gates passed" not in search_failure_verification
        or "Seven isolated hostile mutations were rejected" not in search_failure_verification
        or "external directory" not in search_failure_verification
        or re.search(r"(?i)\b(?:pending|todo|tbd|not run)\b", search_failure_verification)
    ):
        failures.append("Twitter search failure guard plan must record completed verification")
    navigation_plan = read_text("docs/plans/2026-06-15-twitter-navigation-ui-thread.md")
    navigation_verification = markdown_section(navigation_plan, "Verification Completed")
    if (
        "status: completed" not in navigation_plan
        or "All four Make gates passed" not in navigation_verification
        or "Six isolated hostile mutations were rejected" not in navigation_verification
        or "external directory" not in navigation_verification
        or re.search(r"(?i)\b(?:pending|todo|tbd|not run)\b", navigation_verification)
    ):
        failures.append("Twitter navigation UI thread handoff plan must record completed verification")
    login_inflight_plan = read_text("docs/plans/2026-06-15-twitter-login-inflight-guard.md")
    login_inflight_verification = markdown_section(login_inflight_plan, "Verification Completed")
    if (
        "status: completed" not in login_inflight_plan.lower()
        or "All four Make gates passed" not in login_inflight_verification
        or "Eight isolated hostile mutations were rejected" not in login_inflight_verification
        or "external directory" not in login_inflight_verification
        or re.search(r"(?i)\b(?:pending|todo|tbd|not run)\b", login_inflight_verification)
    ):
        failures.append("Twitter login in-flight guard plan must record completed verification")
    for relative_path in ["README.md", "VISION.md", "SECURITY.md", "CHANGES.md"]:
        if "rdio authorization error redaction" not in read_text(relative_path).lower():
            failures.append(f"{relative_path} must document Rdio authorization error redaction")
    rdio_error_plan = read_text("docs/plans/2026-06-14-rdio-error-redaction.md")
    if "status: completed" not in rdio_error_plan or "Five isolated hostile mutations were rejected" not in rdio_error_plan:
        failures.append("Rdio authorization error redaction plan must record completed verification")
    rdio_flow_plan = read_text("docs/plans/2026-06-15-rdio-authorization-flow-guard.md")
    rdio_flow_verification = markdown_section(rdio_flow_plan, "Verification Completed")
    if (
        "status: completed" not in rdio_flow_plan.lower()
        or "All four Make gates passed" not in rdio_flow_verification
        or "Eight isolated hostile mutations were rejected" not in rdio_flow_verification
        or "external directory" not in rdio_flow_verification
        or re.search(r"(?i)\b(?:pending|todo|tbd|not run)\b", rdio_flow_verification)
    ):
        failures.append("Rdio authorization flow guard plan must record completed verification")
    search_view_plan = read_text("docs/plans/2026-06-15-twitter-search-view-lookup-ui-thread.md")
    search_view_verification = markdown_section(search_view_plan, "Verification Completed")
    if (
        "status: completed" not in search_view_plan.lower()
        or "All four Make gates passed" not in search_view_verification
        or "Six isolated hostile mutations were rejected" not in search_view_verification
        or "external directory" not in search_view_verification
        or re.search(r"(?i)\b(?:pending|todo|tbd|not run)\b", search_view_verification)
    ):
        failures.append("Twitter search view lookup UI thread plan must record completed verification")
    callback_inflight_plan = read_text("docs/plans/2026-06-15-twitter-callback-inflight-guard.md")
    callback_inflight_verification = markdown_section(callback_inflight_plan, "Verification Completed")
    if (
        "status: completed" not in callback_inflight_plan.lower()
        or "All four Make gates passed" not in callback_inflight_verification
        or "Eight isolated hostile mutations were rejected" not in callback_inflight_verification
        or "external directory" not in callback_inflight_verification
        or re.search(r"(?i)\b(?:pending|todo|tbd|not run)\b", callback_inflight_verification)
    ):
        failures.append("Twitter callback exchange in-flight guard plan must record completed verification")
    for relative_path in ["README.md", "VISION.md", "SECURITY.md", "CHANGES.md"]:
        if "twitter callback exchange in-flight guard" not in read_text(relative_path).lower():
            failures.append(f"{relative_path} must document the Twitter callback exchange in-flight guard")
    callback_snapshot_plan = read_text("docs/plans/2026-06-15-twitter-callback-state-snapshot.md")
    callback_snapshot_verification = markdown_section(callback_snapshot_plan, "Verification Completed")
    if (
        "status: completed" not in callback_snapshot_plan.lower()
        or "All four Make gates passed" not in callback_snapshot_verification
        or "Seven isolated hostile mutations were rejected" not in callback_snapshot_verification
        or "external directory" not in callback_snapshot_verification
        or re.search(r"(?i)\b(?:pending|todo|tbd|not run)\b", callback_snapshot_verification)
    ):
        failures.append("Twitter callback state snapshot plan must record completed verification")
    if "make lint" not in changes or "make test" not in changes or "make build" not in changes or "make check" not in changes:
        failures.append("CHANGES must record standard Make gate aliases")
    if "status: completed" not in authorization_origin_plan or "hostile mutations" not in authorization_origin_plan:
        failures.append("Twitter authorization origin guard plan must record completed verification")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("musichackday-android baseline checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
