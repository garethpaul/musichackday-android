#!/usr/bin/env python3
import sys
sys.dont_write_bytecode = True

"""Static baseline checks for the Music Hack Day Android project."""

from pathlib import Path
import hashlib
import os
import re
import shutil
import stat
import subprocess
import tempfile
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_TEST_COUNT = 94
SHADOWED_STDLIB_NAMES = {
    "_hashlib",
    "atexit",
    "hashlib",
    "importlib",
    "os",
    "pathlib",
    "re",
    "shutil",
    "sitecustomize",
    "stat",
    "subprocess",
    "sys",
    "tempfile",
    "unittest",
    "usercustomize",
    "xml",
}
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
    "app/src/main/java/com/twitterdev/rdio/app/Utils.java",
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
    "docs/plans/issue-1-copy-stream-errors.md",
    "docs/plans/2026-06-19-auth-playback-stack-integration.md",
    "docs/plans/2026-06-21-spaced-makefile-path.md",
]
TOKEN_LOG_PATTERNS = [
    re.compile(r"Log\.[a-z]\([^;]*(accessToken|accessTokenSecret|getToken\(|getTokenSecret\()", re.IGNORECASE),
    re.compile(r"Access token(?: secret)?:\s*\"\s*\+"),
    re.compile(r"Twitter OAuth Token"),
]
REVIEWED_FILE_SHA256 = {
    "app/src/main/java/com/twitterdev/rdio/app/RdioApp.java": (
        "fb91ad06a10932969adf680e877b76db2b4c0559513cf2bccb471fbb5fd1bc3d"
    ),
    ".github/workflows/check.yml": (
        "3ac196785a75b7a744a1690a396feac24cf1b1fffd189dc2474ff01e6d01b57f"
    ),
}
EVIDENCE_PLAN_PATH = "docs/plans/2026-06-12-album-art-connection-guard.md"
EVIDENCE_PLAN_SHA256 = (
    "a3698f126caa282ffe3242a37dd1bec6e29b0d2fbd086afcf03e324f3937eb3e"
)
REVIEWED_TEST_SHA256 = {
    "tests/test_android_baseline.py": "4191167728954a204d21289e5b96a8310656540364bc5fafde78072890719229",
    "tests/test_reviewed_hashes.py": "7fef7f030cf4c2a1c079bad22381bc1d9a74d4f65ce9c712fab97071f90009a4",
}
REVIEWED_BYTE_CONTRACT = '''The following raw bytes were reviewed together:

- `app/src/main/java/com/twitterdev/rdio/app/RdioApp.java`
  SHA-256: `fb91ad06a10932969adf680e877b76db2b4c0559513cf2bccb471fbb5fd1bc3d`
- `.github/workflows/check.yml`
  SHA-256: `3ac196785a75b7a744a1690a396feac24cf1b1fffd189dc2474ff01e6d01b57f`

Future legitimate changes require explicit review and coordinated updates to the protected file, checker constant, independent test constant, and this contract stanza.'''
ALBUM_ART_HOSTED_EVIDENCE = '''Completed locally on 2026-06-12:

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
`connection.setConnectTimeout(10000)`, `connection.setReadTimeout(10000)`,
`bufferedInputStream.close()`, `connection.disconnect()`, and the sanitized
`Album art download failed` message.'''
EXPECTED_MAKEFILE = '''.PHONY: build check lint static-check test unit-test verify

ifneq ($(origin MAKEFILE_LIST),file)
$(error MAKEFILE_LIST must not be overridden)
endif
override ROOT := $(shell path='$(subst ','"'"',$(MAKEFILE_LIST))'; path=$$(printf '%s\\n' "$$path" | sed 's/^ //'); dirname -- "$$path")
override SHELL := /bin/sh
override PATH := /opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin
override PYTHON := $(shell PATH=$(PATH) command -v python3)
RDIO_APP_SHA256 := fb91ad06a10932969adf680e877b76db2b4c0559513cf2bccb471fbb5fd1bc3d
WORKFLOW_SHA256 := 3ac196785a75b7a744a1690a396feac24cf1b1fffd189dc2474ff01e6d01b57f
TEST_ANDROID_SHA256 := 4191167728954a204d21289e5b96a8310656540364bc5fafde78072890719229
TEST_REVIEWED_SHA256 := 7fef7f030cf4c2a1c079bad22381bc1d9a74d4f65ce9c712fab97071f90009a4
EVIDENCE_PLAN_SHA256 := a3698f126caa282ffe3242a37dd1bec6e29b0d2fbd086afcf03e324f3937eb3e
EXPECTED_TEST_COUNT := 94

check verify test unit-test:
	@set -eu; test -n "$(PYTHON)"; test -x "$(PYTHON)"; $(PYTHON) -I -B -c 'import sys; raise SystemExit(0 if sys.version_info[:2] in {(3, 12), (3, 14)} else 1)'; tmp=$$(/usr/bin/mktemp -d); trap '/bin/rm -rf "$$tmp"' EXIT; /bin/cp "$(ROOT)/scripts/check-android-baseline.py" "$$tmp/verifier.py"; /usr/bin/env -u PYTHONPATH -u PYTHONHOME -u PYTHONSTARTUP -u PYTHONPYCACHEPREFIX -u MHD_NESTED_GATE PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -I -B "$$tmp/verifier.py" --root "$(ROOT)" --expect-python 3.12,3.14 --gate; /usr/bin/git -C "$(ROOT)" diff --exit-code; /usr/bin/git -C "$(ROOT)" diff --cached --exit-code; test -z "$$(/usr/bin/git -C "$(ROOT)" status --porcelain=v1 --untracked-files=all)"

lint build static-check:
	@set -eu; test -n "$(PYTHON)"; test -x "$(PYTHON)"; $(PYTHON) -I -B -c 'import sys; raise SystemExit(0 if sys.version_info[:2] in {(3, 12), (3, 14)} else 1)'; tmp=$$(/usr/bin/mktemp -d); trap '/bin/rm -rf "$$tmp"' EXIT; /bin/cp "$(ROOT)/scripts/check-android-baseline.py" "$$tmp/verifier.py"; /usr/bin/env -u PYTHONPATH -u PYTHONHOME -u PYTHONSTARTUP -u PYTHONPYCACHEPREFIX -u MHD_NESTED_GATE PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -I -B "$$tmp/verifier.py" --root "$(ROOT)" --expect-python 3.12,3.14 --static
'''


def read_text(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8", errors="replace")


def read_bytes(relative_path: str) -> bytes:
    return (ROOT / relative_path).read_bytes()


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def make_hash_variable(relative_path: str) -> str:
    names = {
        "app/src/main/java/com/twitterdev/rdio/app/RdioApp.java": "RDIO_APP_SHA256",
        ".github/workflows/check.yml": "WORKFLOW_SHA256",
        EVIDENCE_PLAN_PATH: "EVIDENCE_PLAN_SHA256",
        "tests/test_android_baseline.py": "TEST_ANDROID_SHA256",
        "tests/test_reviewed_hashes.py": "TEST_REVIEWED_SHA256",
    }
    return names[relative_path]


def markdown_section(text: str, heading: str) -> str:
    match = re.search(
        rf"(?ms)^## {re.escape(heading)}\s*$\n(.*?)(?=^## |\Z)",
        text,
    )
    return match.group(1).strip() if match else ""


def markdown_subsection(text: str, heading: str) -> str:
    match = re.search(
        rf"(?ms)^### {re.escape(heading)}\s*$\n(.*?)(?=^### |^## |\Z)",
        text,
    )
    return match.group(1).strip() if match else ""


def strip_markdown_nonprose(text: str) -> str:
    without_comments = re.sub(r"(?s)<!--.*?-->", "", text)
    return re.sub(r"(?ms)^```[^\n]*\n.*?^```\s*$", "", without_comments)


def android_attr(name: str) -> str:
    return f"{{http://schemas.android.com/apk/res/android}}{name}"


def validate_reviewed_file_bytes(relative_path: str, content: bytes) -> list[str]:
    expected_sha256 = REVIEWED_FILE_SHA256.get(relative_path)
    if expected_sha256 is None:
        return [f"no reviewed byte contract exists for {relative_path}"]
    actual_sha256 = hashlib.sha256(content).hexdigest()
    if actual_sha256 != expected_sha256:
        return [
            f"{relative_path} must match reviewed SHA-256 {expected_sha256}; "
            f"found {actual_sha256}"
        ]
    return []


def validate_evidence_plan_bytes(content: bytes) -> list[str]:
    actual_sha256 = sha256_bytes(content)
    if actual_sha256 != EVIDENCE_PLAN_SHA256:
        return [
            f"{EVIDENCE_PLAN_PATH} must match reviewed SHA-256 "
            f"{EVIDENCE_PLAN_SHA256}; found {actual_sha256}"
        ]
    return []


def validate_test_inventory(root: Path) -> list[str]:
    failures = []
    tests_root = root / "tests"
    expected_paths = set(REVIEWED_TEST_SHA256)
    if not tests_root.is_dir() or tests_root.is_symlink():
        return ["tests must be a real directory containing the reviewed inventory"]
    actual_paths = set()
    for path in tests_root.rglob("*"):
        relative_path = path.relative_to(root).as_posix()
        if "__pycache__" in path.relative_to(tests_root).parts or path.suffix == ".pyc":
            continue
        actual_paths.add(relative_path)
        mode = path.lstat().st_mode
        if stat.S_ISLNK(mode):
            failures.append(f"test inventory path must not be a symlink: {relative_path}")
        elif not stat.S_ISREG(mode):
            failures.append(f"unexpected non-regular test inventory path: {relative_path}")
    if actual_paths != expected_paths:
        missing = sorted(expected_paths - actual_paths)
        added = sorted(actual_paths - expected_paths)
        if missing:
            failures.append("reviewed test inventory missing: " + ", ".join(missing))
        if added:
            failures.append("unreviewed test inventory present: " + ", ".join(added))
    for relative_path, expected_sha256 in REVIEWED_TEST_SHA256.items():
        path = root / relative_path
        try:
            mode = path.lstat().st_mode
        except FileNotFoundError:
            continue
        if not stat.S_ISREG(mode):
            continue
        if stat.S_IMODE(mode) != 0o644:
            failures.append(f"reviewed test file mode must be 0644: {relative_path}")
        actual_sha256 = sha256_bytes(path.read_bytes())
        if actual_sha256 != expected_sha256:
            failures.append(
                f"{relative_path} must match reviewed SHA-256 {expected_sha256}; "
                f"found {actual_sha256}"
            )
    return failures


def validate_import_shadow_inventory(root: Path) -> list[str]:
    failures = []
    for path in root.rglob("*"):
        relative_parts = path.relative_to(root).parts
        if ".git" in relative_parts or "__pycache__" in relative_parts:
            continue
        name = path.name
        shadow_name = name[:-3] if path.is_file() and name.endswith(".py") else name
        if shadow_name in SHADOWED_STDLIB_NAMES:
            failures.append(
                "repository import-shadow path is forbidden: "
                + path.relative_to(root).as_posix()
            )
    return failures


def validate_no_python_artifacts(root: Path) -> list[str]:
    failures = []
    for path in root.rglob("*"):
        if ".git" in path.relative_to(root).parts:
            continue
        if path.name == "__pycache__" or path.suffix in {".pyc", ".pyo"}:
            failures.append(
                "generated Python artifact is forbidden: "
                + path.relative_to(root).as_posix()
            )
    return failures


def sanitized_python_environment(source=None) -> dict[str, str]:
    environment = dict(os.environ if source is None else source)
    for name in list(environment):
        if name.startswith("PYTHON") or name == "MHD_NESTED_GATE":
            environment.pop(name)
    environment["PYTHONNOUSERSITE"] = "1"
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    return environment


def git_output(arguments: list[str], *, text: bool = False):
    return subprocess.run(
        ["git", *arguments],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=text,
        check=False,
    )


def validate_committed_protected_blobs() -> list[str]:
    failures = []
    for relative_path, expected_sha256 in REVIEWED_FILE_SHA256.items():
        result = git_output(["show", f"HEAD:{relative_path}"])
        if result.returncode != 0:
            failures.append(f"unable to read committed protected blob: {relative_path}")
            continue
        actual_sha256 = sha256_bytes(result.stdout)
        if actual_sha256 != expected_sha256:
            failures.append(
                f"committed {relative_path} must match reviewed SHA-256 "
                f"{expected_sha256}; found {actual_sha256}"
            )
        mode_result = git_output(["ls-tree", "HEAD", "--", relative_path], text=True)
        if not mode_result.stdout.startswith("100644 "):
            failures.append(f"committed protected path must be a regular file: {relative_path}")
    return failures


def repository_snapshot(root: Path):
    snapshot = {}
    for path in sorted(root.rglob("*")):
        if ".git" in path.relative_to(root).parts:
            continue
        relative_path = path.relative_to(root).as_posix()
        mode = path.lstat().st_mode
        if stat.S_ISREG(mode):
            value = ("file", stat.S_IMODE(mode), sha256_bytes(path.read_bytes()))
        elif stat.S_ISLNK(mode):
            value = ("symlink", os.readlink(path))
        elif stat.S_ISDIR(mode):
            value = ("directory", stat.S_IMODE(mode))
        else:
            value = ("other", stat.S_IFMT(mode), stat.S_IMODE(mode))
        snapshot[relative_path] = value
    status = git_output(["status", "--porcelain=v1", "-z", "--untracked-files=all"]).stdout
    return snapshot, status


def validate_repository_unchanged(before_snapshot) -> list[str]:
    after_snapshot = repository_snapshot(ROOT)
    if after_snapshot != before_snapshot:
        return ["repository files or git status changed while tests executed"]
    if not before_snapshot[1]:
        for arguments in [["diff", "--exit-code"], ["diff", "--cached", "--exit-code"]]:
            if git_output(arguments).returncode != 0:
                return ["tracked repository state changed while tests executed"]
    return []


def create_disposable_test_checkout(destination: Path) -> None:
    shutil.copytree(
        ROOT,
        destination,
        ignore=shutil.ignore_patterns(".git"),
    )
    subprocess.run(["git", "init", "-q"], cwd=destination, check=True)
    subprocess.run(["git", "config", "user.name", "Baseline Gate"], cwd=destination, check=True)
    subprocess.run(["git", "config", "user.email", "baseline@example.invalid"], cwd=destination, check=True)
    subprocess.run(["git", "add", "-A"], cwd=destination, check=True)
    subprocess.run(["git", "commit", "-qm", "test snapshot"], cwd=destination, check=True)


def run_reviewed_tests() -> tuple[int, list[str]]:
    with tempfile.TemporaryDirectory() as temporary_directory:
        test_root = Path(temporary_directory) / "repo"
        create_disposable_test_checkout(test_root)
        before_snapshot = repository_snapshot_at(test_root)
        result = run_isolated_test_process(test_root, EXPECTED_TEST_COUNT)
        sys.stdout.write(result.stdout)
        sys.stderr.write(result.stderr)
        failures = validate_snapshot_at(test_root, before_snapshot)
        return result.returncode, failures


def run_isolated_test_process(test_root: Path, expected_count: int, python_executable=None):
    runner_source = '''import pathlib
import sys
import unittest

root = pathlib.Path(sys.argv[1]).resolve()
expected_count = int(sys.argv[2])
suite = unittest.defaultTestLoader.discover(
    str(root / "tests"), pattern="test_*.py", top_level_dir=str(root / "tests")
)
result = unittest.TextTestRunner(verbosity=2).run(suite)
print(
    f"trusted-test-summary tests={result.testsRun} skipped={len(result.skipped)} "
    f"failures={len(result.failures)} errors={len(result.errors)}"
)
if result.testsRun != expected_count:
    print(f"expected {expected_count} tests, ran {result.testsRun}", file=sys.stderr)
    raise SystemExit(1)
if result.skipped:
    print(f"skipped={len(result.skipped)} is forbidden", file=sys.stderr)
    raise SystemExit(1)
raise SystemExit(0 if result.wasSuccessful() else 1)
'''
    with tempfile.TemporaryDirectory() as temporary_directory:
        runner_path = Path(temporary_directory) / "trusted-test-runner.py"
        runner_path.write_text(runner_source, encoding="utf-8")
        return subprocess.run(
            [
                python_executable or sys.executable,
                "-I",
                "-B",
                str(runner_path),
                str(test_root),
                str(expected_count),
            ],
            cwd=temporary_directory,
            env=sanitized_python_environment(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )


def repository_snapshot_at(root: Path):
    global ROOT
    original_root = ROOT
    ROOT = root
    try:
        return repository_snapshot(root)
    finally:
        ROOT = original_root


def validate_snapshot_at(root: Path, before_snapshot) -> list[str]:
    global ROOT
    original_root = ROOT
    ROOT = root
    try:
        return validate_repository_unchanged(before_snapshot)
    finally:
        ROOT = original_root


def expected_reviewed_byte_contract() -> str:
    return f'''The following raw bytes were reviewed together:

- `app/src/main/java/com/twitterdev/rdio/app/RdioApp.java`
  SHA-256: `{REVIEWED_FILE_SHA256["app/src/main/java/com/twitterdev/rdio/app/RdioApp.java"]}`
- `.github/workflows/check.yml`
  SHA-256: `{REVIEWED_FILE_SHA256[".github/workflows/check.yml"]}`

Future legitimate changes require explicit review and coordinated updates to the protected file, checker constant, independent test constant, and this contract stanza.'''


def validate_reviewed_contract_consistency() -> list[str]:
    if REVIEWED_BYTE_CONTRACT != expected_reviewed_byte_contract():
        return ["reviewed byte contract must exactly match the checker SHA-256 constants"]
    return []


def validate_album_art_connection_contract(rdio_app: str) -> list[str]:
    return validate_reviewed_file_bytes(
        "app/src/main/java/com/twitterdev/rdio/app/RdioApp.java",
        rdio_app.encode("utf-8"),
    )


def validate_album_art_evidence_contract(album_art_plan: bytes) -> list[str]:
    return validate_evidence_plan_bytes(album_art_plan)


def validate_makefile_contract(makefile: str) -> list[str]:
    if makefile != EXPECTED_MAKEFILE:
        return ["Makefile must match the canonical active test and static-check recipes"]
    return []


def validate_utils_copy_stream_contract(utils_source: str) -> list[str]:
    failures = []
    if "import java.io.IOException;" not in utils_source:
        failures.append("Utils.CopyStream must declare the IOException boundary")

    method_match = re.search(
        r"(?s)public\s+static\s+void\s+CopyStream\s*"
        r"\(\s*InputStream\s+is\s*,\s*OutputStream\s+os\s*\)\s*\{(.*)\n\s*\}",
        utils_source,
    )
    method_body = method_match.group(1) if method_match else ""
    if not method_body:
        failures.append("Utils.CopyStream method body must remain present")
        return failures

    if re.search(r"catch\s*\(\s*(?:Exception|Throwable)\s+\w+\s*\)", method_body):
        failures.append("Utils.CopyStream must not catch broad stream-copy failures")
    if "catch(IOException ex)" not in method_body:
        failures.append("Utils.CopyStream must catch IOException explicitly")
    if 'throw new RuntimeException("Unable to copy stream", ex);' not in method_body:
        failures.append(
            "Utils.CopyStream must rethrow copy failures with diagnostic context"
        )
    if re.search(r"catch\s*\([^)]*\)\s*\{\s*\}", method_body):
        failures.append("Utils.CopyStream must not swallow copy failures")
    return failures


def validate_workflow_credential_boundary(workflow: str) -> list[str]:
    failures = []
    checkout_action = "actions/checkout@df4cb1c069e1874edd31b4311f1884172cec0e10"
    checkout_blocks = re.findall(
        rf"(?m)^(?P<indent> *)- +uses: +{re.escape(checkout_action)}[^\n]*\n"
        rf"(?P=indent)  with:\n"
        rf"(?P=indent)    persist-credentials: +false *$",
        workflow,
    )
    checkout_actions = re.findall(r"(?m)^\s*-\s+uses:\s+actions/checkout@", workflow)
    if not (
        workflow.count("permissions:") == 1
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
    return failures


def validate_main_activity_authentication_contract(main_activity: str) -> list[str]:
    failures = []
    required = [
        "private static boolean twitterCallbackExchangeInFlight;",
        "private boolean twitterLoginInFlight;",
        "final Twitter callbackTwitter = twitter;",
        "final RequestToken callbackRequestToken = requestToken;",
        "if (twitterCallbackExchangeInFlight) {",
        "twitterCallbackExchangeInFlight = true;",
        "private void finishTwitterCallbackExchange()",
        "if (!e.commit()) {",
        'logTwitterLoginFailure("Credential persistence")',
        "private boolean isTrustedTwitterAuthenticationUri(Uri uri)",
        '"https".equals(uri.getScheme())',
        '"api.twitter.com".equals(uri.getHost())',
        "uri.getPort() == -1",
        '"/oauth/authenticate".equals(uri.getPath())',
        "if (twitterCallbackExchangeInFlight || twitterLoginInFlight) {",
        "twitterLoginInFlight = true;",
        "if (!isTrustedTwitterAuthenticationUri(authenticationUri))",
        "private void finishTwitterLoginAttempt()",
    ]
    for text in required:
        if text not in main_activity:
            failures.append(f"MainActivity must preserve authentication contract: {text}")

    trusted_launch = (
        "MainActivity.this.runOnUiThread(new Runnable() {\n"
        "                                @Override\n"
        "                                public void run() {\n"
        "                                    twitterLoginInFlight = false;\n"
        "                                    MainActivity.this.startActivity(new Intent(Intent.ACTION_VIEW, authenticationUri));\n"
        "                                }\n"
        "                            });"
    )
    if trusted_launch not in main_activity:
        failures.append("MainActivity must launch Twitter authorization on the UI thread")
    if (
        "Uri\n                                .parse(requestToken.getAuthenticationURL())"
        in main_activity
        or "e.commit(); // save changes" in main_activity
        or "e.printStackTrace()" in main_activity
        or "e.getMessage()" in main_activity
    ):
        failures.append("MainActivity must not use stale OAuth launch, persistence, or logging paths")
    return failures


def validate_rdio_runtime_contract(rdio_app: str) -> list[str]:
    failures = []
    required = [
        "private boolean rdioAuthorizationInFlight;",
        "private static final int RDIO_AUTHORIZATION_REQUEST = 1;",
        "STATE_RDIO_AUTHORIZATION_IN_FLIGHT",
        "protected void onSaveInstanceState(Bundle outState)",
        "startRdioAuthorization();",
        "rdio.cleanup();\n            rdio = null;",
        'Log.e(TAG, "Playback preparation failed");',
        "if (!hasRdioCredential(accessToken) || !hasRdioCredential(accessTokenSecret)",
        "if (!persistRdioCredentials(accessToken, accessTokenSecret))",
        "requestCode != RDIO_AUTHORIZATION_REQUEST",
        "clearRdioCredentials();",
        "rdio.setTokenAndSecret(accessToken, accessTokenSecret);",
        "rdio.prepareForPlayback();",
        "private void startRdioAuthorization()",
        "if (rdioAuthorizationInFlight) {",
        "private boolean hasRdioCredential(String value)",
        "private boolean persistRdioCredentials(String token, String tokenSecret)",
        "return editor.commit();",
        'Log.e(TAG, "Twitter search failed");\n                return null;',
        'Log.e(TAG, "Twitter result formatting failed");\n                    continue;',
        "runOnUiThread(new Runnable() {\n                @Override\n                public void run() {\n                    final ListView listView = (ListView) findViewById(R.id.list);",
    ]
    for text in required:
        if text not in rdio_app:
            failures.append(f"RdioApp must preserve runtime contract: {text}")

    forbidden = [
        'Log.e("Test", "Exception " + e)',
        "e.printStackTrace()",
        "Log.e(TAG, methodName + \" failed: \", e)",
        "OAuth1WebViewActivity.EXTRA_ERROR_DESCRIPTION",
    ]
    for text in forbidden:
        if text in rdio_app:
            failures.append(f"RdioApp must not keep unsafe runtime path: {text}")
    return failures


def validate_tweet_adapter_contract(tweet_adapter: str) -> list[str]:
    failures = []
    if "private static final String TAG = \"TweetAdapter\";" not in tweet_adapter:
        failures.append("TweetAdapter must define a stable sanitized log tag")
    if 'Log.e(TAG, "Twitter result rendering failed");' not in tweet_adapter:
        failures.append("TweetAdapter must use sanitized rendering failure logging")
    if "e.printStackTrace()" in tweet_adapter or "e.getMessage()" in tweet_adapter:
        failures.append("TweetAdapter must not log provider exception details")
    return failures


def run_static_checks() -> list[str]:
    failures = []
    failures.extend(validate_reviewed_contract_consistency())
    failures.extend(validate_test_inventory(ROOT))
    failures.extend(validate_import_shadow_inventory(ROOT))
    failures.extend(validate_no_python_artifacts(ROOT))
    failures.extend(validate_committed_protected_blobs())

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
    failures.extend(validate_makefile_contract(makefile))

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
    failures.extend(validate_main_activity_authentication_contract(main_activity))
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
    tweet_adapter = read_text("app/src/main/java/com/twitterdev/rdio/app/TweetAdapter.java")
    failures.extend(validate_tweet_adapter_contract(tweet_adapter))
    image_download = read_text("app/src/main/java/com/twitterdev/rdio/app/ImageDownload.java")
    if "isHttpsImageUrl" not in image_download or "URLUtil.isHttpsUrl" not in image_download or "URLUtil.isHttpUrl" in image_download or "params.length == 0" not in image_download:
        failures.append("ImageDownload must guard missing URLs and accept only HTTPS images")
    utils_source = read_text("app/src/main/java/com/twitterdev/rdio/app/Utils.java")
    failures.extend(validate_utils_copy_stream_contract(utils_source))
    rdio_app_path = "app/src/main/java/com/twitterdev/rdio/app/RdioApp.java"
    rdio_app = read_text(rdio_app_path)
    failures.extend(validate_reviewed_file_bytes(rdio_app_path, read_bytes(rdio_app_path)))
    failures.extend(validate_rdio_runtime_contract(rdio_app))
    if "getBiggerProfileImageURLHttps()" not in rdio_app or "getBiggerProfileImageURL()" in rdio_app:
        failures.append("RdioApp must select Twitter profile images from the HTTPS URL field")
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
        "docs/plans/issue-1-copy-stream-errors.md",
    ]:
        if not (ROOT / relative_path).is_file():
            continue
        plan = read_text(relative_path)
        if "status: completed" not in plan:
            failures.append(f"{relative_path} must record completed status")
        if "scripts/check-android-baseline.py" not in plan:
            failures.append(f"{relative_path} must reference the active baseline checker")

    album_art_plan_bytes = read_bytes(EVIDENCE_PLAN_PATH)
    failures.extend(validate_album_art_evidence_contract(album_art_plan_bytes))
    album_art_plan = album_art_plan_bytes.decode("utf-8")
    album_art_status = re.findall(r"(?mi)^status:\s*(.+?)\s*$", album_art_plan)
    album_art_work = markdown_section(album_art_plan, "Work Completed")
    album_art_verification = markdown_section(album_art_plan, "Verification Completed")
    if album_art_status != ["completed"] or not album_art_work:
        failures.append("album art connection guard plan must record one completed status and completed work")
    if not album_art_verification or re.search(
        r"(?i)\b(?:pending|todo|tbd|not run)\b", album_art_verification
    ):
        failures.append("album art connection guard plan must record completed verification")
    workflow_path = ".github/workflows/check.yml"
    failures.extend(
        validate_reviewed_file_bytes(workflow_path, read_bytes(workflow_path))
    )
    workflow = read_text(workflow_path)
    failures.extend(validate_workflow_credential_boundary(workflow))

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
        if "stream copy failure guard" not in text.lower():
            failures.append(f"{relative_path} must document the stream copy failure guard")
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
    if "stream copy failure guard" not in changes.lower():
        failures.append("CHANGES must record stream copy failure guardrails")
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

    return failures


def report_failures(failures: list[str]) -> int:
    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1
    print("musichackday-android baseline checks passed.")
    return 0


def run_gate() -> int:
    pre_failures = run_static_checks()
    if pre_failures:
        return report_failures(pre_failures)
    before_snapshot = repository_snapshot(ROOT)
    test_returncode, test_failures = run_reviewed_tests()
    post_failures = run_static_checks()
    post_failures.extend(test_failures)
    post_failures.extend(validate_repository_unchanged(before_snapshot))
    if test_returncode != 0:
        post_failures.append("reviewed unit-test invocation failed")
    return report_failures(post_failures)


def main() -> int:
    global ROOT
    arguments = sys.argv[1:]
    if len(arguments) >= 2 and arguments[:1] == ["--root"]:
        ROOT = Path(arguments[1]).resolve()
        arguments = arguments[2:]
    if len(arguments) >= 2 and arguments[:1] == ["--expect-python"]:
        allowed_versions = {
            tuple(int(part) for part in version.split("."))
            for version in arguments[1].split(",")
        }
        if sys.version_info[:2] not in allowed_versions:
            print(
                f"unexpected Python {sys.version_info.major}.{sys.version_info.minor}; "
                f"expected {arguments[1]}",
                file=sys.stderr,
            )
            return 1
        arguments = arguments[2:]
    if arguments == ["--static"]:
        return report_failures(run_static_checks())
    if arguments == ["--gate"]:
        return run_gate()
    print(
        "usage: check-android-baseline.py [--root PATH] "
        "[--expect-python VERSIONS] --static|--gate",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
