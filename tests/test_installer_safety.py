"""Offline packaging and preflight tests; only disposable, user-owned paths."""
import os
from pathlib import Path
import plistlib
import stat
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
VERSION = (ROOT / 'VERSION').read_text().strip()


@unittest.skipIf(os.geteuid() == 0, "Installers intentionally reject root")
class InstallerSafetyTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir="/tmp", prefix="ajan-kur-test-")
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name).resolve()
        self.home = self.base / "Türkçe ev"
        self.home.mkdir(mode=0o700)
        self.desktop = self.home / "Masaüstü"
        self.desktop.mkdir(mode=0o700)
        self.data = self.home / "Veri alanı"
        self.stubs = self.base / "stubs"
        self.stubs.mkdir()
        for name, code in {
            "uname": "printf 'Darwin\\n'",
            "xdg-user-dir": 'printf "%s\\n" "$HOME/Masaüstü"',
            "gio": "exit 0",
        }.items():
            p = self.stubs / name
            p.write_text(f"#!/bin/sh\n{code}\n", encoding="utf-8")
            p.chmod(0o755)
        self.env = dict(os.environ, HOME=str(self.home), XDG_DATA_HOME=str(self.data),
                        XDG_CONFIG_HOME=str(self.home / "config"), PATH=f"{self.stubs}:/usr/bin:/bin")
        self.linux = self.data / "ajan-atolyesi"
        self.mac = self.home / "Applications" / "Ajan Atölyesi.app" / "Contents"

    def run_sh(self, file):
        return subprocess.run(["bash", str(ROOT / file)], env=self.env, cwd=self.home,
                              capture_output=True, text=True, timeout=12, check=False)

    def install(self, file):
        result = self.run_sh(file)
        self.assertEqual(result.returncode, 0, result.stderr)

    def version(self, launcher):
        return subprocess.check_output([str(launcher), "--version"], env=self.env, cwd=self.home,
                                       text=True, timeout=5).strip()

    @staticmethod
    def snapshot(base):
        items = {}
        for p in base.rglob("*"):
            st = p.lstat()
            if stat.S_ISLNK(st.st_mode):
                value = os.readlink(p)
            elif stat.S_ISREG(st.st_mode):
                value = p.read_bytes()
            else:
                value = None
            items[str(p.relative_to(base))] = (st.st_mode, value)
        return items

    def assert_preflight_rejects(self, file):
        before = self.snapshot(self.base)
        result = self.run_sh(file)
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("Güvenli olmayan kurulum yolu", result.stderr)
        self.assertEqual(self.snapshot(self.base), before)

    def safe_standin(self, name, directory=False):
        path = self.base / name
        if directory:
            path.mkdir()
        else:
            path.write_text("Ambalaj ön kontrolü için boş örnek.\n", encoding="utf-8")
        return path

    def test_linux_package_and_safe_reinstall_keep_unrelated_user_file(self):
        self.install("masaustune-kur.sh")
        self.assertTrue(self.version(self.linux / "ac").startswith(VERSION))
        self.assertTrue((self.data / "applications/ajan-atolyesi.desktop").is_file())
        self.assertTrue((self.desktop / "Ajan Atölyesi.desktop").is_file())
        unrelated = self.linux / "my-notes.txt"
        unrelated.write_text("korunur", encoding="utf-8")
        self.install("masaustune-kur.sh")
        self.assertEqual(unrelated.read_text(), "korunur")
        self.assertEqual(stat.S_IMODE((self.linux / ".ajan-surum-bilgisi").stat().st_mode), 0o600)

    def test_linux_rejects_linked_nested_dir_before_write(self):
        self.install("masaustune-kur.sh")
        real = self.linux / "docs"
        real.rename(self.linux / "docs-old")
        real.symlink_to(self.safe_standin("linux-dir", directory=True), target_is_directory=True)
        self.assert_preflight_rejects("masaustune-kur.sh")

    def test_linux_rejects_linked_leaves_and_menu_parent(self):
        self.install("masaustune-kur.sh")
        standin = self.safe_standin("linux-file")
        for leaf in (self.linux / ".ajan-atolyesi", self.linux / "bin/ajan-pencere",
                     self.linux / "ac", self.linux / ".ajan-surum-bilgisi",
                     self.desktop / "Ajan Atölyesi.desktop"):
            with self.subTest(leaf=leaf.name):
                prior = leaf.with_name(leaf.name + ".prior")
                leaf.rename(prior)
                leaf.symlink_to(standin)
                self.assert_preflight_rejects("masaustune-kur.sh")
                leaf.unlink()
                prior.rename(leaf)
        menu_dir = self.data / "applications"
        menu_dir.rename(self.data / "applications-old")
        menu_dir.symlink_to(self.safe_standin("menu-dir", directory=True), target_is_directory=True)
        self.assert_preflight_rejects("masaustune-kur.sh")

    def test_refuses_unmanaged_targets_and_group_writable_parent(self):
        self.data.mkdir(mode=0o700)
        self.linux.mkdir(mode=0o700)
        before = self.snapshot(self.base)
        result = self.run_sh("masaustune-kur.sh")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Mevcut klasöre dokunulmadı", result.stderr)
        self.assertEqual(before, self.snapshot(self.base))
        self.data.chmod(0o775)
        self.assert_preflight_rejects("masaustune-kur.sh")
        apps = self.home / "Applications"
        apps.mkdir()
        apps.chmod(0o775)
        self.assert_preflight_rejects("kur-macos.sh")

    def test_mac_package_and_safe_reinstall_keep_unmanaged_files(self):
        self.install("kur-macos.sh")
        metadata = plistlib.loads((self.mac / "Info.plist").read_bytes())
        self.assertEqual(metadata["CFBundleShortVersionString"], VERSION)
        self.assertTrue(self.version(self.mac / "MacOS/ajan-atolyesi").startswith(VERSION))
        unmanaged = self.mac / "Resources/local-note"
        unmanaged.write_text("korunur", encoding="utf-8")
        self.install("kur-macos.sh")
        self.assertEqual(unmanaged.read_text(), "korunur")

    def test_mac_refuses_symlinked_bundle_parents_and_managed_leaves(self):
        self.install("kur-macos.sh")
        standin = self.safe_standin("mac-file")
        for leaf in (self.mac / ".ajan-atolyesi", self.mac / "Info.plist",
                     self.mac / "MacOS/ajan-atolyesi", self.mac / "Resources/bin/ajan-pencere",
                     self.mac / "Resources/.ajan-surum-bilgisi"):
            with self.subTest(leaf=leaf.name):
                prior = leaf.with_name(leaf.name + ".prior")
                leaf.rename(prior)
                leaf.symlink_to(standin)
                self.assert_preflight_rejects("kur-macos.sh")
                leaf.unlink()
                prior.rename(leaf)
        for directory in (self.home / "Applications", self.mac, self.mac / "Resources/bin"):
            with self.subTest(directory=directory.name):
                prior = directory.with_name(directory.name + ".prior")
                directory.rename(prior)
                directory.symlink_to(self.safe_standin(f"dir-{directory.name}", directory=True),
                                     target_is_directory=True)
                self.assert_preflight_rejects("kur-macos.sh")
                directory.unlink()
                prior.rename(directory)
