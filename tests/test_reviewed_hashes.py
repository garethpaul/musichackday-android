import hashlib
import importlib.util
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
CHECKER_PATH = ROOT / "scripts/check-android-baseline.py"
PLAN_PATH = ROOT / "docs/plans/2026-06-12-album-art-connection-guard.md"
MAKEFILE_PATH = ROOT / "Makefile"
EXPECTED_PLAN_SHA256 = (
    "a3698f126caa282ffe3242a37dd1bec6e29b0d2fbd086afcf03e324f3937eb3e"
)
EXPECTED_TEST_COUNT = 91
TEST_REVIEWED_FILE_SHA256 = {
    "app/src/main/java/com/twitterdev/rdio/app/RdioApp.java": (
        "fb91ad06a10932969adf680e877b76db2b4c0559513cf2bccb471fbb5fd1bc3d"
    ),
    ".github/workflows/check.yml": (
        "3ac196785a75b7a744a1690a396feac24cf1b1fffd189dc2474ff01e6d01b57f"
    ),
}
EXPECTED_REVIEWED_BYTE_CONTRACT = '''The following raw bytes were reviewed together:

- `app/src/main/java/com/twitterdev/rdio/app/RdioApp.java`
  SHA-256: `fb91ad06a10932969adf680e877b76db2b4c0559513cf2bccb471fbb5fd1bc3d`
- `.github/workflows/check.yml`
  SHA-256: `3ac196785a75b7a744a1690a396feac24cf1b1fffd189dc2474ff01e6d01b57f`

Future legitimate changes require explicit review and coordinated updates to the protected file, checker constant, independent test constant, and this contract stanza.'''


def load_checker():
    spec = importlib.util.spec_from_file_location("android_baseline", CHECKER_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class IndependentlyPinnedReviewedHashesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.checker = load_checker()

    def test_checker_hashes_equal_independent_test_literals(self):
        self.assertEqual(
            TEST_REVIEWED_FILE_SHA256,
            self.checker.REVIEWED_FILE_SHA256,
        )

    def test_checker_contract_equals_independent_literal(self):
        self.assertEqual(
            EXPECTED_REVIEWED_BYTE_CONTRACT,
            self.checker.REVIEWED_BYTE_CONTRACT,
        )

    def test_independent_contract_contains_each_independent_hash(self):
        for expected_sha256 in TEST_REVIEWED_FILE_SHA256.values():
            with self.subTest(expected_sha256=expected_sha256):
                self.assertEqual(
                    1,
                    EXPECTED_REVIEWED_BYTE_CONTRACT.count(expected_sha256),
                )

    def test_protected_bytes_equal_independent_test_literals(self):
        for relative_path, expected_sha256 in TEST_REVIEWED_FILE_SHA256.items():
            with self.subTest(relative_path=relative_path):
                self.assertEqual(
                    expected_sha256,
                    hashlib.sha256((ROOT / relative_path).read_bytes()).hexdigest(),
                )

    def test_evidence_plan_hash_equals_independent_literal(self):
        self.assertEqual(EXPECTED_PLAN_SHA256, self.checker.EVIDENCE_PLAN_SHA256)
        self.assertEqual(
            EXPECTED_PLAN_SHA256,
            hashlib.sha256(PLAN_PATH.read_bytes()).hexdigest(),
        )

    def test_make_and_checker_pin_all_reviewed_hash_constants(self):
        makefile = MAKEFILE_PATH.read_text(encoding="utf-8")
        reviewed_hashes = {
            **TEST_REVIEWED_FILE_SHA256,
            **self.checker.REVIEWED_TEST_SHA256,
            str(PLAN_PATH.relative_to(ROOT)): EXPECTED_PLAN_SHA256,
        }
        for relative_path, expected_sha256 in reviewed_hashes.items():
            with self.subTest(relative_path=relative_path):
                variable = self.checker.make_hash_variable(relative_path)
                self.assertIn(f"{variable} := {expected_sha256}\n", makefile)
                self.assertEqual(
                    expected_sha256,
                    hashlib.sha256((ROOT / relative_path).read_bytes()).hexdigest(),
                )

    def test_checker_accepts_only_exact_regular_test_inventory(self):
        self.assertEqual([], self.checker.validate_test_inventory(ROOT))

    def test_checker_rejects_repo_controlled_import_shadows(self):
        shadows = [
            "hashlib.py",
            "scripts/hashlib.py",
            "sitecustomize.py",
            "usercustomize.py",
            "scripts/pathlib/__init__.py",
            "subprocess/__init__.py",
            "tests/os.py",
        ]
        for relative_path in shadows:
            with self.subTest(relative_path=relative_path), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary) / "repo"
                root.mkdir()
                path = root / relative_path
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("raise RuntimeError('shadow imported')\n", encoding="utf-8")
                self.assertTrue(self.checker.validate_import_shadow_inventory(root))

    def test_sanitized_python_environment_removes_import_hooks_and_skip_hook(self):
        environment = self.checker.sanitized_python_environment(
            {
                "PATH": "/usr/bin",
                "PYTHONPATH": "/attacker",
                "PYTHONHOME": "/attacker-python",
                "PYTHONSTARTUP": "/attacker/start.py",
                "MHD_NESTED_GATE": "1",
            }
        )
        self.assertEqual("/usr/bin", environment["PATH"])
        self.assertEqual("1", environment["PYTHONNOUSERSITE"])
        self.assertEqual("1", environment["PYTHONDONTWRITEBYTECODE"])
        for name in ["PYTHONPATH", "PYTHONHOME", "PYTHONSTARTUP", "MHD_NESTED_GATE"]:
            self.assertNotIn(name, environment)

    def test_verifier_and_runner_require_bytecode_suppression(self):
        makefile = MAKEFILE_PATH.read_text(encoding="utf-8")
        workflow = (ROOT / ".github/workflows/check.yml").read_text(encoding="utf-8")
        self.assertIn(" -I -B ", makefile)
        self.assertIn(" -I -B ", workflow)
        self.assertIn('"-I",\n                "-B",', CHECKER_PATH.read_text(encoding="utf-8"))
        self.assertTrue(self.checker.sys.dont_write_bytecode)

    def test_checker_rejects_python_bytecode_artifacts(self):
        artifacts = [
            "scripts/__pycache__/check-android-baseline.cpython-312.pyc",
            "tests/__pycache__/test_android_baseline.cpython-312.pyc",
            "hashlib.pyc",
        ]
        for relative_path in artifacts:
            with self.subTest(relative_path=relative_path), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary) / "repo"
                path = root / relative_path
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(b"bytecode")
                self.assertTrue(self.checker.validate_no_python_artifacts(root))

    def test_make_interpreter_is_override_protected_and_absolute(self):
        makefile = MAKEFILE_PATH.read_text(encoding="utf-8")
        self.assertIn("override PYTHON :=", makefile)
        self.assertIn("override PATH :=", makefile)
        self.assertIn("--expect-python 3.12,3.14", makefile)
        self.assertNotIn("PYTHON ?=", makefile)

    def test_workflow_resolves_and_checks_setup_python_interpreter(self):
        workflow = (ROOT / ".github/workflows/check.yml").read_text(encoding="utf-8")
        self.assertIn('python_bin="$pythonLocation/bin/python3"', workflow)
        self.assertIn('test -x "$python_bin"', workflow)
        self.assertIn('--expect-python 3.12', workflow)
        self.assertNotIn("$(command -v python3)", workflow)

    def test_isolated_runner_rejects_skips_and_wrong_test_count(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "repo"
            tests = root / "tests"
            tests.mkdir(parents=True)
            (tests / "test_skip.py").write_text(
                "import unittest\n\n"
                "class SkipTest(unittest.TestCase):\n"
                "    @unittest.skip('malicious skip')\n"
                "    def test_skipped(self):\n"
                "        pass\n",
                encoding="utf-8",
            )
            result = self.checker.run_isolated_test_process(root, expected_count=1)
            self.assertNotEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertIn("skipped=1", result.stdout + result.stderr)
            result = self.checker.run_isolated_test_process(root, expected_count=2)
            self.assertNotEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertIn("expected 2 tests", result.stdout + result.stderr)

    def test_expected_test_count_is_independently_anchored(self):
        self.assertEqual(EXPECTED_TEST_COUNT, self.checker.EXPECTED_TEST_COUNT)
        makefile = MAKEFILE_PATH.read_text(encoding="utf-8")
        self.assertIn(f"EXPECTED_TEST_COUNT := {EXPECTED_TEST_COUNT}\n", makefile)

    def test_checker_rejects_added_symlink_and_nonregular_test_paths(self):
        mutations = {
            "added": lambda root: (root / "tests/test_extra.py").write_text(
                "import unittest\n", encoding="utf-8"
            ),
            "symlink": lambda root: (
                (root / "tests/test_android_baseline.py").unlink(),
                (root / "tests/test_android_baseline.py").symlink_to(
                    "test_reviewed_hashes.py"
                ),
            ),
            "directory": lambda root: (
                (root / "tests/test_android_baseline.py").unlink(),
                (root / "tests/test_android_baseline.py").mkdir(),
            ),
            "mode": lambda root: (root / "tests/test_android_baseline.py").chmod(
                0o755
            ),
        }
        for name, mutate in mutations.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary) / "repo"
                (root / "tests").mkdir(parents=True)
                for relative_path in self.checker.REVIEWED_TEST_SHA256:
                    source = ROOT / relative_path
                    destination = root / relative_path
                    shutil.copy2(source, destination)
                mutate(root)
                self.assertTrue(self.checker.validate_test_inventory(root))

    def test_plan_contains_exact_independent_reviewed_contract(self):
        plan = PLAN_PATH.read_text(encoding="utf-8")
        self.assertEqual(
            EXPECTED_REVIEWED_BYTE_CONTRACT,
            self.checker.markdown_subsection(plan, "Reviewed Byte Contract"),
        )

    def test_workflow_reviewed_bytes_keep_exact_unoverridden_command(self):
        workflow = (ROOT / ".github/workflows/check.yml").read_bytes()
        self.assertIn(b"PYTHONNOUSERSITE=1", workflow)
        self.assertIn(b"/usr/bin/env -i", workflow)
        self.assertIn(b'PATH="/usr/bin:/bin"', workflow)
        self.assertIn(b'"$python_bin" -I -B', workflow)
        self.assertIn(
            b'--root "$GITHUB_WORKSPACE" --expect-python 3.12 --gate', workflow
        )
        self.assertNotIn(b"make check", workflow)
        self.assertNotIn(b"MHD_NESTED_GATE", workflow)
        self.assertNotIn(b"MAKEFLAGS", workflow)
        self.assertNotIn(b"bash -c", workflow)
        self.assertNotIn(b"sh -c", workflow)


if __name__ == "__main__":
    unittest.main()
