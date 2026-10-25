# Guided case: review after your first attempt

The raw reflect response contains a real `<b>` start tag and `</b>` end
tag inside the paragraph. A browser is expected to show bold LOCAL MARKER,
without those tag characters on screen.

The encoded response contains `&lt;b&gt;LOCAL MARKER&lt;/b&gt;`. The browser
is expected to show the literal characters `<b>LOCAL MARKER</b>`. It reads
the escaped brackets as text, not as another nested bold tag.

The script records that response text and content types. It does not show
what a browser put on screen. Add the two browser screenshots. State whether
what you saw agrees with this prediction. The marker runs no script. It does
not show token theft or text stored for later visits. It is not a general
XSS test against another app.
