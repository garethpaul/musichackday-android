import importlib.util
import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
CHECKER_PATH = ROOT / "scripts/check-android-baseline.py"
MAIN_ACTIVITY_PATH = (
    ROOT / "app/src/main/java/com/twitterdev/rdio/app/MainActivity.java"
)
RDIO_APP_PATH = (
    ROOT
    / "app/src/main/java/com/twitterdev/rdio/app/RdioApp.java"
)
TWEET_ADAPTER_PATH = (
    ROOT / "app/src/main/java/com/twitterdev/rdio/app/TweetAdapter.java"
)
UTILS_PATH = ROOT / "app/src/main/java/com/twitterdev/rdio/app/Utils.java"
ALBUM_ART_PLAN_PATH = (
    ROOT / "docs/plans/2026-06-12-album-art-connection-guard.md"
)
MAKEFILE_PATH = ROOT / "Makefile"
WORKFLOW_PATH = ROOT / ".github/workflows/check.yml"
ALBUM_ART_CONNECTION_START = (
    "        // Fetch album art in the background and then update the UI on the main thread"
)
ALBUM_ART_CONNECTION_END = "        artworkTask.execute(track);"


def load_checker():
    spec = importlib.util.spec_from_file_location("android_baseline", CHECKER_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def initialize_scratch_repository(root):
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    subprocess.run(
        ["git", "config", "user.name", "Baseline Test"], cwd=root, check=True
    )
    subprocess.run(
        ["git", "config", "user.email", "baseline@example.invalid"],
        cwd=root,
        check=True,
    )
    subprocess.run(["git", "add", "-A"], cwd=root, check=True)
    subprocess.run(["git", "commit", "-qm", "scratch baseline"], cwd=root, check=True)


class UtilsCopyStreamContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.checker = load_checker()
        cls.source = UTILS_PATH.read_text(encoding="utf-8")

    def validate(self, source):
        validator = getattr(
            self.checker,
            "validate_utils_copy_stream_contract",
            None,
        )
        self.assertIsNotNone(validator, "Utils.CopyStream contract validator is missing")
        return validator(source)

    def assert_rejected(self, source):
        self.assertTrue(
            self.validate(source),
            "mutated Utils.CopyStream contract was accepted",
        )

    def test_accepts_canonical_copy_stream_contract(self):
        self.assertEqual([], self.validate(self.source))

    def test_rejects_swallowed_copy_stream_exception(self):
        self.assert_rejected(
            self.source.replace(
                "catch(IOException ex)\n"
                "        {\n"
                "            throw new RuntimeException(\"Unable to copy stream\", ex);\n"
                "        }",
                "catch(Exception ex){}",
                1,
            )
        )

    def test_rejects_missing_copy_stream_diagnostic_rethrow(self):
        self.assert_rejected(
            self.source.replace(
                "throw new RuntimeException(\"Unable to copy stream\", ex);",
                "return;",
                1,
            )
        )

    def test_rejects_missing_io_exception_boundary(self):
        self.assert_rejected(
            self.source.replace("import java.io.IOException;\n", "", 1).replace(
                "catch(IOException ex)",
                "catch(Exception ex)",
                1,
            )
        )


class MainActivityAuthenticationContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.checker = load_checker()
        cls.source = MAIN_ACTIVITY_PATH.read_text(encoding="utf-8")

    def validate(self, source):
        validator = getattr(
            self.checker,
            "validate_main_activity_authentication_contract",
            None,
        )
        self.assertIsNotNone(
            validator,
            "MainActivity authentication contract validator is missing",
        )
        return validator(source)

    def assert_rejected(self, source):
        self.assertTrue(
            self.validate(source),
            "mutated MainActivity authentication contract was accepted",
        )

    def test_accepts_canonical_authentication_contract(self):
        self.assertEqual([], self.validate(self.source))

    def test_rejects_untrusted_twitter_authorization_uri_launch(self):
        self.assert_rejected(
            self.source.replace(
                "private boolean isTrustedTwitterAuthenticationUri(Uri uri)",
                "private boolean isTrustedTwitterAuthenticationUriDisabled(Uri uri)",
                1,
            )
        )

    def test_rejects_unchecked_twitter_credential_persistence(self):
        self.assert_rejected(
            self.source.replace(
                "if (!e.commit()) {",
                "e.commit();\n                                if (false) {",
                1,
            )
        )

    def test_rejects_missing_twitter_callback_inflight_guard(self):
        self.assert_rejected(
            self.source.replace(
                "if (twitterCallbackExchangeInFlight) {\n"
                "                    return;\n"
                "                }\n"
                "                twitterCallbackExchangeInFlight = true;",
                "twitterCallbackExchangeInFlight = false;",
                1,
            )
        )

    def test_rejects_background_thread_twitter_navigation(self):
        self.assert_rejected(
            self.source.replace(
                "MainActivity.this.runOnUiThread(new Runnable() {\n"
                "                                @Override\n"
                "                                public void run() {\n"
                "                                    twitterLoginInFlight = false;\n"
                "                                    MainActivity.this.startActivity(new Intent(Intent.ACTION_VIEW, authenticationUri));\n"
                "                                }\n"
                "                            });",
                "twitterLoginInFlight = false;\n"
                "                            MainActivity.this.startActivity(new Intent(Intent.ACTION_VIEW, authenticationUri));",
                1,
            )
        )


class RdioRuntimeContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.checker = load_checker()
        cls.source = RDIO_APP_PATH.read_text(encoding="utf-8")

    def validate(self, source):
        validator = getattr(self.checker, "validate_rdio_runtime_contract", None)
        self.assertIsNotNone(validator, "Rdio runtime contract validator is missing")
        return validator(source)

    def assert_rejected(self, source):
        self.assertTrue(
            self.validate(source),
            "mutated Rdio runtime contract was accepted",
        )

    def test_accepts_canonical_rdio_runtime_contract(self):
        self.assertEqual([], self.validate(self.source))

    def test_rejects_unchecked_rdio_credential_persistence(self):
        self.assert_rejected(
            self.source.replace(
                "return editor.commit();",
                "editor.commit();\n        return true;",
                1,
            )
        )

    def test_rejects_playback_exception_detail_logging(self):
        self.assert_rejected(
            self.source.replace(
                'Log.e(TAG, "Playback preparation failed");',
                'Log.e("Test", "Exception " + e);',
                1,
            )
        )

    def test_rejects_twitter_search_failure_continuation(self):
        self.assert_rejected(
            self.source.replace(
                'Log.e(TAG, "Twitter search failed");\n'
                "                return null;",
                "e.printStackTrace();",
                1,
            )
        )

    def test_rejects_background_thread_search_view_lookup(self):
        self.assert_rejected(
            self.source.replace(
                "runOnUiThread(new Runnable() {\n"
                "                @Override\n"
                "                public void run() {\n"
                "                    final ListView listView = (ListView) findViewById(R.id.list);",
                "final ListView listView = (ListView) findViewById(R.id.list);\n"
                "            runOnUiThread(new Runnable() {\n"
                "                @Override\n"
                "                public void run() {",
                1,
            )
        )


class TweetAdapterRedactionContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.checker = load_checker()
        cls.source = TWEET_ADAPTER_PATH.read_text(encoding="utf-8")

    def validate(self, source):
        validator = getattr(self.checker, "validate_tweet_adapter_contract", None)
        self.assertIsNotNone(validator, "TweetAdapter contract validator is missing")
        return validator(source)

    def test_accepts_canonical_tweet_adapter_contract(self):
        self.assertEqual([], self.validate(self.source))

    def test_rejects_tweet_rendering_stack_trace_logging(self):
        self.assertTrue(
            self.validate(
                self.source.replace(
                    'Log.e(TAG, "Twitter result rendering failed");',
                    "e.printStackTrace();",
                    1,
                )
            ),
            "mutated TweetAdapter contract was accepted",
        )


class WorkflowCredentialBoundaryContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.checker = load_checker()
        cls.source = WORKFLOW_PATH.read_text(encoding="utf-8")

    def validate(self, source):
        validator = getattr(self.checker, "validate_workflow_credential_boundary", None)
        self.assertIsNotNone(
            validator,
            "workflow credential-boundary validator is missing",
        )
        return validator(source)

    def test_accepts_canonical_workflow_credential_boundary(self):
        self.assertEqual([], self.validate(self.source))

    def test_rejects_persisted_checkout_credentials(self):
        self.assertTrue(
            self.validate(
                self.source.replace(
                    "        with:\n"
                    "          persist-credentials: false\n",
                    "",
                    1,
                )
            ),
            "mutated workflow credential boundary was accepted",
        )


class AlbumArtConnectionContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.checker = load_checker()
        cls.source = RDIO_APP_PATH.read_text(encoding="utf-8")
        start = cls.source.index(ALBUM_ART_CONNECTION_START)
        end = cls.source.index(ALBUM_ART_CONNECTION_END, start) + len(
            ALBUM_ART_CONNECTION_END
        )
        cls.canonical = cls.source[start:end]

    def assert_rejected(self, source):
        self.assertTrue(
            self.checker.validate_album_art_connection_contract(source),
            "mutated album-art connection contract was accepted",
        )

    def test_accepts_canonical_runtime_block(self):
        self.assertEqual(
            [],
            self.checker.validate_album_art_connection_contract(self.source),
        )

    def test_rejects_disabled_https_guard(self):
        self.assert_rejected(
            self.source.replace(
                "if (!URLUtil.isHttpsUrl(artworkUrl)) {",
                "if (false && !URLUtil.isHttpsUrl(artworkUrl)) {",
                1,
            )
        )

    def test_rejects_unreachable_timeouts(self):
        source = self.source.replace(
            "connection.setConnectTimeout(10000);",
            "if (false) connection.setConnectTimeout(10000);",
            1,
        ).replace(
            "connection.setReadTimeout(10000);",
            "if (false) connection.setReadTimeout(10000);",
            1,
        )
        self.assert_rejected(source)

    def test_requires_redirects_disabled_before_connect(self):
        redirect_guard = "connection.setInstanceFollowRedirects(false);"
        self.assertIn(redirect_guard, self.canonical)
        self.assertLess(
            self.canonical.index(redirect_guard),
            self.canonical.index("connection.connect();"),
        )

    def test_rejects_unreachable_close_and_disconnect(self):
        source = self.source.replace(
            "if (bufferedInputStream != null) {",
            "if (false && bufferedInputStream != null) {",
            1,
        ).replace(
            "if (connection != null) {",
            "if (false && connection != null) {",
            1,
        )
        self.assert_rejected(source)

    def test_rejects_exception_detail_logging(self):
        self.assert_rejected(
            self.source.replace(
                'Log.e(TAG, "Album art download failed");',
                'Log.e(TAG, "Album art download failed: " + e);',
                1,
            )
        )

    def test_rejects_url_logging(self):
        self.assert_rejected(
            self.source.replace(
                "String artworkUrl = track.albumArt.replace(\"square-200\", \"square-600\");",
                "String artworkUrl = track.albumArt.replace(\"square-200\", \"square-600\");\n"
                '                    Log.i(TAG, "Downloading album art: " + artworkUrl);',
                1,
            )
        )

    def test_rejects_comment_decoy_for_mutated_runtime(self):
        canonical = self.canonical
        source = self.source.replace(
            "if (!URLUtil.isHttpsUrl(artworkUrl)) {",
            "if (false && !URLUtil.isHttpsUrl(artworkUrl)) {",
            1,
        )
        source = source.replace(
            "public class RdioApp extends Activity implements RdioListener {",
            "/*\n" + canonical + "\n*/\n"
            "public class RdioApp extends Activity implements RdioListener {",
            1,
        )
        self.assert_rejected(source)

    def test_rejects_dead_code_decoy_for_mutated_runtime(self):
        canonical = self.canonical
        source = self.source.replace(
            "if (!URLUtil.isHttpsUrl(artworkUrl)) {",
            "if (false && !URLUtil.isHttpsUrl(artworkUrl)) {",
            1,
        )
        source = source.replace(
            "private void playPause() {",
            "private void albumArtDecoy() {\n"
            "        if (false) {\n"
            + canonical
            + "\n        }\n"
            "    }\n\n"
            "    private void playPause() {",
            1,
        )
        self.assert_rejected(source)

    def test_rejects_alternate_method_decoy_for_mutated_runtime(self):
        canonical = self.canonical
        source = self.source.replace(
            "if (!URLUtil.isHttpsUrl(artworkUrl)) {",
            "if (false && !URLUtil.isHttpsUrl(artworkUrl)) {",
            1,
        )
        source = source.replace(
            "private void playPause() {",
            "private void albumArtDecoy() {\n"
            + canonical
            + "\n    }\n\n"
            "    private void playPause() {",
            1,
        )
        self.assert_rejected(source)

    def test_rejects_duplicate_connection_path(self):
        self.assert_rejected(
            self.source.replace(
                "artworkTask.execute(track);",
                "artworkTask.execute(track);\n"
                "        new URL(track.albumArt).openConnection();",
                1,
            )
        )

    def test_rejects_reachable_open_stream_path(self):
        source = self.source.replace(
            "private void playPause() {",
            "private void playPause() {\n"
            "        try {\n"
            '            new URL("https://example.invalid/second.jpg").openStream();\n'
            "        } catch (IOException ignored) {\n"
            "        }",
            1,
        )
        self.assert_rejected(source)

    def test_rejects_reachable_get_content_path(self):
        source = self.source.replace(
            "private void playPause() {",
            "private void playPause() {\n"
            "        try {\n"
            '            new URL("https://example.invalid/second.jpg").getContent();\n'
            "        } catch (IOException ignored) {\n"
            "        }",
            1,
        )
        self.assert_rejected(source)

    def test_rejects_alternate_network_api_in_comment_or_string(self):
        source = self.source.replace(
            "private void playPause() {",
            "private void playPause() {\n"
            "        // new URL(track.albumArt).openStream();\n"
            '        String example = "new URL(track.albumArt).getContent()";',
            1,
        )
        self.assert_rejected(source)

    def test_rejects_album_art_url_logging_before_canonical_block(self):
        source = self.source.replace(
            ALBUM_ART_CONNECTION_START,
            '        Log.e(TAG, "Album art URL: " + track.albumArt);\n'
            + ALBUM_ART_CONNECTION_START,
            1,
        )
        self.assert_rejected(source)

    def test_rejects_album_art_url_logging_after_canonical_block(self):
        source = self.source.replace(
            "artworkTask.execute(track);",
            "artworkTask.execute(track);\n"
            '        Log.e(TAG, "Artwork URL: " + track.albumArt);',
            1,
        )
        self.assert_rejected(source)

    def test_rejects_album_art_exception_logging_outside_canonical_block(self):
        source = self.source.replace(
            "private void playPause() {",
            "private void playPause() {\n"
            "        try {\n"
            "            throw new IOException();\n"
            "        } catch (IOException e) {\n"
            '            Log.e(TAG, "Album art retry failed", e);\n'
            "        }",
            1,
        )
        self.assert_rejected(source)

    def test_rejects_album_art_url_alias_logging_outside_canonical_block(self):
        source = self.source.replace(
            "private void playPause() {",
            "private void playPause() {\n"
            "        String leakedArtwork = track.albumArt;\n"
            "        Log.e(TAG, leakedArtwork);",
            1,
        )
        self.assert_rejected(source)

    def test_rejects_album_art_logging_decoy_in_comment_or_string(self):
        source = self.source.replace(
            "private void playPause() {",
            "private void playPause() {\n"
            '        // Log.e(TAG, "Album art URL: " + track.albumArt);\n'
            '        String example = "Log.e(TAG, Album art URL)";',
            1,
        )
        self.assert_rejected(source)

    def test_rejects_duplicate_canonical_block(self):
        canonical = self.canonical
        self.assert_rejected(self.source + "\n" + canonical + "\n")


class DynamicImageViewContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.checker = load_checker()
        cls.source = (
            ROOT
            / "app/src/main/java/com/twitterdev/rdio/app/DynamicImageView.java"
        ).read_text(encoding="utf-8")

    def assert_rejected(self, source):
        self.assertTrue(
            self.checker.validate_dynamic_image_view_contract(source),
            "mutated DynamicImageView measurement contract was accepted",
        )

    def test_accepts_positive_intrinsic_dimension_guard(self):
        self.assertEqual(
            [],
            self.checker.validate_dynamic_image_view_contract(self.source),
        )

    def test_rejects_missing_positive_intrinsic_width_guard(self):
        self.assert_rejected(
            self.source.replace("d.getIntrinsicWidth() > 0", "d.getIntrinsicWidth() >= 0", 1)
        )

    def test_rejects_missing_positive_intrinsic_height_guard(self):
        self.assert_rejected(
            self.source.replace("d.getIntrinsicHeight() > 0", "d.getIntrinsicHeight() >= 0", 1)
        )


class ReviewedByteContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.checker = load_checker()
        cls.rdio_bytes = RDIO_APP_PATH.read_bytes()
        cls.workflow_bytes = WORKFLOW_PATH.read_bytes()

    def assert_file_rejected(self, relative_path, content):
        self.assertTrue(
            self.checker.validate_reviewed_file_bytes(relative_path, content),
            f"mutated reviewed file was accepted: {relative_path}",
        )

    def run_mutated_repository(self, mutate):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory) / "repo"
            shutil.copytree(
                ROOT,
                root,
                ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc"),
            )
            initialize_scratch_repository(root)
            mutate(root)
            return subprocess.run(
                ["make", "check"],
                cwd=root,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                check=False,
            )

    def run_committed_attack(self, mutate):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory) / "repo"
            shutil.copytree(
                ROOT,
                root,
                ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc"),
            )
            initialize_scratch_repository(root)
            mutate(root)
            subprocess.run(["git", "add", "-A"], cwd=root, check=True)
            subprocess.run(
                ["git", "commit", "-qm", "malicious rewrite"], cwd=root, check=True
            )
            result = subprocess.run(
                ["make", "check"],
                cwd=root,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                check=False,
            )
            paths = {
                path.relative_to(root).as_posix()
                for path in root.rglob("*")
                if ".git" not in path.relative_to(root).parts
            }
            return result, paths

    def replace_hash_literal(self, path, old_hash, new_hash):
        text = path.read_text(encoding="utf-8")
        self.assertIn(old_hash, text)
        path.write_text(text.replace(old_hash, new_hash, 1), encoding="utf-8")

    def test_reviewed_hash_constants_match_current_bytes(self):
        for relative_path, path in [
            ("app/src/main/java/com/twitterdev/rdio/app/RdioApp.java", RDIO_APP_PATH),
            (".github/workflows/check.yml", WORKFLOW_PATH),
        ]:
            with self.subTest(relative_path=relative_path):
                self.assertEqual(
                    hashlib.sha256(path.read_bytes()).hexdigest(),
                    self.checker.REVIEWED_FILE_SHA256[relative_path],
                )

    def test_accepts_exact_reviewed_runtime_and_workflow_bytes(self):
        self.assertEqual(
            [],
            self.checker.validate_reviewed_file_bytes(
                "app/src/main/java/com/twitterdev/rdio/app/RdioApp.java",
                self.rdio_bytes,
            ),
        )
        self.assertEqual(
            [],
            self.checker.validate_reviewed_file_bytes(
                ".github/workflows/check.yml",
                self.workflow_bytes,
            ),
        )

    def test_rejects_delegated_album_art_helper_call(self):
        mutated = self.rdio_bytes.replace(
            ALBUM_ART_CONNECTION_START.encode(),
            b"        HiddenAlbumArt.fetch(track);\n"
            + ALBUM_ART_CONNECTION_START.encode(),
            1,
        )
        self.assert_file_rejected(
            "app/src/main/java/com/twitterdev/rdio/app/RdioApp.java", mutated
        )

    def test_full_gate_rejects_delegated_helper_reproducer(self):
        def mutate(root):
            rdio_path = root / RDIO_APP_PATH.relative_to(ROOT)
            rdio_path.write_bytes(
                rdio_path.read_bytes().replace(
                    ALBUM_ART_CONNECTION_START.encode(),
                    b"        HiddenAlbumArt.fetch(track);\n"
                    + ALBUM_ART_CONNECTION_START.encode(),
                    1,
                )
            )
            helper_path = rdio_path.with_name("HiddenAlbumArt.java")
            helper_path.write_text(
                "package com.twitterdev.rdio.app;\n"
                "import java.net.URL;\n"
                "final class HiddenAlbumArt {\n"
                "    static void fetch(RdioApp.Track track) throws Exception {\n"
                "        android.util.Log.e(\"RdioAPIExample\", track.albumArt);\n"
                "        new URL(track.albumArt).openStream();\n"
                "    }\n"
                "}\n",
                encoding="utf-8",
            )

        result = self.run_mutated_repository(mutate)
        self.assertNotEqual(0, result.returncode, result.stdout)
        self.assertIn("must match reviewed SHA-256", result.stdout)

    def test_rejects_reflective_album_art_path(self):
        probe = (
            '        Object hiddenArtwork = Track.class.getField("album" + "Art").get(track);\n'
            '        Object hiddenUrl = new URL(String.valueOf(hiddenArtwork));\n'
            '        Object hiddenConnection = URL.class.getMethod("open" + "Connection").invoke(hiddenUrl);\n'
            '        hiddenConnection.getClass().getMethod("connect").invoke(hiddenConnection);\n'
            '        android.util.Log.e(TAG, String.valueOf(hiddenArtwork));\n'
        ).encode()
        mutated = self.rdio_bytes.replace(
            ALBUM_ART_CONNECTION_START.encode(),
            probe + ALBUM_ART_CONNECTION_START.encode(),
            1,
        )
        self.assert_file_rejected(
            "app/src/main/java/com/twitterdev/rdio/app/RdioApp.java", mutated
        )

    def test_full_gate_rejects_reflection_reproducer(self):
        def mutate(root):
            rdio_path = root / RDIO_APP_PATH.relative_to(ROOT)
            probe = (
                '        Object hiddenArtwork = Track.class.getField("album" + "Art").get(track);\n'
                '        Object hiddenUrl = new URL(String.valueOf(hiddenArtwork));\n'
                '        Object hiddenConnection = URL.class.getMethod("open" + "Connection").invoke(hiddenUrl);\n'
                '        hiddenConnection.getClass().getMethod("connect").invoke(hiddenConnection);\n'
                '        android.util.Log.e(TAG, String.valueOf(hiddenArtwork));\n'
            ).encode()
            rdio_path.write_bytes(
                rdio_path.read_bytes().replace(
                    ALBUM_ART_CONNECTION_START.encode(),
                    probe + ALBUM_ART_CONNECTION_START.encode(),
                    1,
                )
            )

        result = self.run_mutated_repository(mutate)
        self.assertNotEqual(0, result.returncode, result.stdout)
        self.assertIn("must match reviewed SHA-256", result.stdout)

    def test_rejects_runtime_line_ending_and_single_byte_changes(self):
        for mutated in [
            self.rdio_bytes.replace(b"\n", b"\r\n"),
            self.rdio_bytes.replace(b"Album art download failed", b"Album art failed", 1),
            self.rdio_bytes + b"\n",
        ]:
            with self.subTest(length=len(mutated)):
                self.assert_file_rejected(
                    "app/src/main/java/com/twitterdev/rdio/app/RdioApp.java", mutated
                )

    def test_rejects_workflow_argument_bypasses(self):
        trusted_command = (
            b'"$python_bin" -I -B "$verifier_dir/verifier.py" --root '
            b'"$GITHUB_WORKSPACE" --expect-python 3.12 --gate'
        )
        for command in [
            trusted_command.replace(b"--gate", b"--static"),
            trusted_command + b" --skip-tests",
            trusted_command.replace(b"-I -B", b"-O"),
            b"bash -c 'python3 -I -B verifier.py --gate'",
            b'sh -c "python3 -I -B verifier.py --gate"',
        ]:
            with self.subTest(command=command):
                mutated = self.workflow_bytes.replace(trusted_command, command, 1)
                self.assert_file_rejected(".github/workflows/check.yml", mutated)

    def test_full_gate_rejects_workflow_python_override_reproducer(self):
        def mutate(root):
            workflow_path = root / WORKFLOW_PATH.relative_to(ROOT)
            workflow_path.write_bytes(
                workflow_path.read_bytes().replace(
                    b"--gate", b"--static", 1
                )
            )

        result = self.run_mutated_repository(mutate)
        self.assertNotEqual(0, result.returncode, result.stdout)
        self.assertIn("must match reviewed SHA-256", result.stdout)

    def test_full_gate_rejects_runtime_plus_checker_hash_only(self):
        def mutate(root):
            runtime_path = root / RDIO_APP_PATH.relative_to(ROOT)
            checker_path = root / CHECKER_PATH.relative_to(ROOT)
            mutated = runtime_path.read_bytes().replace(
                ALBUM_ART_CONNECTION_START.encode(),
                b"        new java.net.URL(track.albumArt).openStream();\n"
                + ALBUM_ART_CONNECTION_START.encode(),
                1,
            )
            runtime_path.write_bytes(mutated)
            self.replace_hash_literal(
                checker_path,
                "a71008d19f4811c217a420ff8828f2ebf7f45969055fbd515584c896d67239ec",
                hashlib.sha256(mutated).hexdigest(),
            )

        result = self.run_mutated_repository(mutate)
        self.assertNotEqual(0, result.returncode, result.stdout)
        self.assertIn("reviewed byte contract", result.stdout.lower())

    def test_full_gate_rejects_runtime_plus_test_hash_only(self):
        def mutate(root):
            runtime_path = root / RDIO_APP_PATH.relative_to(ROOT)
            test_path = root / "tests/test_reviewed_hashes.py"
            mutated = runtime_path.read_bytes().replace(
                ALBUM_ART_CONNECTION_START.encode(),
                b"        new java.net.URL(track.albumArt).openStream();\n"
                + ALBUM_ART_CONNECTION_START.encode(),
                1,
            )
            runtime_path.write_bytes(mutated)
            self.replace_hash_literal(
                test_path,
                "a71008d19f4811c217a420ff8828f2ebf7f45969055fbd515584c896d67239ec",
                hashlib.sha256(mutated).hexdigest(),
            )

        result = self.run_mutated_repository(mutate)
        self.assertNotEqual(0, result.returncode, result.stdout)

    def test_full_gate_rejects_runtime_checker_and_test_without_contract_update(self):
        def mutate(root):
            runtime_path = root / RDIO_APP_PATH.relative_to(ROOT)
            checker_path = root / CHECKER_PATH.relative_to(ROOT)
            test_path = root / "tests/test_reviewed_hashes.py"
            mutated = runtime_path.read_bytes().replace(
                ALBUM_ART_CONNECTION_START.encode(),
                b"        new java.net.URL(track.albumArt).openStream();\n"
                + ALBUM_ART_CONNECTION_START.encode(),
                1,
            )
            new_hash = hashlib.sha256(mutated).hexdigest()
            runtime_path.write_bytes(mutated)
            for path in [checker_path, test_path]:
                self.replace_hash_literal(
                    path,
                    "a71008d19f4811c217a420ff8828f2ebf7f45969055fbd515584c896d67239ec",
                    new_hash,
                )

        result = self.run_mutated_repository(mutate)
        self.assertNotEqual(0, result.returncode, result.stdout)
        self.assertIn("reviewed byte contract", result.stdout.lower())

    def test_full_gate_rejects_workflow_checker_and_test_without_contract_update(self):
        def mutate(root):
            workflow_path = root / WORKFLOW_PATH.relative_to(ROOT)
            checker_path = root / CHECKER_PATH.relative_to(ROOT)
            test_path = root / "tests/test_reviewed_hashes.py"
            mutated = workflow_path.read_bytes().replace(
                b"--gate", b"--static", 1
            )
            new_hash = hashlib.sha256(mutated).hexdigest()
            workflow_path.write_bytes(mutated)
            for path in [checker_path, test_path]:
                self.replace_hash_literal(
                    path,
                    "3ac196785a75b7a744a1690a396feac24cf1b1fffd189dc2474ff01e6d01b57f",
                    new_hash,
                )

        result = self.run_mutated_repository(mutate)
        self.assertNotEqual(0, result.returncode, result.stdout)
        self.assertIn("reviewed byte contract", result.stdout.lower())

    def test_rejects_workflow_environment_bypasses(self):
        for environment in [
            b"      env:\n        PYTHON: true\n",
            b"      env:\n        MAKEFLAGS: -n\n",
            b"    env:\n      PYTHON: ':'\n",
        ]:
            with self.subTest(environment=environment):
                mutated = self.workflow_bytes.replace(b"    steps:\n", environment + b"    steps:\n", 1)
                self.assert_file_rejected(".github/workflows/check.yml", mutated)

    def test_rejects_workflow_line_ending_and_single_byte_changes(self):
        for mutated in [
            self.workflow_bytes.replace(b"\n", b"\r\n"),
            self.workflow_bytes.replace(b"ubuntu-24.04", b"ubuntu-latest", 1),
            self.workflow_bytes + b"\n",
        ]:
            with self.subTest(length=len(mutated)):
                self.assert_file_rejected(".github/workflows/check.yml", mutated)

    def test_gate_rejects_hashlib_shadow_import_time_restore_attack(self):
        marker_name = "malicious-hashlib-imported"

        def mutate(root):
            runtime_path = root / RDIO_APP_PATH.relative_to(ROOT)
            runtime_path.write_bytes(
                runtime_path.read_bytes().replace(
                    b"if (!URLUtil.isHttpsUrl(artworkUrl)) {",
                    b"if (false) {",
                    1,
                )
            )
            reviewed_runtime = subprocess.check_output(
                ["git", "show", "HEAD:app/src/main/java/com/twitterdev/rdio/app/RdioApp.java"],
                cwd=root,
            )
            (root / "scripts/reviewed-rdio.bin").write_bytes(reviewed_runtime)
            (root / "scripts/hashlib.py").write_text(
                "import atexit\n"
                "import os\n"
                "from pathlib import Path\n"
                "from _hashlib import openssl_sha256 as sha256\n\n"
                "ROOT = Path(__file__).resolve().parents[1]\n"
                "TARGET = ROOT / 'app/src/main/java/com/twitterdev/rdio/app/RdioApp.java'\n"
                "unsafe = TARGET.read_bytes()\n"
                f"(ROOT / '{marker_name}').write_text('imported', encoding='utf-8')\n"
                "os.environ['MHD_NESTED_GATE'] = '1'\n"
                "TARGET.write_bytes((ROOT / 'scripts/reviewed-rdio.bin').read_bytes())\n"
                "atexit.register(lambda: TARGET.write_bytes(unsafe))\n",
                encoding="utf-8",
            )

        result, paths = self.run_committed_attack(mutate)
        self.assertNotEqual(0, result.returncode, result.stdout)
        self.assertIn("import-shadow", result.stdout)
        self.assertIn("committed app/src/main", result.stdout)
        self.assertNotIn(marker_name, paths)

    def test_gate_rejects_reviewed_test_rewrite_before_restore_after_test_runs(self):
        marker_name = "restore-after-test-executed"

        def mutate(root):
            test_path = root / "tests/test_android_baseline.py"
            test_path.write_text(
                "from pathlib import Path\n"
                "import unittest\n\n"
                "ROOT = Path(__file__).resolve().parents[1]\n"
                "class RestoreAfterTest(unittest.TestCase):\n"
                "    def test_mutates_and_restores(self):\n"
                "        target = ROOT / 'README.md'\n"
                "        original = target.read_bytes()\n"
                "        target.write_bytes(original + b'unsafe')\n"
                "        target.write_bytes(original)\n"
                f"        (ROOT / '{marker_name}').write_text('executed', encoding='utf-8')\n",
                encoding="utf-8",
            )

        result, paths = self.run_committed_attack(mutate)
        self.assertNotEqual(0, result.returncode, result.stdout)
        self.assertIn("tests/test_android_baseline.py must match reviewed SHA-256", result.stdout)
        self.assertNotIn(marker_name, paths)


class AlbumArtEvidenceContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.checker = load_checker()
        cls.plan = ALBUM_ART_PLAN_PATH.read_bytes()

    def test_accepts_exact_truthful_predecessor_evidence_stanza(self):
        self.assertEqual(
            [],
            self.checker.validate_album_art_evidence_contract(self.plan),
        )
        self.assertEqual(
            self.checker.ALBUM_ART_HOSTED_EVIDENCE,
            self.checker.markdown_subsection(
                self.plan.decode("utf-8"), "Canonical Evidence"
            ),
        )
        self.assertIn(
            "This verified predecessor/implementation head is not the final evidence-only head.",
            self.checker.ALBUM_ART_HOSTED_EVIDENCE,
        )

    def test_rejects_false_final_head_claims_in_evidence_stanza(self):
        truthful = (
            "This verified predecessor/implementation head is not the final "
            "evidence-only head."
        )
        for claim in [
            "This verified predecessor/implementation head is the final evidence-only head.",
            "This predecessor is also the final commit used by this change.",
            "This verified predecessor is the final published PR head.",
        ]:
            with self.subTest(claim=claim):
                misleading = self.plan.replace(truthful.encode(), claim.encode(), 1)
                self.assertTrue(
                    self.checker.validate_album_art_evidence_contract(misleading)
                )

    def test_rejects_noncanonical_truthful_negation(self):
        truthful_variant = self.plan.replace(
            b"This verified predecessor/implementation head is not the final evidence-only head.",
            b"The predecessor is not the final head.",
            1,
        )
        self.assertTrue(
            self.checker.validate_album_art_evidence_contract(truthful_variant)
        )

    def test_rejects_missing_verified_predecessor_sha(self):
        missing_sha = self.plan.replace(
            b"1fd944d8b02118d817f98603aed3050bceb6dc32",
            b"0000000000000000000000000000000000000000",
            1,
        )
        self.assertTrue(
            self.checker.validate_album_art_evidence_contract(missing_sha)
        )

    def test_rejects_additive_text_inside_hosted_evidence_stanza(self):
        misleading = self.plan.replace(
            b"- pull-request run `27397458335`: success",
            b"- pull-request run `27397458335`: success\n\n"
            b"The SHA above is the final head.",
            1,
        )
        self.assertTrue(
            self.checker.validate_album_art_evidence_contract(misleading)
        )

    def test_rejects_predecessor_label_moved_outside_evidence_stanza(self):
        separated = self.plan.replace(
            b"verified predecessor/implementation head",
            b"implementation head",
            1,
        ) + b"\n\nGlossary: verified predecessor/implementation head.\n"
        self.assertTrue(
            self.checker.validate_album_art_evidence_contract(separated)
        )

    def test_rejects_changed_or_duplicated_hosted_evidence_stanza(self):
        changed_run = self.plan.replace(b"27397458335", b"00000000000", 1)
        duplicated = (
            self.plan + b"\n\n" + self.checker.ALBUM_ART_HOSTED_EVIDENCE.encode()
        )
        self.assertTrue(
            self.checker.validate_album_art_evidence_contract(changed_run)
        )
        self.assertTrue(
            self.checker.validate_album_art_evidence_contract(duplicated)
        )

    def test_rejects_hosted_evidence_hidden_in_nonprose_decoy(self):
        weakened = self.plan.replace(
            self.checker.ALBUM_ART_HOSTED_EVIDENCE.encode(),
            b"Completed on GitHub Actions for implementation evidence below.",
            1,
        )
        for decoy in [
            "<!--\n" + self.checker.ALBUM_ART_HOSTED_EVIDENCE + "\n-->",
            "```text\n" + self.checker.ALBUM_ART_HOSTED_EVIDENCE + "\n```",
        ]:
            with self.subTest(decoy=decoy.splitlines()[0]):
                hidden_inside_verification = weakened.replace(
                    b"\n## Boundaries",
                    ("\n\n" + decoy + "\n\n## Boundaries").encode(),
                    1,
                )
                self.assertTrue(
                    self.checker.validate_album_art_evidence_contract(
                        hidden_inside_verification
                    )
                )

    def test_rejects_contradictions_anywhere_in_plan_bytes(self):
        claims = [
            b"The verified predecessor is the final published PR head.",
            b"The verified predecessor is the current final head.",
            b"The implementation predecessor is the latest PR head.",
        ]
        placements = [
            lambda claim: claim + b"\n\n" + self.plan,
            lambda claim: self.plan + b"\n\n" + claim + b"\n",
            lambda claim: self.plan.replace(
                b"## Boundaries", claim + b"\n\n## Boundaries", 1
            ),
        ]
        for claim in claims:
            for place in placements:
                with self.subTest(claim=claim, place=place):
                    self.assertTrue(
                        self.checker.validate_album_art_evidence_contract(
                            place(claim)
                        )
                    )


class MakefileContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.checker = load_checker()
        cls.makefile = MAKEFILE_PATH.read_text(encoding="utf-8")

    def test_accepts_unit_tests_in_check_and_test_targets(self):
        self.assertEqual([], self.checker.validate_makefile_contract(self.makefile))

    def run_hostile_make(self, *arguments, environment=None):
        with tempfile.TemporaryDirectory(prefix="musichackday make path ") as temporary:
            temporary_root = Path(temporary)
            checkout = temporary_root / "checkout [hostile] 'quote"
            checkout.mkdir()
            makefile = checkout / "Makefile"
            shutil.copyfile(MAKEFILE_PATH, makefile)
            external = temporary_root / "external caller"
            external.mkdir()
            env = os.environ.copy()
            if environment:
                env.update(environment)
            result = subprocess.run(
                ["make", "--no-print-directory", "-n", "-f", str(makefile), *arguments],
                cwd=external,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )
            return result, str(checkout)

    def test_all_aliases_preserve_spaced_absolute_makefile_path(self):
        for target in ("check", "verify", "test", "unit-test", "lint", "build", "static-check"):
            for name, arguments, environment in (
                ("none", (target,), None),
                ("command", (target, "ROOT=/tmp/attacker-root"), None),
                ("environment", (target,), {"ROOT": "/tmp/attacker-root"}),
            ):
                with self.subTest(target=target, override=name):
                    result, checkout = self.run_hostile_make(
                        *arguments, environment=environment
                    )
                    self.assertEqual(0, result.returncode, result.stderr)
                    self.assertIn(checkout, result.stdout)
                    self.assertNotIn("/tmp/attacker-root", result.stdout)

    def test_command_line_makefile_list_override_fails_closed(self):
        result, _ = self.run_hostile_make(
            "check", "MAKEFILE_LIST=/tmp/attacker-root/Makefile"
        )
        self.assertNotEqual(0, result.returncode)
        self.assertIn("MAKEFILE_LIST must not be overridden", result.stderr)

    def test_environment_makefile_list_override_fails_closed(self):
        result, _ = self.run_hostile_make(
            "-e",
            "check",
            environment={"MAKEFILE_LIST": "/tmp/attacker-root/Makefile"},
        )
        self.assertNotEqual(0, result.returncode)
        self.assertIn("MAKEFILE_LIST must not be overridden", result.stderr)

    def test_rejects_check_without_unit_tests(self):
        old_makefile = self.makefile.replace(
            "check verify test unit-test:",
            "verify test unit-test:",
            1,
        )
        self.assertTrue(self.checker.validate_makefile_contract(old_makefile))

    def test_rejects_test_alias_without_unit_tests(self):
        incomplete = self.makefile.replace(
            "check verify test unit-test:",
            "check verify unit-test:",
            1,
        )
        self.assertTrue(self.checker.validate_makefile_contract(incomplete))

    def test_rejects_commented_verify_decoy(self):
        decoy = self.makefile.replace(
            "check verify test unit-test:",
            "# check verify test unit-test:\ncheck verify test unit-test:\n\t@true",
            1,
        )
        self.assertTrue(self.checker.validate_makefile_contract(decoy))

    def test_rejects_commented_recipe_decoy(self):
        decoy = self.makefile.replace(
            "\t@set -eu; test -n",
            "\t# @set -eu; test -n\n\t@true\n\t@test -n",
            1,
        )
        self.assertTrue(self.checker.validate_makefile_contract(decoy))

    def test_rejects_test_recipe_that_skips_discovery(self):
        skipped = self.makefile.replace(
            ' --expect-python 3.12,3.14 --gate;',
            ' --expect-python 3.12,3.14 --static;',
            1,
        )
        self.assertTrue(self.checker.validate_makefile_contract(skipped))

    def test_full_gate_fails_when_comment_decoy_skips_failing_test(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory) / "repo"
            shutil.copytree(
                ROOT,
                root,
                ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc"),
            )
            initialize_scratch_repository(root)
            makefile = (root / "Makefile").read_text(encoding="utf-8").replace(
                "check verify test unit-test:",
                "# check verify test unit-test:\ncheck verify test unit-test:\n\t@true",
                1,
            )
            (root / "Makefile").write_text(makefile, encoding="utf-8")
            (root / "tests/test_forced_failure.py").write_text(
                "import unittest\n\n"
                "class ForcedFailure(unittest.TestCase):\n"
                "    def test_fails(self):\n"
                "        self.fail('must execute')\n",
                encoding="utf-8",
            )
            result = subprocess.run(
                ["make", "check"],
                cwd=root,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                check=False,
            )
        self.assertNotEqual(0, result.returncode, result.stdout)

    def test_canonical_check_rejects_an_added_discovered_test(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory) / "repo"
            shutil.copytree(
                ROOT,
                root,
                ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc"),
            )
            initialize_scratch_repository(root)
            (root / "tests/test_android_baseline.py").unlink()
            (root / "tests/test_forced_failure.py").write_text(
                "import unittest\n\n"
                "class ForcedFailure(unittest.TestCase):\n"
                "    def test_fails(self):\n"
                "        self.fail('must execute')\n",
                encoding="utf-8",
            )
            result = subprocess.run(
                ["make", "check"],
                cwd=root,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                check=False,
            )
        self.assertNotEqual(0, result.returncode, result.stdout)
        self.assertIn("reviewed test inventory", result.stdout)

    def test_make_aliases_reject_python_and_path_noop_overrides(self):
        attacks = [
            (["PYTHON=true"], None),
            (["PYTHON=/usr/bin/true"], None),
            ([], "fake-path"),
        ]
        for arguments, path_attack in attacks:
            for target in ["lint", "static-check", "build", "test", "unit-test", "verify", "check"]:
                with self.subTest(arguments=arguments, path_attack=path_attack, target=target), tempfile.TemporaryDirectory() as temporary:
                    root = Path(temporary) / "repo"
                    shutil.copytree(
                        ROOT,
                        root,
                        ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc"),
                    )
                    initialize_scratch_repository(root)
                    workflow_path = root / ".github/workflows/check.yml"
                    workflow_path.write_bytes(workflow_path.read_bytes() + b"\n")
                    environment = os.environ.copy()
                    if path_attack:
                        fake_bin = root / "fake-bin"
                        fake_bin.mkdir()
                        fake_python = fake_bin / "python3"
                        fake_python.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
                        fake_python.chmod(0o755)
                        environment["PATH"] = str(fake_bin) + os.pathsep + environment["PATH"]
                    result = subprocess.run(
                        ["make", *arguments, target],
                        cwd=root,
                        env=environment,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        text=True,
                        check=False,
                    )
                    self.assertNotEqual(0, result.returncode, result.stdout)
                    self.assertIn("must match reviewed SHA-256", result.stdout)

    def test_python_312_gate_leaves_no_bytecode_artifacts(self):
        python = sys.executable
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory) / "repo"
            tests = root / "tests"
            tests.mkdir(parents=True)
            (tests / "test_bytecode.py").write_text(
                "import unittest\n\n"
                "class BytecodeTest(unittest.TestCase):\n"
                "    def test_passes(self):\n"
                "        self.assertTrue(True)\n",
                encoding="utf-8",
            )
            result = load_checker().run_isolated_test_process(
                root, expected_count=1, python_executable=python
            )
            artifacts = [
                path.relative_to(root).as_posix()
                for path in root.rglob("*")
                if path.name == "__pycache__" or path.suffix == ".pyc"
            ]
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("trusted-test-summary tests=1 skipped=0", result.stdout)
        self.assertEqual([], artifacts)


if __name__ == "__main__":
    unittest.main()
