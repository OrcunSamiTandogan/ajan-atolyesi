import json
import os
from pathlib import Path
import runpy
import tempfile
import unittest
from unittest.mock import patch

BRIDGE = runpy.run_path(str(Path(__file__).resolve().parents[1] / "bin/evren-dsh-terminal"))


class Source:
    def __init__(self, payload):
        self.payload = iter(payload)

    def read1(self, _n):
        return next(self.payload, b"")


class DshTests(unittest.TestCase):
    def test_sse_text_passes_and_tool_events_are_rejected(self):
        text = b'event: content_block_start\ndata: {"type":"content_block_start","content_block":{"type":"text","text":""}}\n\n'
        self.assertEqual(list(BRIDGE["safe_stream"](Source([text[:25], text[25:]]))), [text])
        event = b'data: {"type":"content_block_start","content_block":{"type":"tool_use"}}\n\n'
        with self.assertRaises(ValueError):
            list(BRIDGE["safe_stream"](Source([event])))

    def test_subprocess_gets_only_loopback_key(self):
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, {
            "NVIDIA_API_KEY": "never", "EVREN_API_KEY": "never",
            "DEEPSEEK_BASE_URL": "https://example.invalid", "HTTPS_PROXY": "https://example.invalid",
        }):
            env = BRIDGE["isolated_env"](Path(tmp), "local-dummy")
            self.assertEqual(env["DEEPSEEK_API_KEY"], "local-dummy")
            self.assertEqual(env["HOME"], tmp)
            self.assertNotIn("never", env.values())
            self.assertNotIn("HTTPS_PROXY", env)
            self.assertNotIn("DEEPSEEK_BASE_URL", env)
            self.assertEqual(env["DSH_TELEMETRY_DISABLED"], "1")

    def test_success_needs_completed_and_valid_session(self):
        base = {"type": "final", "sessionId": "session-case", "text": "ok"}
        self.assertEqual(BRIDGE["summary"]([{**base, "reason": {"kind": "completed"}}]), ("session-case", "ok"))
        self.assertEqual(BRIDGE["summary"]([{**base, "reason": {"kind": "failed"}}]), ("session-case", None))
        self.assertEqual(BRIDGE["summary"]([{**base, "reason": None}]), ("session-case", None))

    def test_only_official_loopback_handoff_is_accepted(self):
        token = "Abcd1234_5678-abcd"
        good = f"http://127.0.0.1:34567/?token={token}"
        self.assertEqual(BRIDGE["browser_url"]("dsh web: " + good), good)
        for wrong in (good.replace("127.0.0.1", "other.invalid"),
                      good.replace("34567", "65536"), good + "&redirect=https://other.invalid",
                      good.replace("/?token", "/other?token"), good.split("?")[0]):
            self.assertIsNone(BRIDGE["browser_url"]("dsh web: " + wrong))

    def test_official_web_uses_ephemeral_loopback_only(self):
        cmd = BRIDGE["web_command"]("/fake/dsh", Path("/tmp/patch"))
        self.assertEqual(cmd, ["/fake/dsh", "--profile", "web", "--patch", "/tmp/patch",
                               "--host", "127.0.0.1", "--port", "0", "--no-open"])
        cfg = BRIDGE["web_overlay"](34567, Path("/tmp/temporary session"))
        self.assertIn('documentsDirectory: "/tmp/temporary session/documents"', cfg)
        self.assertIn("plugins: []", cfg)
        self.assertIn("preset-ptc\n  disabled: true", cfg)

    def test_native_history_keeps_text_and_never_forwards_tools_or_thinking(self):
        history = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": [
                {"type": "thinking", "thinking": "not forwarded"},
                {"type": "text", "text": "Hello", "cache_control": {"type": "ephemeral"}},
            ]},
            {"role": "user", "content": [{"type": "text", "text": "Continue"}]},
        ]
        clean = BRIDGE["text_messages"](history)
        self.assertEqual(clean[1], {"role": "assistant", "content": [{"type": "text", "text": "Hello"}]})
        for kind in ("tool_result", "document", "image", "tool_use"):
            with self.assertRaises(ValueError):
                BRIDGE["text_messages"](history + [{"role": "user", "content": [{"type": kind}]}])


    def test_sdk_command_and_policy(self):
        args = BRIDGE["sdk_command"]("/fake/dsh", Path("/tmp/dsh.yml"))
        self.assertEqual(args, ["/fake/dsh", "--profile", "sdk-minimal", "--patch", "/tmp/dsh.yml"])
        cfg = BRIDGE["sdk_overlay"](23456, Path("/tmp/fixture"))
        self.assertIn('mode: read-only', cfg)
        self.assertIn('workspaceRoot: "/tmp/fixture"', cfg)
        self.assertIn('tool-fs\n  disabled: true', cfg)
        self.assertIn('persistent-bash\n  disabled: true', cfg)
        self.assertIn('persistent-pwsh\n  disabled: true', cfg)

    def test_usage_does_not_invent_missing_cache_counters(self):
        format_usage = BRIDGE["usage_line"]
        self.assertEqual(format_usage({}), "Cache/token sayaçları bildirilmedi.")
        self.assertEqual(format_usage({"outputTokens": 4}), "Çıkış: 4")
        self.assertEqual(format_usage({"cacheReadTokens": 0}), "Cache okuma: 0")
        self.assertEqual(format_usage({"cacheReadTokens": 2496}), "Cache okuma: 2,496")
