# Guided case: review after your first attempt

The guided run begins with a grey preference. Its first request sends
the valid cookie to `/open` from the other origin, without a token. The route
uses the session alone, so status 200 changes the preference to blue.

The second request asks `/protected` to change it to gold from the other
origin without a token. Status 403 leaves it blue. The following state read
is needed: a status alone does not show whether a write happened first.

The third request uses the current token and the desk's own origin. It
returns 200 and changes the preference to gold. Expected status sequence:
200, 403, 200. This checks both a blocked change and normal use.

These are real requests sent by the script. The script chooses its headers.
Add the separate browser checks before claiming that a browser sent the cookie
on its own. In this local pair, the ports differ but the site stays the same.
This does not show what happens between unrelated sites.
