from contextlib import redirect_stdout, redirect_stderr
from io import BytesIO, StringIO
from pathlib import Path
import runpy
import unittest

APP = runpy.run_path(str(Path(__file__).resolve().parents[1] / "bin/evren-baglanti-kontrol"))


class EvrenCheckTests(unittest.TestCase):
    def test_fixed_host_and_no_key_in_output(self):
        key = "evren_mock_key"

        class FakeOpener:
            def open(self, request, timeout):
                assert request.full_url == "https://evren-llmapi.ssyz.org.tr/v1/models"
                assert request.get_method() == "GET"
                assert request.get_header("Authorization") == "Bearer " + key
                assert timeout == 10
                return BytesIO(b'{"data":[{"id":"deepseek-v4.1-flash"}]}')

        with redirect_stdout(StringIO()) as stdout, redirect_stderr(StringIO()) as stderr:
            self.assertEqual(APP["check_model"](key, FakeOpener()), 0)
        self.assertNotIn(key, stdout.getvalue() + stderr.getvalue())
        self.assertIsNone(APP["NoRedirect"]().redirect_request(None, None, 302, "", {}, "https://example.org"))

    def test_invalid_token_rejected_before_network(self):
        with redirect_stderr(StringIO()):
            self.assertEqual(APP["check_model"]("a\nb", object()), 2)
