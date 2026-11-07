# Access Notes practice path

Work on a copy or a branch. Keep the supplied working app as a reference. Use fictional data and only this local app. Each stage ends with something you should be able to explain or demonstrate; ticking a box requires doing the work yourself.

## 1. Use it before reading it

- [ ] Run the existing tests and record the result.
- [ ] Run the five-minute demonstration in the README.
- [ ] Explain what Alex can do, what Sam can do, and what happens when Sam requests Alex's note ID.

Write three sentences distinguishing authentication (who is signed in), authorisation (what that user may access) and validation (whether a title/body is acceptable).

## 2. Follow one request

Read `templates/notes.html`, then find `create_note` in `app.py`. On paper trace a POST from the browser through `check_request`, `require_user`, `note_fields`, `INSERT`, `commit` and the redirect. Do not try to understand every helper at once.

- [ ] Point to where title/body arrive from the browser.
- [ ] Point to where the trusted user ID comes from.
- [ ] Explain why the app does not read `owner_id` from the form.
- [ ] Explain why a redirect follows a successful POST.

## 3. Learn the syntax in that path

Use these concrete lines as small Python exercises:

| Syntax | Explain it, then predict a small change |
| --- | --- |
| `@app.post("/notes")` | A decorator registers a function for a URL and HTTP method. What happens for a GET to that URL? |
| `request.form.get("title", "").strip()` | Explain the method calls, default and whitespace handling. What happens when the field is absent? |
| `(g.user["id"],)` | Explain dictionary-style row access and why a one-item tuple has a comma. |
| `1 <= len(title) <= 80` | Explain the chained comparison. Predict the result for an empty or 81-character title. |
| `with app.app_context():` | Explain why setup code needs application context for `g` and database access. |
| `return response, 401` | Explain the response/status pair. Compare it with a redirect response. |

- [ ] Check each prediction by reading or running a focused test.
- [ ] Write a 10-line explanation of `create_note` without copying comments.

## 4. Make one small independent change

Choose just one change; define the expected behaviour before editing.

1. Reduce the title limit to 60 characters. Update the server validation, HTML `maxlength`, help text and boundary test together. Prove that 60 succeeds and 61 fails.
2. Add a word count to the note page using a server-side calculation. Keep it as text rendered by Jinja. Check an empty/whitespace example separately without weakening the saved-note validation.
3. Add case-insensitive search within the signed-in user's list. Keep a parameterised query and the `owner_id` condition. Test that Alex's search cannot return Sam's matching title. Decide whether `%` and `_` should be literal characters or SQL `LIKE` wildcards, then document that choice.

- [ ] Explain every changed line.
- [ ] Run the existing regression suite plus a meaningful check of the changed behaviour.
- [ ] Record the changed files and evidence, including any unresolved bug.

Do not remove authentication, ownership predicates, escaping or CSRF checks to make a test pass. Discuss a vulnerable query on paper if helpful; the runnable project should retain its secure defaults.

## 5. Explain the security boundaries

Read the named tests, then the code they exercise:

- [ ] `test_other_users_note_id_denied_for_read_edit_and_delete`: why must the server check a guessed ID?
- [ ] `test_forged_owner_is_ignored_on_create_and_update`: why does a submitted user ID have no authority?
- [ ] `test_csrf_required_for_login_create_edit_delete_logout`: why does login need a token too?
- [ ] `test_logout_revokes_cookie_even_if_replayed`: why is clearing the browser cookie insufficient?
- [ ] `test_html_is_escaped_in_title_attribute_and_body`: how do HTML text, attributes and textarea content differ?
- [ ] `test_sql_injection_is_data_and_cannot_log_in`: what do SQL placeholders protect, and what do they fail to decide about access rights?

Draw the three database tables and their links. Explain why a fast SHA-256 digest is appropriate for a high-entropy session token here, while human passwords use a slow password hash.

## 6. Rebuild a narrow slice

In a separate scratch copy, implement only the owner-scoped read helper and its cross-user test from your written specification. Compare with the reference afterwards. Keep this local and leave the original intact.

- [ ] State what you wrote without reference and what you needed help with.
- [ ] Demonstrate a successful own-note read, an unauthenticated denial and an other-user denial.
- [ ] Explain the missing production controls in the README without calling this production-ready.

Then update the status in your own practice log. Use the interview wording only to the extent that your completed work supports it.
