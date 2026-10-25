"""Real loopback integration checks. These are not evidence of Burp completion."""
import contextlib
import http.client
import json
import os
from pathlib import Path
import queue
import secrets
import socket
import subprocess
import sys
import threading
import unittest

sys.dont_write_bytecode = True
import lab


class LabTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workspace = lab.create_run("run/software-tests-" + secrets.token_hex(6))
        print("Software-test artifacts: " + str(cls.workspace), flush=True)

    def fresh(self):
        return lab.create_run("run/check-" + secrets.token_hex(5), self.workspace)

    @contextlib.contextmanager
    def running(self, mode="fixed", scenario="guided"):
        path = self.fresh()
        server = lab.LabServer(mode, scenario, 0, path)
        thread = threading.Thread(target=server.serve_forever, kwargs={"poll_interval": 0.02})
        thread.start()
        try:
            yield server, path
        finally:
            server.shutdown()
            thread.join(timeout=5)
            server.server_close()
            self.assertFalse(thread.is_alive())

    def request(self, server, path, cookie=None, method="GET", body=None, headers=None):
        fields = {"Host": server.host_header}
        if cookie:
            fields["Cookie"] = cookie
        fields.update(headers or {})
        with contextlib.closing(http.client.HTTPConnection(lab.HOST, server.server_port, timeout=4)) as conn:
            conn.request(method, path, body=body, headers=fields)
            response = conn.getresponse()
            data = response.read().decode("utf-8")
            return response.status, dict(response.getheaders()), data

    def login(self, server, account):
        status, headers, _ = self.request(server, "/session", method="POST", body="account=" + account,
                                          headers={"Origin": server.origin, "Content-Type": "application/x-www-form-urlencoded"})
        self.assertEqual(status, 303)
        self.assertEqual(headers["Location"], "/")
        self.assertIn("HttpOnly", headers["Set-Cookie"])
        self.assertIn("SameSite=Strict", headers["Set-Cookie"])
        return headers["Set-Cookie"].split(";", 1)[0]

    def raw(self, server, request):
        with socket.create_connection((lab.HOST, server.server_port), timeout=4) as client:
            client.sendall(request.encode("ascii"))
            chunks = []
            while True:
                chunk = client.recv(16384)
                if not chunk:
                    break
                chunks.append(chunk)
        response = b"".join(chunks).decode("utf-8")
        return int(response.split(" ", 2)[1]), response

    def test_both_modes_two_users_each_record_and_scenario(self):
        # Explicit expected ownership, independent from the server fixture lookup.
        expected = {"guided": {"101": "ada", "102": "ben", "103": "ada"},
                    "changed": {"101": "ben", "102": "ada", "103": "ben"}}
        for scenario, owners in expected.items():
            for mode in ("vulnerable", "fixed"):
                with self.subTest(mode=mode, scenario=scenario), self.running(mode, scenario) as (server, _):
                    self.assertEqual(server.server_address[0], "127.0.0.1")
                    for account in ("ada", "ben"):
                        cookie = self.login(server, account)
                        for oid, owner in owners.items():
                            status, headers, body = self.request(server, "/api/orders/" + oid, cookie)
                            self.assertEqual(status, 200 if mode == "vulnerable" or account == owner else 403)
                            self.assertEqual(headers["X-Lab-Mode"], mode)
                            self.assertEqual(headers["X-Lab-Scenario"], scenario)
                            self.assertEqual(headers["Cache-Control"], "no-store")
                            parsed = json.loads(body)
                            if status == 200:
                                self.assertEqual((parsed["id"], parsed["owner"]), (oid, owner))
                                self.assertTrue(parsed["synthetic"])
                            else:
                                self.assertEqual(set(parsed), {"error"})
                                self.assertNotIn("Fictional order", body)

    def test_home_links_are_filtered_in_both_modes(self):
        for mode in ("vulnerable", "fixed"):
            with self.running(mode) as (server, _):
                cookie = self.login(server, "ada")
                status, headers, body = self.request(server, "/", cookie)
                self.assertEqual(status, 200)
                self.assertIn('/api/orders/101', body)
                self.assertIn('/api/orders/103', body)
                self.assertNotIn('/api/orders/102', body)
                self.assertIn("not real authentication", body)
                self.assertIn("frame-ancestors 'none'", headers["Content-Security-Policy"])

    def test_missing_invalid_duplicate_and_stale_sessions(self):
        old_cookie = None
        with self.running() as (server, _):
            old_cookie = self.login(server, "ada")
            for cookie in (None, "lab_session=ada", "lab_session=bogus", old_cookie + "; " + old_cookie):
                with self.subTest(cookie_kind="absent" if cookie is None else "invalid"):
                    self.assertEqual(self.request(server, "/api/orders/101", cookie)[0], 401)
        with self.running() as (server, _):
            self.assertEqual(self.request(server, "/api/orders/101", old_cookie)[0], 401)

    def test_unknown_and_malformed_ids_have_distinct_outcomes(self):
        with self.running() as (server, _):
            cookie = self.login(server, "ada")
            self.assertEqual(self.request(server, "/api/orders/999", cookie)[0], 404)
            for suffix in ("abc", "010", "10", "1000", "-1", "101?owner=ada", "%31%30%31", "101/", "../101", ""):
                with self.subTest(suffix=suffix):
                    self.assertEqual(self.request(server, "/api/orders/" + suffix, cookie)[0], 400)
            for path in ("/lab.py", "/run/worksheet.md", "/../lab.py", "/%2e%2e/lab.py", "/session?account=ada"):
                self.assertEqual(self.request(server, path, cookie)[0], 404)

    def test_host_and_origin_boundaries(self):
        with self.running() as (server, _):
            for host in ("localhost:" + str(server.server_port), "attacker.test", "127.0.0.1", "0.0.0.0:8765"):
                self.assertEqual(self.request(server, "/", headers={"Host": host})[0], 421)
            for origin in ("null", "https://attacker.test", "http://127.0.0.1:1"):
                self.assertEqual(self.request(server, "/", headers={"Origin": origin})[0], 403)
            self.assertEqual(self.request(server, "/", headers={"Origin": server.origin})[0], 200)
            for headers in ("", "Host: " + server.host_header + "\r\nHost: " + server.host_header + "\r\n"):
                self.assertEqual(self.raw(server, "GET / HTTP/1.1\r\n" + headers + "\r\n")[0], 421)

    def test_http_framing_and_unsupported_methods(self):
        with self.running() as (server, _):
            for headers in ("Transfer-Encoding: chunked\r\n", "Content-Length: 1\r\nContent-Length: 1\r\n",
                            "Content-Length: -1\r\n", "Content-Length: 1\r\n", "Cookie: a=b\r\nCookie: c=d\r\n"):
                status, _ = self.raw(server, "GET / HTTP/1.1\r\nHost: " + server.host_header + "\r\n" + headers + "\r\n")
                self.assertEqual(status, 400)
            self.assertEqual(self.raw(server, "GET http://attacker.test/ HTTP/1.1\r\nHost: " + server.host_header + "\r\n\r\n")[0], 400)
            for method in ("PUT", "DELETE", "PATCH", "OPTIONS", "TRACE"):
                self.assertEqual(self.request(server, "/", method=method)[0], 405)

    def test_session_form_validation(self):
        with self.running() as (server, _):
            good = {"Origin": server.origin, "Content-Type": "application/x-www-form-urlencoded"}
            for body in ("account=unknown", "account=", "account=ada&account=ben", "account=ada&extra=yes", "broken", "account=%FF"):
                self.assertEqual(self.request(server, "/session", method="POST", body=body, headers=good)[0], 400)
            self.assertEqual(self.request(server, "/session", method="POST", body="account=ada", headers={"Content-Type": good["Content-Type"]})[0], 403)
            self.assertEqual(self.request(server, "/session", method="POST", body="account=ada", headers={"Origin": server.origin})[0], 415)
            self.assertEqual(self.request(server, "/session", method="POST", body="a" * 129, headers=good)[0], 413)
            request = "POST /session HTTP/1.1\r\nHost: " + server.host_header + "\r\nOrigin: " + server.origin + "\r\nContent-Type: application/x-www-form-urlencoded\r\n\r\n"
            self.assertEqual(self.raw(server, request)[0], 411)

    def test_event_evidence_contains_no_session_tokens(self):
        with self.running("vulnerable") as (server, path):
            cookie = self.login(server, "ada")
            self.request(server, "/api/orders/102", cookie)
        text = (path / "events.jsonl").read_text(encoding="utf-8")
        self.assertNotIn(cookie.split("=", 1)[1], text)
        last = json.loads(text.splitlines()[-1])
        self.assertEqual((last["mode"], last["account"], last["object_id"], last["status"]),
                         ("vulnerable", "ada", "102", 200))

    def test_fresh_run_rejects_existing_escape_absolute_and_reserved_names(self):
        folder = lab.create_run("run/fresh", self.workspace)
        marker = folder / "keep.txt"
        marker.write_text("preserve", encoding="utf-8")
        with self.assertRaises(FileExistsError):
            lab.create_run("run/fresh", self.workspace)
        self.assertEqual(marker.read_text(encoding="utf-8"), "preserve")
        for value in ("run", "run/../escape", "run/a/b", "../escape", "/tmp/escape", "C:\\escape", "run/CON", "run/name."):
            with self.subTest(value=value), self.assertRaises(ValueError):
                lab.create_run(value, self.workspace)

    def test_linked_output_paths_are_refused(self):
        target = self.workspace / "link-target"
        target.mkdir()
        link = self.workspace / "run" / "linked"
        try:
            os.symlink(target, link, target_is_directory=True)
        except (OSError, NotImplementedError):
            if os.name != "nt":
                self.skipTest("Host cannot create symlinks")
            # Junctions usually do not require Windows developer mode.
            script = "New-Item -ItemType Junction -Path '" + str(link).replace("'", "''") + "' -Target '" + str(target).replace("'", "''") + "' | Out-Null"
            result = subprocess.run(["powershell.exe", "-NoProfile", "-Command", script], capture_output=True, text=True)
            if result.returncode:
                self.skipTest("Host cannot create test symlink or junction")
        with self.assertRaises(ValueError):
            lab.create_run("run/linked", self.workspace)
        with self.assertRaises(ValueError):
            lab.create_run("run/child", link)
        self.assertEqual(list(target.iterdir()), [])

    def test_server_configuration_rejects_bad_values(self):
        for mode, scenario, port in (("other", "guided", 0), ("fixed", "other", 0), ("fixed", "guided", -1),
                                     ("fixed", "guided", 80), ("fixed", "guided", 65536)):
            with self.assertRaises(ValueError):
                lab.LabServer(mode, scenario, port, self.fresh())

    def test_maintained_cli_help_cases_and_argument_boundaries(self):
        for args in (["--help"], ["serve", "--help"], ["cases"]):
            result = subprocess.run([sys.executable, "-B", str(lab.ROOT / "lab.py"), *args], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
        for args in (["serve", "--mode", "fixed", "--out", "run/invalid", "--port", "0"],
                     ["serve", "--mode", "fixed", "--out", "../outside"],
                     ["serve", "--mode", "fixed", "--out", "run/invalid", "--host", "0.0.0.0"]):
            result = subprocess.run([sys.executable, "-B", str(lab.ROOT / "lab.py"), *args], capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
        self.assertFalse((lab.ROOT / "run" / "invalid").exists())

    def test_cli_serve_creates_worksheet_and_socket_closes_on_process_stop(self):
        # Reserve an available loopback port briefly; no fixed service is displaced.
        with socket.socket() as probe:
            probe.bind(("127.0.0.1", 0))
            port = probe.getsockname()[1]
        name = "run/cli-smoke-" + secrets.token_hex(6)
        proc = subprocess.Popen([sys.executable, "-B", str(lab.ROOT / "lab.py"), "serve",
                                 "--mode", "fixed", "--scenario", "guided", "--out", name,
                                 "--port", str(port)], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                text=True, cwd=self.workspace)
        lines = queue.Queue()
        reader = threading.Thread(target=lambda: lines.put(proc.stdout.readline()), daemon=True)
        reader.start()
        try:
            info = json.loads(lines.get(timeout=6))
            self.assertEqual(info["url"], "http://127.0.0.1:" + str(port) + "/")
            self.assertEqual(info["manual_burp_completion"], "pending")
            folder = lab.ROOT / name
            self.assertEqual(set(p.name for p in folder.iterdir()),
                             {"run.json", "roster.json", "worksheet.md", "events.jsonl"})
            self.assertIn("pending hands-on completion", (folder / "worksheet.md").read_text(encoding="utf-8"))
            with contextlib.closing(http.client.HTTPConnection("127.0.0.1", port, timeout=3)) as connection:
                connection.request("GET", "/")
                response = connection.getresponse()
                self.assertEqual(response.status, 200)
                self.assertIn("FIXED", response.read().decode("utf-8"))
        finally:
            proc.terminate()
            proc.wait(timeout=5)
            reader.join(timeout=2)
            proc.stdout.close()
            proc.stderr.close()
        with socket.socket() as probe:
            probe.settimeout(2)
            self.assertNotEqual(probe.connect_ex(("127.0.0.1", port)), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
