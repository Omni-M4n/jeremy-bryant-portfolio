# Worked example: check software versions

Open this page after saving your guided answer. It explains the fictional records. It does not assess your skill.

## Read the notices

- `DEMO-ADV-001` covers demo-parser from 1.9.0 up to, but not including, 1.10.0.
- `DEMO-ADV-002` covers demo-builder from 2.0.0 up to, but not including, 2.0.5.

## Compare each component

1. `upload-parser` is version 1.9.9. As numbers, `(1,9,9)` is at least `(1,9,0)` and below `(1,10,0)`. It matches DEMO-ADV-001. It runs in the app. The case supplies a request-map path to it. Use `affected-prioritise-runtime-path`. This gives a reason for review. It does not prove that an exploit has occurred or would work.
2. `asset-builder` is 2.0.4, which lies within its range. It is used during development. That does not remove risk to build inputs or outputs. Use `affected-review-build-exposure`.
3. `theme-helper` has no supplied advisory. Use `no-advisory-supplied`. This does not mean that no flaws exist.

For a handover, name the package, version and notice ID. Cite the path evidence. Propose checking whether an update works with the app and whether other affected ranges still apply.

Keep your first answer. Add corrections in `notes.txt` and cite the facts that changed your view. If it matched, explain how you reached it. Copying a label does not show that you understand the evidence. Use the separate drills for later cases.
