# Guided case: review after your first attempt

The first request uses GET. Its target contains `item=red+apple`, so the
decoded query contains `item: ["red apple"]`. Its body and form are empty.
The header record contains `desk-1`.

The second request uses POST with a form content type. Its target is just
`/inspect`. Its raw body is `item=red+apple`, so the decoded form contains
`item: ["red apple"]` and the query is empty. Both responses are 200.

The decoded value agrees, but the location differs. `+` was converted to a
space by form decoding. It was not part of the original word. Compare the
raw target/body with the returned lists in evidence. Do not describe this as
a packet capture; it is the receiving app's record.
