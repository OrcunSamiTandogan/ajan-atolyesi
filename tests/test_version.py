import io
from pathlib import Path
import shutil
import subprocess
import tarfile
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
ORIGIN = "git@github.com:OrcunSamiTandogan/ajan-atolyesi.git"


@unittest.skipUnless(shutil.which("git") and shutil.which("bash"), "Git ve Bash gerekiyor")
class VersionTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.repo = self.base / "fixture"
        self.repo.mkdir()
        self.git("init", "--initial-branch=master", "-q")
        self.git("config", "user.email", "version@example.test")
        self.git("config", "user.name", "Version fixture")
        self.git("config", "commit.gpgsign", "false")
        self.git("remote", "add", "origin", ORIGIN)
        (self.repo / "bin").mkdir()
        for item in ("VERSION", "SOURCE_REVISION", ".gitattributes", "bin/ajan-surum"):
            shutil.copyfile(ROOT / item, self.repo / item)
        self.git("add", ".")
        self.git("commit", "-qm", "fixture baseline")
        (self.repo / "marker.txt").write_text("main", encoding="utf-8")
        self.git("add", "marker.txt")
        self.git("commit", "-qm", "fixture mainline")

    def git(self, *cmd):
        return subprocess.check_output(["git", "-C", str(self.repo), *cmd], text=True).strip()

    def version(self, *args, checkout=None):
        checkout = checkout or self.repo
        return subprocess.check_output(
            ["bash", str(checkout / "bin/ajan-surum"), *args], text=True
        ).strip()

    def test_first_parent_ignores_merged_branch_commits(self):
        self.git("checkout", "-qb", "feature")
        for i in range(2):
            self.git("commit", "--allow-empty", "-qm", f"fixture side {i}")
        self.assertIn("Derleme bilinmiyor", self.version())
        self.git("checkout", "-q", "master")
        self.git("merge", "--no-ff", "-qm", "fixture merge", "feature")
        self.assertEqual(self.git("rev-list", "--count", "HEAD"), "5")
        self.assertIn("0.1.0 · Derleme 3 · " + self.git("rev-parse", "--short=7", "HEAD"),
                      self.version())

    def test_no_count_for_dirty_tree_shallow_history_or_other_origin(self):
        (self.repo / "marker.txt").write_text("changed", encoding="utf-8")
        self.assertIn("Derleme bilinmiyor", self.version())
        self.assertIn("Yerel değişiklikler", self.version())
        self.git("checkout", "--", "marker.txt")
        shallow = self.base / "shallow"
        subprocess.check_call(["git", "clone", "-q", "--depth", "1", self.repo.as_uri(), str(shallow)])
        subprocess.check_call(["git", "-C", str(shallow), "remote", "set-url", "origin", ORIGIN])
        self.assertIn("Derleme bilinmiyor", self.version(checkout=shallow))
        self.assertIn(self.git("rev-parse", "--short=7", "HEAD"), self.version(checkout=shallow))
        self.git("remote", "set-url", "origin", "https://example.test/unrelated.git")
        self.assertEqual(self.version(), "0.1.0 · Derleme bilinmiyor")

    def test_archive_and_installed_snapshot_are_distinct(self):
        archive = self.base / "archive"
        archive.mkdir()
        data = subprocess.check_output(["git", "-C", str(self.repo), "archive", "HEAD"])
        with tarfile.open(fileobj=io.BytesIO(data)) as exported:
            for name in ("VERSION", "SOURCE_REVISION", "bin/ajan-surum"):
                item = exported.extractfile(name)
                dest = archive / name
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(item.read())
        short = self.git("rev-parse", "--short=7", "HEAD")
        self.assertEqual(self.version(checkout=archive), f"0.1.0 · Derleme bilinmiyor · {short}")
        (archive / ".ajan-surum-bilgisi").write_text(self.version("--metadata") + "\n", encoding="utf-8")
        self.assertEqual(self.version(checkout=archive), f"0.1.0 · Derleme 2 · {short}")
        (archive / ".ajan-surum-bilgisi").unlink()
        (archive / "SOURCE_REVISION").write_text("$Format:%H$\n", encoding="utf-8")
        self.assertEqual(self.version(checkout=archive), "0.1.0 · Derleme bilinmiyor")
