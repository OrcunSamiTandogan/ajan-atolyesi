"""Local TCP + actual dsh 0.2.2-rc.5, fake upstream and credentials only."""
from http.server import ThreadingHTTPServer
import io
import json
from pathlib import Path
import runpy
import shutil
import subprocess
import tempfile
from threading import Thread
from urllib.error import HTTPError
from urllib.request import Request, urlopen

bridge = runpy.run_path(str(Path(__file__).resolve().parents[1] / "bin/evren-dsh-terminal"))
model = bridge["MODEL"]
seen = []
errors = []


def request(req, timeout):
    body = json.loads(req.data)
    assert req.full_url == bridge["ENDPOINT"]
    assert req.get_header("Authorization") == "Bearer fake-upstream"
    assert body["model"] == model and body["stream"]
    assert "tools" not in body and "tool_choice" not in body and "system" not in body
    assert "local-dummy" not in str(req.headers) + str(req.data)
    seen.append(body["messages"])
    events = [
        ("message_start", {"message": {"id": "msg_test", "type": "message", "model": model, "role": "assistant",
                                       "content": [], "stop_reason": None, "stop_sequence": None,
                                       "usage": {"input_tokens": 15, "output_tokens": 1}}}),
        ("content_block_start", {"index": 0, "content_block": {"type": "text", "text": ""}}),
        ("content_block_delta", {"index": 0, "delta": {"type": "text_delta", "text": "EVRENMOCK"}}),
        ("content_block_stop", {"index": 0}),
        ("message_delta", {"delta": {"stop_reason": "end_turn", "stop_sequence": None}, "usage": {"output_tokens": 5, "cache_read_input_tokens": 17 if len(seen) % 2 == 0 else 0}}),
        ("message_stop", {})
    ]

    class Reply(io.BytesIO):
        headers = {"Content-Type": "text/event-stream", "X-Evren-Routed-Model": bridge["ROUTED_MODEL"]}
    return Reply("".join(f"event: {kind}\ndata: {json.dumps({'type': kind, **v})}\n\n"
                         for kind, v in events).encode())


runner = shutil.which("dsh")
assert runner, "Install pinned dsh for this integration test."
with ThreadingHTTPServer(("127.0.0.1", 0), bridge["bridge_handler"](
        "fake-upstream", "local-dummy", errors.append, request)) as server:
    Thread(target=server.serve_forever, daemon=True).start()
    url = f"http://127.0.0.1:{server.server_port}/v1/messages"
    for key, path, model_id, code in [
        ("wrong", "", model, 401),
        ("local-dummy", "/../", model, 404),
        ("local-dummy", "", "another-model", 400),
    ]:
        try:
            urlopen(Request(url + path, data=json.dumps({"model": model_id}).encode(),
                            headers={"Authorization": "Bearer " + key}), timeout=2)
            raise AssertionError("invalid request reached handler as valid")
        except HTTPError as e:
            assert e.code == code
    errors.clear()
    assert not seen
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        patch_path = root / "dsh.yml"
        patch_path.write_text(bridge["overlay"](server.server_port))
        env = bridge["isolated_env"](root, "local-dummy")
        session = None
        for index in range(2):
            rc, events = bridge["run_turn"](runner, patch_path, root, env, f"Görev {index + 1}", session)
            new_id, answer = bridge["summary"](events)
            if rc or not new_id or answer != "EVRENMOCK" or errors:
                raise AssertionError(f"rc={rc} kinds={[e.get('type') for e in events]} has_id={bool(new_id)} correct={answer=='EVRENMOCK'} bridge_errors={errors} upstream={len(seen)}")
            session = new_id
        assert len(seen) == 2 and "Görev 1" in json.dumps(seen[1], ensure_ascii=False)
        seen.clear()
        sdk_root = root / "sdk-only"
        sdk_root.mkdir()
        patch_path.write_text(bridge["sdk_overlay"](server.server_port, sdk_root))
        with subprocess.Popen(bridge["sdk_command"](runner, patch_path), cwd=sdk_root,
                              env=bridge["isolated_env"](sdk_root, "local-dummy"),
                              stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True) as child:
            try:
                cli = bridge["HarnessSdk"](child, sdk_root)
                cli.initialize()
                sid = cli.session
                for index in range(2):
                    lines = []
                    stats, failed = cli.turn(f"SDK görev {index + 1}", lines.append)
                    assert not failed and lines == ["EVRENMOCK"], (stats, failed, lines, errors)
                    assert cli.session == sid and child.poll() is None
                    assert stats.get("cacheReadTokens") == (17 if index == 1 else 0), stats
                assert len(seen) == 2 and "SDK görev 1" in json.dumps(seen[1], ensure_ascii=False)
                cli.request("shutdown", {}, seconds=6)
            finally:
                child.terminate()
    server.shutdown()
print("actual dsh headless and persistent SDK + loopback relay + fake upstream: two turns each, correct model, filtered credentials, rejected wrong target/pass.")
