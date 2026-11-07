# Access Notes

A small local Flask application for practising authentication, object ownership and security regression tests. Two fictional users each have a private notebook. Users can create, read, edit and delete their own notes.

This is a prepared personal practice project. Independent implementation and explanation exercises are pending; the files alone do not establish that the learner has mastered these controls. Start with [PRACTICE.md](PRACTICE.md), then use [INTERVIEW.md](INTERVIEW.md) to prepare an honest explanation.

## Run locally

Use Python 3.11 or newer. From this directory in PowerShell:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m unittest -v
.\.venv\Scripts\python.exe app.py
```

Open [Access Notes on loopback](http://127.0.0.1:5071). Use that exact address; `localhost` and other ports are deliberately rejected. Stop with `Ctrl+C`. No accounts, external services or frontend build are required.

| Fictional username | Demo password |
| --- | --- |
| `alex` | `Alex-demo-47!` |
| `sam` | `Sam-demo-82!` |

The first run creates `instance/notes.sqlite3`, seeds both users and one note each. Later runs preserve edits and deletions. The tests create their own temporary database. The runtime database, virtual environment and bytecode are ignored by Git; do not commit local notes. To start over, stop the app and move the `instance` directory to a backup location before running again.

## A five-minute demonstration

1. Sign in as Alex. Create a note and copy its `/notes/<id>` URL.
2. Sign out, then sign in as Sam. Alex's title is absent from Sam's list.
3. Open Alex's copied URL. It returns the same `404` used for a missing note.
4. Create Sam's own note, edit it, then delete it.
5. Run the tests. They also attempt cross-user edits/deletes, forged ownership fields, SQL injection input, HTML injection and reuse of a logged-out cookie.

Use separate browser profiles for simultaneous users: tabs in one profile share this app's cookie.

## Read the data flow

`form → request checks → server-side session → authenticated user → owner-scoped SQL → escaped HTML`

| Place | Responsibility |
| --- | --- |
| `app.py:create_app` | Configure the app and initialise the small SQLite schema. |
| `check_request` | Validate the exact host, load an unexpired session and check origin plus CSRF on every POST. |
| `login` / `logout` | Verify a Werkzeug password hash, rotate the login token and revoke the token at logout. |
| `owned_note` | Require a user and query both note ID **and** that user's ID. |
| `create_note` / `note` / `delete_note` | Validate fields and execute parameterised, owner-scoped writes. |
| `templates/` | Present forms and render note text through Jinja's default escaping. |
| `test_app.py` | Exercise the security boundaries through Flask's test client. |

The browser receives a random opaque cookie. SQLite holds its SHA-256 digest, associated user, CSRF token and fixed one-hour expiry. The session record, rather than a user ID supplied by a form, establishes identity. Login removes the anonymous session; logout deletes the current session record. Deleting a cookie alone would not revoke a stolen copy.

The important access query is deliberately visible:

```python
db().execute(
    "SELECT * FROM notes WHERE id = ? AND owner_id = ?",
    (note_id, g.user["id"]),
).fetchone()
```

Creation also takes `owner_id` from `g.user`. Extra ownership fields in a submitted form are ignored. Updates and deletes repeat the ownership predicate. Hiding links or guessing-resistant identifiers would not replace these checks.

## Controls and sources

- Passwords use Werkzeug's scrypt-based hash helpers; session tokens use the standard library's cryptographic randomness. See [Werkzeug password hashing](https://werkzeug.palletsprojects.com/en/stable/utils/#werkzeug.security.generate_password_hash) and [Python secrets](https://docs.python.org/3/library/secrets.html).
- Queries bind data with `?` placeholders, as recommended in [Python's SQLite documentation](https://docs.python.org/3/library/sqlite3.html#sqlite3-placeholders). Ownership checks follow [OWASP's object reference guidance](https://cheatsheetseries.owasp.org/cheatsheets/Insecure_Direct_Object_Reference_Prevention_Cheat_Sheet.html).
- Jinja escapes HTML; forms use quoted attributes. CSRF tokens, an exact POST `Origin`, strict same-site cookies, response headers, trusted hosts and a 64 KiB request limit supply additional boundaries. `Referrer-Policy: same-origin` preserves normal local form submissions while suppressing referrers to other origins; see [MDN's policy and Origin explanation](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Referrer-Policy#effect_on_the_origin_header). See also [Flask security considerations](https://flask.palletsprojects.com/en/stable/web-security/) and [OWASP CSRF guidance](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html).
- Flask and Werkzeug are pinned for this exercise. Review available security updates before reusing the project. The test suite verifies application behaviour, not the absence of every possible vulnerability.

## Deliberate limits

This runs on `127.0.0.1` with debugging and the reloader disabled. Flask's development server is suitable for this local exercise; [Flask explicitly advises against production use](https://flask.palletsprojects.com/en/stable/deploying/). Do not publish or port-forward it.

The passwords are public demo credentials. There is no registration, password reset, login throttling, audit trail or multi-factor authentication. HTTP loopback cookies use `HttpOnly` and `SameSite=Strict` but cannot supply the transport protection of HTTPS `Secure` cookies. A process or person with access to the database can read its plaintext notes; account separation is an application control, not disk encryption. Session expiry is fixed at one hour, and logout revokes only the current session. Requests without a same-origin `Origin` header are rejected on POST, including hand-written command-line requests.

Use fictional data only. Production authentication, HTTPS, deployment hardening and wider security assessment are outside this exercise. There is no deliberately vulnerable mode.
