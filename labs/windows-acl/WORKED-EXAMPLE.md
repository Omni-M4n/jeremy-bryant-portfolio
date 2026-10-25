# Worked example: classroom note

First predict whether the reader can open, change and remove the note. Think of
three separate requests rather than one broad word such as "access".

In `guided`, the token contains `reader` and `classroom`. The file has one
inherited allow rule for `classroom`, covering only `read`.

- `q1` asks for read. That group rule matches, so record `allow`.
- `q2` asks for write. No rule grants it, so record `deny`.
- `q3` asks for delete. The file has no grant and the parent list is empty.
  Neither route grants deletion, so record `deny`.

Evidence: cite the token, `file_aces[0]`, the empty parent list, and each request.
Do not say "all denies always win": rule order matters. Do not infer that a
real program will ask for just the one right shown here.
