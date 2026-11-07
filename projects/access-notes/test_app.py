"""Run with: python -m unittest -v"""

import hashlib
import html
import re
import sqlite3
import tempfile
import time
import unittest
from contextlib import closing
from pathlib import Path

from app import COOKIE, DEMO_USERS, ORIGIN, create_app


class AccessNotesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.database = Path(cls.temp.name) / "test.sqlite3"
        cls.app = create_app(cls.database)
        cls.app.config["TESTING"] = True

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def setUp(self):
        self.client = self.app.test_client()
        with closing(sqlite3.connect(self.database, isolation_level=None)) as connection:
            connection.execute("DELETE FROM sessions")
            connection.execute("DELETE FROM notes")
            connection.executemany(
                "INSERT INTO notes (id, owner_id, title, body) VALUES (?, ?, ?, ?)",
                ((1, 1, "Alex private", "Alex only"), (2, 2, "Sam private", "Sam only")),
            )

    def get(self, path, client=None):
        return (client or self.client).get(path, base_url=ORIGIN)

    def csrf(self, response):
        return re.search(r'name="csrf_token" value="([^"]+)"', response.get_data(as_text=True))[1]

    def post(self, path, data, client=None, origin=ORIGIN):
        headers = {"Origin": origin} if origin else {}
        return (client or self.client).post(path, data=data, headers=headers, base_url=ORIGIN)

    def login(self, username="alex", client=None):
        csrf = self.csrf(self.get("/login", client))
        passwords = dict(DEMO_USERS)
        response = self.post("/login", {
            "csrf_token": csrf, "username": username, "password": passwords[username]
        }, client)
        self.assertEqual(response.status_code, 303)
        return self.csrf(self.get("/", client))

    def test_signed_out_cannot_read_or_write_notes(self):
        self.assertEqual(self.get("/").status_code, 303)
        self.assertEqual(self.get("/notes/1").status_code, 401)
        csrf = self.csrf(self.get("/login"))
        self.assertEqual(self.post("/notes", {"csrf_token": csrf, "title": "No", "body": "No"}).status_code, 401)

    def test_each_user_sees_only_their_own_notes(self):
        self.login()
        page = self.get("/").get_data(as_text=True)
        self.assertIn("Alex private", page)
        self.assertNotIn("Sam private", page)
        other = self.app.test_client()
        self.login("sam", other)
        page = self.get("/", other).get_data(as_text=True)
        self.assertIn("Sam private", page)
        self.assertNotIn("Alex private", page)

    def test_other_users_note_id_denied_for_read_edit_and_delete(self):
        csrf = self.login()
        self.assertEqual(self.get("/notes/2").status_code, 404)
        self.assertEqual(self.get("/notes/999").status_code, 404)
        self.assertEqual(self.post("/notes/2", {"csrf_token": csrf, "title": "Taken", "body": "Taken"}).status_code, 404)
        self.assertEqual(self.post("/notes/2/delete", {"csrf_token": csrf}).status_code, 404)
        with closing(sqlite3.connect(self.database, isolation_level=None)) as connection:
            self.assertEqual(connection.execute("SELECT title, body FROM notes WHERE id = 2").fetchone(), ("Sam private", "Sam only"))

    def test_forged_owner_is_ignored_on_create_and_update(self):
        csrf = self.login()
        response = self.post("/notes", {"csrf_token": csrf, "title": "Mine", "body": "Mine", "owner_id": "2", "user_id": "2"})
        self.assertEqual(response.status_code, 303)
        note_url = response.headers["Location"]
        self.assertEqual(self.post(note_url, {"csrf_token": csrf, "title": "Still mine", "body": "Still mine", "owner_id": "2"}).status_code, 303)
        with closing(sqlite3.connect(self.database, isolation_level=None)) as connection:
            self.assertEqual(connection.execute("SELECT owner_id FROM notes WHERE title = ?", ("Still mine",)).fetchone()[0], 1)
        other = self.app.test_client()
        self.login("sam", other)
        self.assertEqual(self.get(note_url, other).status_code, 404)

    def test_owner_can_create_edit_and_delete(self):
        csrf = self.login()
        response = self.post("/notes", {"csrf_token": csrf, "title": "New thought", "body": "First draft"})
        url = response.headers["Location"]
        self.assertIn("First draft", self.get(url).get_data(as_text=True))
        self.assertEqual(self.post(url, {"csrf_token": csrf, "title": "Revised", "body": "Second draft"}).status_code, 303)
        self.assertIn("Second draft", self.get(url).get_data(as_text=True))
        self.assertEqual(self.post(url + "/delete", {"csrf_token": csrf}).status_code, 303)
        self.assertEqual(self.get(url).status_code, 404)

    def test_csrf_required_for_login_create_edit_delete_logout(self):
        self.get("/login")
        self.assertEqual(self.post("/login", {"username": "alex", "password": dict(DEMO_USERS)["alex"]}).status_code, 403)
        self.login()
        for path in ("/notes", "/notes/1", "/notes/1/delete", "/logout"):
            with self.subTest(path=path):
                self.assertEqual(self.post(path, {"title": "No", "body": "No"}).status_code, 403)
                self.assertEqual(self.post(path, {"csrf_token": "wrong", "title": "No", "body": "No"}).status_code, 403)
        self.assertEqual(self.get("/notes/1").status_code, 200)

    def test_csrf_from_another_session_is_rejected(self):
        self.login()
        other = self.app.test_client()
        other_csrf = self.login("sam", other)
        self.assertEqual(self.post("/logout", {"csrf_token": other_csrf}).status_code, 403)

    def test_malformed_csrf_is_rejected_without_server_error(self):
        self.get("/login")
        for csrf in ("é", "é" * 43, "a" * 44):
            self.assertEqual(self.post("/login", {"csrf_token": csrf}).status_code, 403)
        self.login()
        self.assertEqual(self.post("/logout", {"csrf_token": "é" * 43}).status_code, 403)

    def test_out_of_range_note_ids_return_not_found(self):
        csrf = self.login()
        for note_id in ("9223372036854775808", "9" * 300):
            url = "/notes/" + note_id
            self.assertEqual(self.get(url).status_code, 404)
            self.assertEqual(self.post(url, {"csrf_token": csrf, "title": "No", "body": "No"}).status_code, 404)
            self.assertEqual(self.post(url + "/delete", {"csrf_token": csrf}).status_code, 404)

    def test_logout_revokes_cookie_even_if_replayed(self):
        csrf = self.login()
        old_cookie = self.client.get_cookie(COOKIE, domain="127.0.0.1").value
        self.assertEqual(self.post("/logout", {"csrf_token": csrf}).status_code, 303)
        replay = self.app.test_client()
        replay.set_cookie(COOKIE, old_cookie, domain="127.0.0.1")
        self.assertEqual(self.get("/notes/1", replay).status_code, 401)
        with closing(sqlite3.connect(self.database, isolation_level=None)) as connection:
            self.assertIsNone(connection.execute("SELECT 1 FROM sessions WHERE token_hash = ?", (hashlib.sha256(old_cookie.encode()).hexdigest(),)).fetchone())

    def test_login_rotates_and_revokes_anonymous_cookie(self):
        page = self.get("/login")
        old_cookie = self.client.get_cookie(COOKIE, domain="127.0.0.1").value
        response = self.post("/login", {"csrf_token": self.csrf(page), "username": "alex", "password": dict(DEMO_USERS)["alex"]})
        new_cookie = self.client.get_cookie(COOKIE, domain="127.0.0.1").value
        self.assertNotEqual(old_cookie, new_cookie)
        self.assertIn("HttpOnly", response.headers["Set-Cookie"])
        self.assertIn("SameSite=Strict", response.headers["Set-Cookie"])
        self.client.set_cookie(COOKIE, old_cookie, domain="127.0.0.1")
        self.assertEqual(self.get("/notes/1").status_code, 401)

    def test_expired_session_is_denied(self):
        self.login()
        with closing(sqlite3.connect(self.database, isolation_level=None)) as connection:
            connection.execute("UPDATE sessions SET expires_at = ?", (int(time.time()) - 1,))
        self.assertEqual(self.get("/notes/1").status_code, 401)

    def test_html_is_escaped_in_title_attribute_and_body(self):
        csrf = self.login()
        title = '\"><script>alert(1)</script>'
        body = '</textarea><img src=x onerror="alert(1)">'
        response = self.post("/notes", {"csrf_token": csrf, "title": title, "body": body})
        page = self.get(response.headers["Location"]).get_data(as_text=True)
        self.assertIn(html.escape(title).replace("&quot;", "&#34;").replace("&#x27;", "&#39;"), page)
        self.assertIn(html.escape(body).replace("&quot;", "&#34;").replace("&#x27;", "&#39;"), page)
        self.assertNotIn("<script>", page)
        self.assertNotIn("<img", page)

    def test_sql_injection_is_data_and_cannot_log_in(self):
        csrf = self.csrf(self.get("/login"))
        payload = "' OR 1=1 --"
        self.assertEqual(self.post("/login", {"csrf_token": csrf, "username": payload, "password": "wrong"}).status_code, 401)
        csrf = self.login()
        response = self.post("/notes", {"csrf_token": csrf, "title": payload, "body": "'); DROP TABLE notes; --"})
        self.assertEqual(response.status_code, 303)
        with closing(sqlite3.connect(self.database, isolation_level=None)) as connection:
            self.assertEqual(connection.execute("SELECT count(*) FROM notes").fetchone()[0], 3)
            self.assertEqual(connection.execute("SELECT title FROM notes ORDER BY id DESC").fetchone()[0], payload)

    def test_host_and_origin_are_restricted(self):
        self.assertEqual(self.client.get("/login", base_url="http://evil.example:5071").status_code, 400)
        self.assertEqual(self.client.get("/login", base_url="http://127.0.0.1:9999").status_code, 400)
        csrf = self.csrf(self.get("/login"))
        for origin in ("https://evil.example", "null", None):
            self.assertEqual(self.post("/login", {"csrf_token": csrf, "username": "alex", "password": dict(DEMO_USERS)["alex"]}, origin=origin).status_code, 403)

    def test_body_and_field_bounds(self):
        csrf = self.login()
        for title, body in (("", "Body"), ("x" * 81, "Body"), ("Title", "x" * 4001)):
            self.assertEqual(self.post("/notes", {"csrf_token": csrf, "title": title, "body": body}).status_code, 400)
        self.assertEqual(self.post("/notes", {"csrf_token": csrf, "title": "Large", "body": "x" * 70000}).status_code, 413)

    def test_passwords_are_hashed_and_security_headers_present(self):
        with closing(sqlite3.connect(self.database, isolation_level=None)) as connection:
            password_hash = connection.execute("SELECT password_hash FROM users WHERE username = ?", ("alex",)).fetchone()[0]
        self.assertNotEqual(password_hash, dict(DEMO_USERS)["alex"])
        self.assertTrue(password_hash.startswith("scrypt:"))
        response = self.get("/login")
        self.assertEqual(response.headers["Cache-Control"], "no-store")
        self.assertIn("script-src 'none'", response.headers["Content-Security-Policy"])
        self.assertEqual(response.headers["X-Frame-Options"], "DENY")
        self.assertEqual(response.headers["Referrer-Policy"], "same-origin")


if __name__ == "__main__":
    unittest.main()
