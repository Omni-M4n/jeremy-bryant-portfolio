"""Local practice app: authenticate a user, then scope every note query to them."""

import hashlib
import secrets
import sqlite3
import time
from pathlib import Path

from flask import Flask, abort, g, redirect, render_template, request, url_for
from werkzeug.exceptions import SecurityError
from werkzeug.security import check_password_hash, generate_password_hash

ORIGIN = "http://127.0.0.1:5071"
COOKIE = "access_notes_session"
SESSION_SECONDS = 3600
DEMO_USERS = (("alex", "Alex-demo-47!"), ("sam", "Sam-demo-82!"))


def create_app(database=None):
    app = Flask(__name__)
    app.config.update(
        DATABASE=str(database or Path(app.root_path) / "instance" / "notes.sqlite3"),
        TRUSTED_HOSTS=["127.0.0.1"],
        MAX_CONTENT_LENGTH=65536,
        MAX_FORM_MEMORY_SIZE=65536,
        MAX_FORM_PARTS=8,
    )

    def db():
        if "db" not in g:
            g.db = sqlite3.connect(app.config["DATABASE"])
            g.db.row_factory = sqlite3.Row
            g.db.execute("PRAGMA foreign_keys = ON")
        return g.db

    @app.teardown_appcontext
    def close_db(error=None):
        connection = g.pop("db", None)
        if connection is not None:
            connection.close()

    def issue_session(user_id=None):
        token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        csrf = secrets.token_urlsafe(32)
        now = int(time.time())
        db().execute("DELETE FROM sessions WHERE expires_at <= ?", (now,))
        db().execute(
            "INSERT INTO sessions (token_hash, user_id, csrf, expires_at) VALUES (?, ?, ?, ?)",
            (token_hash, user_id, csrf, now + SESSION_SECONDS),
        )
        db().commit()
        return token, csrf

    def set_session_cookie(response, token):
        # shortcut: HTTP cookie is for loopback practice; hosted use requires HTTPS.
        response.set_cookie(
            COOKIE, token, max_age=SESSION_SECONDS, httponly=True,
            samesite="Strict", secure=False, path="/",
        )
        return response

    @app.before_request
    def check_request():
        if request.host_url.rstrip("/") != ORIGIN:
            abort(400, "Open the app at http://127.0.0.1:5071.")
        g.login_session = None
        g.user = None
        token = request.cookies.get(COOKIE, "")
        if len(token) == 43:
            token_hash = hashlib.sha256(token.encode()).hexdigest()
            g.login_session = db().execute(
                "SELECT * FROM sessions WHERE token_hash = ? AND expires_at > ?",
                (token_hash, int(time.time())),
            ).fetchone()
            if g.login_session and g.login_session["user_id"] is not None:
                g.user = db().execute(
                    "SELECT id, username FROM users WHERE id = ?",
                    (g.login_session["user_id"],),
                ).fetchone()
        if request.method == "POST":
            if request.headers.get("Origin") != ORIGIN:
                abort(403, "A same-origin form submission is required.")
            supplied = request.form.get("csrf_token", "")
            if (
                not g.login_session or len(supplied) != 43 or not supplied.isascii()
                or not secrets.compare_digest(supplied, g.login_session["csrf"])
            ):
                abort(403, "The form expired. Reload the page and try again.")

    @app.after_request
    def security_headers(response):
        response.headers["Cache-Control"] = "no-store"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; script-src 'none'; style-src 'self'; "
            "base-uri 'none'; form-action 'self'; frame-ancestors 'none'"
        )
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "same-origin"
        return response

    @app.context_processor
    def form_context():
        login_session = g.get("login_session")
        return {"csrf": login_session["csrf"] if login_session else ""}

    def require_user():
        if g.user is None:
            abort(401, "Sign in to access your notes.")

    def owned_note(note_id):
        require_user()
        if note_id > 2**63 - 1:
            abort(404, "Note not found.")
        note = db().execute(
            "SELECT * FROM notes WHERE id = ? AND owner_id = ?",
            (note_id, g.user["id"]),
        ).fetchone()
        if note is None:
            abort(404, "Note not found.")
        return note

    def note_fields():
        title = request.form.get("title", "").strip()
        body = request.form.get("body", "").strip()
        if not 1 <= len(title) <= 80 or not 1 <= len(body) <= 4000:
            abort(400, "Use a title of 1–80 characters and a note of 1–4,000 characters.")
        return title, body

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if g.user is not None:
            return redirect(url_for("notes"), code=303)
        if request.method == "GET":
            if g.login_session:
                return render_template("login.html", csrf=g.login_session["csrf"])
            token, csrf = issue_session()
            return set_session_cookie(app.make_response(render_template("login.html", csrf=csrf)), token)
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = db().execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone() if len(username) <= 40 else None
        password_valid = len(password) <= 128 and check_password_hash(
            user["password_hash"] if user else app.config["DUMMY_HASH"], password
        )
        if user is None or not password_valid:
            return render_template(
                "login.html", csrf=g.login_session["csrf"], error="Username or password was not recognised."
            ), 401
        db().execute("DELETE FROM sessions WHERE token_hash = ?", (g.login_session["token_hash"],))
        token, csrf = issue_session(user["id"])
        return set_session_cookie(redirect(url_for("notes"), code=303), token)

    @app.post("/logout")
    def logout():
        db().execute("DELETE FROM sessions WHERE token_hash = ?", (g.login_session["token_hash"],))
        db().commit()
        response = redirect(url_for("login"), code=303)
        response.delete_cookie(COOKIE, path="/", httponly=True, samesite="Strict")
        return response

    @app.get("/")
    def notes():
        if g.user is None:
            return redirect(url_for("login"), code=303)
        rows = db().execute(
            "SELECT id, title FROM notes WHERE owner_id = ? ORDER BY id DESC",
            (g.user["id"],),
        ).fetchall()
        return render_template("notes.html", notes=rows, csrf=g.login_session["csrf"])

    @app.post("/notes")
    def create_note():
        require_user()
        title, body = note_fields()
        count = db().execute("SELECT count(*) FROM notes WHERE owner_id = ?", (g.user["id"],)).fetchone()[0]
        if count >= 200:
            abort(400, "The local practice limit is 200 notes per user.")
        cursor = db().execute(
            "INSERT INTO notes (owner_id, title, body) VALUES (?, ?, ?)",
            (g.user["id"], title, body),
        )
        db().commit()
        return redirect(url_for("note", note_id=cursor.lastrowid), code=303)

    @app.route("/notes/<int:note_id>", methods=["GET", "POST"])
    def note(note_id):
        row = owned_note(note_id)
        if request.method == "POST":
            title, body = note_fields()
            db().execute(
                "UPDATE notes SET title = ?, body = ? WHERE id = ? AND owner_id = ?",
                (title, body, note_id, g.user["id"]),
            )
            db().commit()
            return redirect(url_for("note", note_id=note_id), code=303)
        return render_template("note.html", note=row, csrf=g.login_session["csrf"])

    @app.post("/notes/<int:note_id>/delete")
    def delete_note(note_id):
        owned_note(note_id)
        db().execute("DELETE FROM notes WHERE id = ? AND owner_id = ?", (note_id, g.user["id"]))
        db().commit()
        return redirect(url_for("notes"), code=303)

    @app.errorhandler(400)
    @app.errorhandler(401)
    @app.errorhandler(403)
    @app.errorhandler(404)
    @app.errorhandler(413)
    def show_error(error):
        if isinstance(error, SecurityError):
            return error.get_response()
        return render_template("error.html", error=error), error.code

    Path(app.config["DATABASE"]).parent.mkdir(parents=True, exist_ok=True)
    with app.app_context():
        db().executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY, username TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS sessions (
                token_hash TEXT PRIMARY KEY, user_id INTEGER REFERENCES users(id),
                csrf TEXT NOT NULL, expires_at INTEGER NOT NULL
            );
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY, owner_id INTEGER NOT NULL REFERENCES users(id),
                title TEXT NOT NULL, body TEXT NOT NULL
            );
        """)
        for username, password in DEMO_USERS:
            if db().execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone():
                continue
            cursor = db().execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (username, generate_password_hash(password)),
            )
            db().execute(
                "INSERT INTO notes (owner_id, title, body) VALUES (?, ?, ?)",
                (cursor.lastrowid, f"{username.title()}'s first note", "Fictional practice data. Try switching accounts to check who can see this note."),
            )
        db().commit()
    app.config["DUMMY_HASH"] = generate_password_hash(secrets.token_urlsafe(32))
    return app


if __name__ == "__main__":
    create_app().run(host="127.0.0.1", port=5071, debug=False, use_reloader=False)
