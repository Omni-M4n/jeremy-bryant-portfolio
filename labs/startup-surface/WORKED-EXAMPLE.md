# Worked example: office timer and note

The office timer `e1` exists in both snapshots. Its mechanism, command, account,
owner and hash all match, so record `matches-baseline`.

The note `e2` is new. The approval contains the same ID and every observed field,
including its file hash. Record `approved-addition`. An approval for a similar
name or an old file would not support this exact entry.

Cite both snapshots for `e1` and the observed plus approval records for `e2`.
Do not write "safe". This check explains the change history. It does not show
everything the launched program can do. Next, test the harmless note at sign-in
in the disposable VM described in the README.
