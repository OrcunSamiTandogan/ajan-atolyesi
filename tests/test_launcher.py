import os
from contextlib import redirect_stderr
from io import StringIO
from pathlib import Path
import runpy
import subprocess
import tempfile
import unittest
from unittest.mock import patch

APP = runpy.run_path(str(Path(__file__).resolve().parents[1] / "bin/ajan-pencere"))
MOCK = "nvapi-" + "fake_fixture_only_" + ("a" * 24)


class LauncherTests(unittest.TestCase):
    def test_setup_has_fixed_commands(self):
        for role in ("claude", "codex"):
            for selection in ("pi", "evren", "both"):
                args = APP["session_command"]("setup-" + role, "normal", selection)
                self.assertEqual((Path(args[0]).name, args[1:]),
                                 ("ajan-kur", [role, "normal", "setup", selection]))
            with self.assertRaises(ValueError):
                APP["session_command"]("setup-" + role, "unsafe", "pi")
            self.assertEqual(APP["session_command"]("setup-" + role, "existing")[-3:],
                             [role, "existing", "plain"])
            for selection in (None, "", "bad"):
                with self.assertRaises(ValueError):
                    APP["session_command"]("setup-" + role, "normal", selection)
            with self.assertRaises(ValueError):
                APP["session_command"](role, "normal", "pi")
        with self.assertRaises(ValueError):
            APP["session_command"]("invalid")
        with self.assertRaises(ValueError):
            APP["session_command"]("evren", "unsafe")

    def test_setup_prompt_only_mentions_checked_providers(self):
        launcher = Path(__file__).resolve().parents[1] / "bin/ajan-kur"
        for choice, included in (("pi", ("Pi + NVIDIA",)), ("evren", ("EVREN + DeepSeek",)),
                                 ("both", ("Pi + NVIDIA", "EVREN + DeepSeek"))):
            prompt = subprocess.check_output([launcher, "--print-setup-prompt", choice], text=True)
            self.assertIn("tekrar seçim sorma", prompt)
            self.assertIn("Model çağrısı yapma", prompt)
            for label in ("Pi + NVIDIA", "EVREN + DeepSeek"):
                self.assertEqual(label in prompt, label in included)
        bad = subprocess.run([launcher, "--print-setup-prompt", "pi; unexpected"], capture_output=True)
        self.assertEqual(bad.returncode, 2)
        self.assertEqual(bad.stdout, b"")

    def test_evren_starts_the_credential_isolating_wrapper(self):
        args = APP["session_command"]("evren")
        self.assertEqual(Path(args[-1]).name, "evren-dsh-terminal")
        self.assertNotIn("EVREN_API_KEY", " ".join(args))

    def test_new_pi_launch_does_not_attach_to_a_concurrently_created_session(self):
        pi_tmux = APP["pi_tmux"]
        with patch.dict(pi_tmux.__globals__, session_attachment=lambda _: ("trusted", ("/test/tmux", "$9"))), \
                patch("shutil.which", return_value="/test/tmux"), patch("subprocess.run") as run, \
                patch("os.execve") as execute, redirect_stderr(StringIO()):
            self.assertEqual(pi_tmux(), 1)
        run.assert_not_called()
        execute.assert_not_called()

    def test_pi_without_saved_key_drops_inherited_provider_keys(self):
        pi_terminal = APP["pi_terminal"]
        with patch.dict(pi_terminal.__globals__, pi_binary=lambda: "/test/pi", saved_key=lambda: None), \
                patch.dict(os.environ, {"NVIDIA_API_KEY": MOCK, "EVREN_API_KEY": "fake-evren"}), \
                patch("os.execve") as execute:
            pi_terminal()
        execute.assert_called_once()
        binary, args, env = execute.call_args.args
        self.assertEqual((binary, args), ("/test/pi", ["/test/pi"]))
        self.assertNotIn("NVIDIA_API_KEY", env)
        self.assertNotIn("EVREN_API_KEY", env)

    def test_save_key_read_mode_and_command_has_no_secret(self):
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, XDG_CONFIG_HOME=tmp):
            self.assertIsNone(APP["saved_key"]())
            APP["save_key"](MOCK)
            path = Path(tmp) / "ajan-atolyesi/.env"
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)
            self.assertEqual(APP["saved_key"](), MOCK)
            self.assertNotIn(MOCK, " ".join(APP["session_command"]("pi")))
            path.chmod(0o644)
            with self.assertRaises(OSError):
                APP["saved_key"]()

    def test_invalid_key_never_creates_file(self):
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, XDG_CONFIG_HOME=tmp):
            with self.assertRaises(ValueError):
                APP["save_key"]("nvapi-ABC\nexport OOPS=1")
            self.assertIsNone(APP["saved_key"]())

    def test_claude_and_codex_are_separate_terminal_choices(self):
        roles = dict(APP["OPTIONS"])
        self.assertEqual(roles["Claude oturumu"], "claude")
        self.assertEqual(roles["Codex oturumu"], "codex")
        for role in ("claude", "codex"):
            self.assertEqual(APP["session_command"](role)[-3:], [role, "normal", "plain"])
            self.assertEqual(APP["session_command"](role, "existing")[-3:], [role, "existing", "plain"])
        self.assertEqual(set(APP["STATES"]), {"closed", "ready", "active"})

    def test_save_both_keys_without_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, XDG_CONFIG_HOME=tmp):
            APP["save_key"](MOCK)
            APP["save_key"]("evren_mock_key", "EVREN_API_KEY")
            self.assertEqual(APP["saved_key"](), MOCK)
            self.assertEqual(APP["saved_key"]("EVREN_API_KEY"), "evren_mock_key")
            with self.assertRaises(ValueError):
                APP["save_key"]("evren_bad\nKEY=injection", "EVREN_API_KEY")

    def test_named_session_targets_exact_normal_owned_session_only(self):
        def fake_run(args, **kwargs):
            if args[1] == "list-sessions":
                return subprocess.CompletedProcess(args, 0,
                    "aa-codex-other $1\naa-codex $9\naa-claude $4\n", "")
            self.assertEqual(args[1:3], ["show-environment", "-t"])
            self.assertIn(args[3], ("$9", "$4"))
            valid = {"AA_ATOLYE_OWNER": APP["PUBLIC_TMUX_OWNER"], "AA_SETUP_MODE": "normal"}
            value = "unsafe" if args[3:] == ["$4", "AA_SETUP_MODE"] else valid[args[4]]
            return subprocess.CompletedProcess(args, 0, f"{args[4]}={value}\n", "")
        with patch("shutil.which", return_value="/test/tmux"), patch("subprocess.run", side_effect=fake_run):
            self.assertEqual(APP["named_session"]("codex"), ("/test/tmux", "$9"))
            self.assertEqual(APP["session_attachment"]("claude"), ("blocked", None))
            self.assertEqual(APP["session_attachment"]("codex-other"), ("absent", None))

    def test_cli_refuses_non_normal_unowned_and_replaced_sessions(self):
        launcher = Path(__file__).resolve().parents[1] / "bin/ajan-kur"
        with tempfile.TemporaryDirectory() as tmp:
            tmux = Path(tmp) / "tmux"
            tmux.write_text("""#!/bin/sh
case "$1" in
  has-session) test "$3" = "=aa-codex" ;;
  list-sessions) printf '%s\n' 'aa-codex-extra $1' 'aa-codex $9' ;;
  show-environment)
    test "$3" = '$9' || exit 1
    case "$4" in
      AA_ATOLYE_OWNER) test -n "$MOCK_OWNER" && printf '%s\n' "AA_ATOLYE_OWNER=$MOCK_OWNER" ;;
      AA_SETUP_MODE) printf '%s\n' "AA_SETUP_MODE=$MOCK_MODE" ;;
      *) exit 1 ;;
    esac ;;
  attach-session) printf 'attached:%s\n' "$3" ;;
  *) exit 1 ;;
esac
""")
            tmux.chmod(0o700)
            def launch(owner, mode, expected, entry="existing"):
                env = {"PATH": f"{tmp}:/usr/bin:/bin", "HOME": tmp,
                       "MOCK_OWNER": owner, "MOCK_MODE": mode}
                return subprocess.run([launcher, "codex", entry, "plain", expected], input="",
                                      text=True, capture_output=True, env=env, timeout=5)
            owner = APP["PUBLIC_TMUX_OWNER"]
            accepted = launch(owner, "normal", "$9")
            self.assertEqual((accepted.returncode, accepted.stdout.strip()), (0, "attached:$9"))
            for args in (("", "normal", "$9"), (owner, "unsafe", "$9"),
                         (owner, "normal", "$1"), ("", "normal", "", "normal")):
                rejected = launch(*args)
                self.assertEqual(rejected.returncode, 1)
                self.assertNotIn("attached:", rejected.stdout)
                self.assertIn("Bağlanılmadı", rejected.stderr)
            self.assertEqual(launch(owner, "normal", "", "unsafe").returncode, 2)

    def test_pi_defaults_to_minimax_without_passing_a_secret_in_argv(self):
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, {
                "XDG_CONFIG_HOME": tmp, "EVREN_API_KEY": "private-mock",
                "ANTHROPIC_API_KEY": "private-mock", "SSH_AUTH_SOCK": "/tmp/fake-agent"}):
            APP["save_key"](MOCK)
            with patch("shutil.which", return_value="/test/pi"), patch("os.execve", side_effect=SystemExit) as launch:
                with self.assertRaises(SystemExit):
                    APP["pi_terminal"]()
                binary, argv, env = launch.call_args.args
                self.assertEqual(binary, "/test/pi")
                self.assertEqual(argv, ["/test/pi", "--models", APP["NVIDIA_SCOPE"], "--model",
                                        "nvidia/minimaxai/minimax-m3.1-flash", "--thinking", "low", "--no-extensions"])
                self.assertNotIn(MOCK, (Path(env["PI_CODING_AGENT_DIR"]) / "models.json").read_text())
                self.assertEqual(env["NVIDIA_API_KEY"], MOCK)
                self.assertNotIn(MOCK, argv)
                for variable in ("EVREN_API_KEY", "ANTHROPIC_API_KEY", "SSH_AUTH_SOCK"):
                    self.assertNotIn(variable, env)

    def test_nvidia_config_keeps_existing_models_and_refuses_a_different_endpoint(self):
        import json
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            path = directory / "models.json"
            path.write_text(json.dumps({"providers": {"nvidia": {"models": [{"id": "other"}]}}}))
            APP["add_nvidia_models"](directory)
            expected = path.read_text()
            APP["add_nvidia_models"](directory)
            self.assertEqual(path.read_text(), expected)
            models = json.loads(expected)["providers"]["nvidia"]["models"]
            self.assertEqual([m["id"] for m in models], ["other", APP["KIMI_ID"], APP["MINIMAX_ID"]])
            path.write_text(expected.replace(APP["NVIDIA_URL"], "https://example.org/v1"))
            with self.assertRaises(ValueError):
                APP["add_nvidia_models"](directory)

    def test_icons_persist_by_session_and_reset_independently(self):
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, XDG_CONFIG_HOME=tmp):
            APP["save_session_icon"]("codex", "emblem-favorite-symbolic")
            APP["save_session_icon"]("claude", "security-high-symbolic")
            self.assertEqual(APP["session_icons"]()["codex"], "emblem-favorite-symbolic")
            with self.assertRaises(ValueError):
                APP["save_session_icon"]("codex", "/tmp/not-an-icon")
            APP["save_session_icon"]("codex", None)
            self.assertEqual(APP["session_icons"](), {"claude": "security-high-symbolic"})

    def test_key_status_uses_app_file_and_never_exposes_secret(self):
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, XDG_CONFIG_HOME=tmp):
            self.assertEqual(APP["key_file_status"]()["NVIDIA_API_KEY"], "Henüz girilmedi")
            APP["save_key"](MOCK)
            status = APP["key_file_status"]()
            self.assertEqual(status["NVIDIA_API_KEY"], "Kayıtlı")
            self.assertEqual(status["EVREN_API_KEY"], "Henüz girilmedi")
            self.assertNotIn(MOCK, str(status))

    def test_standalone_pi_setup_pins_package_and_rejects_old_node(self):
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, XDG_CONFIG_HOME=tmp):
            with patch("shutil.which", side_effect=lambda name: "/test/" + name):
                with patch("subprocess.check_output", return_value="v22.18.0"):
                    self.assertIsNone(APP["pi_install_command"]())
                with patch("subprocess.check_output", return_value="v22.19.0"):
                    args = APP["pi_install_command"]()
            self.assertEqual(args[0], "/test/npm")
            self.assertIn("--ignore-scripts", args)
            self.assertEqual(args[-3:], ["--prefix", str(Path(tmp) / "ajan-atolyesi/pi-install"),
                                         "@earendil-works/pi-coding-agent@1.6.0"])

    def test_pi_install_location_works_without_system_pi(self):
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, XDG_CONFIG_HOME=tmp):
            with patch("shutil.which", return_value=None):
                self.assertIsNone(APP["pi_binary"]())
                path = APP["pi_prefix"]() / "bin/pi"
                path.parent.mkdir(parents=True)
                path.write_text("#!/bin/sh\n")
                path.chmod(0o700)
                self.assertEqual(APP["pi_binary"](), str(path))

    def test_bad_key_file_is_reported_without_overwriting_or_showing_key(self):
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, XDG_CONFIG_HOME=tmp):
            path = Path(tmp) / "ajan-atolyesi/.env"
            path.parent.mkdir()
            malformed = "NVIDIA_API_KEY=" + MOCK + "\nBROKEN=reserved\n"
            path.write_text(malformed)
            path.chmod(0o600)
            self.assertEqual(set(APP["key_file_status"]().values()), {"Okunamadı"})
            with self.assertRaises(ValueError):
                APP["save_key"](MOCK)
            self.assertEqual(path.read_text(), malformed)


    def test_web_and_cli_are_separate_and_only_cli_has_a_tmux_target(self):
        self.assertEqual(Path(APP["session_command"]("evren-cli")[0]).name, "ajan-dsh-pane")
        self.assertEqual(Path(APP["session_command"]("evren")[-1]).name, "evren-dsh-terminal")
        self.assertEqual(APP["tmux_role"]("evren-cli"), "evren-cli")
        self.assertIsNone(APP["tmux_role"]("evren"))
        with self.assertRaises(ValueError):
            APP["session_command"]("evren-cli", "unsafe")


    def test_plain_terminal_uses_interactive_shell_without_provider(self):
        self.assertEqual(APP["OPTIONS"][-1], ("Terminal", "terminal"))
        with patch.dict(os.environ, SHELL="/bin/sh"):
            self.assertEqual(APP["session_command"]("terminal"), ["/bin/sh", "-i"])
        with patch.dict(os.environ, SHELL="relative-or-missing"):
            self.assertEqual(APP["session_command"]("terminal"), ["/bin/bash", "-i"])
        self.assertIsNone(APP["tmux_role"]("terminal"))


    def test_reminder_lists_only_exact_observed_sessions(self):
        from subprocess import CompletedProcess
        lines = "aa-codex $5\naa-evren-cli-test $8\naa-evren-cli $9\naa-claude not-an-id\n"
        outputs = [lines, f'AA_ATOLYE_OWNER={APP["PUBLIC_TMUX_OWNER"]}\n', "AA_SETUP_MODE=normal\n"]
        with patch("shutil.which", return_value="/test/tmux"), patch(
                "subprocess.run", side_effect=[CompletedProcess([], 0, line, "") for line in outputs]):
            names = APP["atolye_sessions"]()
        self.assertEqual(set(names), {"aa-codex", "aa-evren-cli"})
        reminder = APP["session_reminder"](names)
        self.assertIn("tmux hedefleri: aa-codex, aa-evren-cli.", reminder)
        self.assertNotIn("aa-evren-cli-test", reminder)
        self.assertIn("doğrulanmış açık hedef yok", APP["session_reminder"]({}))


    def test_fresh_install_checks_installed_binary_and_version_not_global(self):
        with tempfile.TemporaryDirectory() as tmp:
            prefix = Path(tmp)
            self.assertFalse(APP["installed_package_ready"](prefix, "pi", APP["PI_PACKAGE"], {}))
            tool = prefix / "bin/pi"
            tool.parent.mkdir()
            tool.write_text("#!/bin/sh\n")
            tool.chmod(0o755)
            with patch("subprocess.check_output", return_value="0.9.0"):
                self.assertFalse(APP["installed_package_ready"](prefix, "pi", APP["PI_PACKAGE"], {}))
            with patch("subprocess.check_output", return_value="1.6.0") as check:
                self.assertTrue(APP["installed_package_ready"](prefix, "pi", APP["PI_PACKAGE"], {}))
                self.assertEqual(check.call_args.args[0], [str(tool), "--version"])
