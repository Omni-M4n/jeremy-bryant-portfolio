"""Behavior checks, including real loopback HTTP. No packet capture claim."""
import contextlib
import io
import json
from pathlib import Path
import socket
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import lab


class TrafficTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.root_patch = patch.object(lab, "ROOT", self.root)
        self.root_patch.start()

    def tearDown(self):
        self.root_patch.stop()
        self.temp.cleanup()

    def test_actual_loopback_statuses_and_no_capture(self):
        with contextlib.redirect_stdout(io.StringIO()):
            results, setup = lab.run_experiment("run/real", "guided", False)
        self.assertEqual([row["status"] for row in results[:3]], [200, 404, 200])
        self.assertEqual(results[-1]["outcome"], "connection_refused")
        self.assertIsNone(results[-1]["http_response"])
        self.assertEqual(setup["host"], "127.0.0.1")
        self.assertNotEqual(setup["http_port"], setup["non_listening_port"])
        self.assertFalse(list((self.root / "run/real").glob("*.pcap*")))
        self.assertEqual(len(json.loads((self.root / "run/real/server-log.json").read_text())["requests"]), 3)
        with socket.socket() as sock:
            self.assertNotEqual(sock.connect_ex(("127.0.0.1", setup["http_port"])), 0)

    def test_changed_query_does_not_decide_status(self):
        self.assertEqual(lab.response_for("/hello?note=missing")[0], 200)
        self.assertEqual(lab.response_for("/missing?note=hello")[0], 404)
        self.assertEqual(lab.response_for("/hello/")[0], 404)
        self.assertEqual(lab.response_for("/HELLO")[0], 404)

    def test_fresh_output_boundary_and_preservation(self):
        for bad in ("../escape", "run/../escape", "run", "run/a/b", "/tmp/escape", "run/con", "run/x:y"):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                lab.fresh_run(bad)
        out = lab.fresh_run("run/kept")
        lab.write_new(out / "note.txt", "original")
        with self.assertRaises(ValueError):
            lab.fresh_run("run/kept")
        with self.assertRaises(FileExistsError):
            lab.write_new(out / "note.txt", "changed")
        self.assertEqual((out / "note.txt").read_text(), "original")

    def test_linked_run_refused(self):
        target = self.root / "destination"
        target.mkdir()
        try:
            (self.root / "run").symlink_to(target, target_is_directory=True)
        except OSError as error:
            self.skipTest(f"symlink creation unavailable: {error}")
        with self.assertRaises(ValueError):
            lab.fresh_run("run/escaped")

    def test_invalid_case_has_no_side_effect(self):
        with self.assertRaises(ValueError):
            lab.run_experiment("run/bad", "unknown", False)
        self.assertFalse((self.root / "run").exists())

    def test_windows_reparse_attribute_refused(self):
        run = self.root / "run"
        run.mkdir()
        original = Path.lstat
        def metadata(path, *args, **kwargs):
            info = original(path, *args, **kwargs)
            return SimpleNamespace(st_mode=info.st_mode, st_file_attributes=0x400) if path == run else info
        with patch.object(Path, "lstat", metadata), self.assertRaises(ValueError):
            lab.fresh_run("run/escaped")

    def test_no_target_argument(self):
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            lab.main(["run", "--out", "run/x", "--host", "192.0.2.1"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
