"""Turn bounded, normalized scanner observations into an offline HTML report."""

import argparse
from collections import Counter
from html import escape
import json
import os
from pathlib import Path
import re
import sys
import tempfile


MAX_BYTES = 1_000_000
MAX_FINDINGS = 500
MAX_DEPTH = 8
SEVERITIES = ("critical", "high", "medium", "low", "informational")
CONFIDENCES = ("high", "medium", "low")
ID_PATTERN = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}")


class ReportError(ValueError):
    """An expected input or output failure safe to show at the command line."""


def check_depth(source):
    """Bound container nesting before the JSON decoder visits it."""
    depth = 0
    quoted = False
    escaped = False
    for character in source:
        if quoted:
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == '"':
                quoted = False
        elif character == '"':
            quoted = True
        elif character in "[{":
            depth += 1
            if depth > MAX_DEPTH:
                raise ReportError("input exceeds the JSON nesting limit")
        elif character in "]}":
            depth -= 1


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ReportError("JSON objects must not repeat a field")
        result[key] = value
    return result


def reject_constant(value):
    raise ReportError("JSON must not contain non-finite numbers")


def fields(value, expected, label):
    if not isinstance(value, dict) or set(value) != set(expected):
        raise ReportError(f"{label}: missing or unsupported fields")


def short_text(value, maximum, label):
    if not isinstance(value, str) or not value.strip() or len(value) > maximum:
        raise ReportError(f"{label}: expected nonempty text, at most {maximum} characters")
    # Reject invisible controls and lone surrogates before HTML serialization.
    if any((ord(char) < 32 and char not in "\n\r\t") or
           127 <= ord(char) <= 159 or 0xD800 <= ord(char) <= 0xDFFF
           for char in value):
        raise ReportError(f"{label}: unsupported control or Unicode character")


def validate(data):
    """Validate every field; return the original data without coercion."""
    fields(data, ("schema_version", "report_title", "findings"), "report")
    if type(data["schema_version"]) is not int or data["schema_version"] != 1:
        raise ReportError("schema_version must be the integer 1")
    short_text(data["report_title"], 200, "report_title")
    findings = data["findings"]
    if not isinstance(findings, list) or len(findings) > MAX_FINDINGS:
        raise ReportError(f"findings must be a list of 0-{MAX_FINDINGS} observations")
    seen = set()
    for finding in findings:
        fields(finding, ("id", "resource", "title", "severity", "confidence", "evidence"),
               "finding")
        identifier = finding["id"]
        if not isinstance(identifier, str) or not ID_PATTERN.fullmatch(identifier):
            raise ReportError("finding id must be 1-64 ASCII letters, digits, dots, underscores or hyphens; start with a letter or digit")
        if identifier in seen:
            raise ReportError("finding ids must be unique")
        seen.add(identifier)
        short_text(finding["resource"], 500, "resource")
        short_text(finding["title"], 200, "finding title")
        for field, choices in (("severity", SEVERITIES), ("confidence", CONFIDENCES)):
            if not isinstance(finding[field], str) or finding[field] not in choices:
                raise ReportError(f"unsupported {field}")
        evidence = finding["evidence"]
        if not isinstance(evidence, list) or not 1 <= len(evidence) <= 10:
            raise ReportError("evidence must contain 1-10 text observations")
        for item in evidence:
            short_text(item, 2000, "evidence item")
    return data


def load_report(path):
    try:
        with Path(path).open("rb") as source:
            raw = source.read(MAX_BYTES + 1)
    except OSError as error:
        raise ReportError("input could not be read") from error
    if len(raw) > MAX_BYTES:
        raise ReportError(f"input exceeds {MAX_BYTES} bytes")
    try:
        source = raw.decode("utf-8-sig")
        check_depth(source)
        data = json.loads(source, object_pairs_hook=unique_object,
                          parse_constant=reject_constant)
    except (UnicodeError, json.JSONDecodeError, RecursionError, ValueError) as error:
        if isinstance(error, ReportError):
            raise
        raise ReportError("input is not valid UTF-8 JSON") from error
    return validate(data)


CSS = """
:root { color-scheme: light; font-family: system-ui, sans-serif; color: #172b3a; background: #edf2f5; }
* { box-sizing: border-box; }
body { margin: 0; line-height: 1.6; }
main { max-width: 1050px; margin: 0 auto; padding: 3rem 1.4rem; }
header { border-top: 6px solid #176b76; padding: 1.5rem 0; }
h1 { line-height: 1.2; font-size: clamp(1.8rem, 4vw, 2.8rem); margin: .5rem 0 1rem; }
h2 { font-size: 1.35rem; line-height: 1.35; margin: .35rem 0 .8rem; }
h3 { font-size: 1rem; margin-bottom: .4rem; }
.eyebrow { text-transform: uppercase; letter-spacing: .12em; font-size: .8rem; font-weight: 700; color: #225a67; }
.notice { background: #dcecf0; border-left: 4px solid #176b76; padding: 1rem 1.2rem; }
table { border-collapse: collapse; width: 100%; margin: 1.8rem 0 2.4rem; background: white; }
caption { text-align: left; font-weight: 700; padding-bottom: .6rem; }
th, td { text-align: left; padding: .5rem 1rem; border-bottom: 1px solid #dce3e9; }
td { font-variant-numeric: tabular-nums; }
thead { background: #172f41; color: white; }
article { background: white; border: 1px solid #d4dfe6; border-left: 5px solid #557080; border-radius: 4px; padding: 1.3rem; margin: 1.2rem 0; break-inside: avoid; }
article.critical, article.high { border-left-color: #aa2e39; }
article.medium { border-left-color: #966115; }
article.low { border-left-color: #1a6c74; }
.meta { font-size: .9rem; color: #374c5b; }
code, pre { font-family: ui-monospace, monospace; white-space: pre-wrap; overflow-wrap: anywhere; }
pre { margin: .3rem 0; font-size: .9rem; }
li { padding-left: .25rem; margin-bottom: .6rem; }
.resource { background: #f1f5f7; padding: .7rem; overflow-wrap: anywhere; }
h1, h2, .meta { overflow-wrap: anywhere; }
footer { color: #435765; font-size: .9rem; margin-top: 2rem; border-top: 1px solid #c9d7df; padding-top: 1rem; }
@media print {
  :root { background: white; color: black; }
  main { max-width: none; padding: 0; }
  header { padding-top: .5rem; }
  article { break-inside: auto; }
  h2, h3 { break-after: avoid; }
  .notice, thead { background: #f3f3f3; color: black; }
}
"""


def render_report(data):
    """Render validated values only as escaped text, never URLs or markup."""
    validate(data)
    title = escape(data["report_title"])
    findings = sorted(data["findings"], key=lambda row: (SEVERITIES.index(row["severity"]), row["id"]))
    counts = Counter(row["severity"] for row in findings)
    parts = [
        '<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        '<meta http-equiv="Content-Security-Policy" content="default-src \'none\'; style-src \'unsafe-inline\'; base-uri \'none\'; form-action \'none\'">',
        f"<title>{title}</title>\n<style>{CSS}</style>\n</head>\n<body>\n<main>",
        '<header><p class="eyebrow">Offline observation report</p>',
        f"<h1>{title}</h1>",
        f"<p>{len(findings)} supplied scanner observations.</p></header>",
        '<p class="notice">Severity and confidence are supplied by the input. This report does not confirm exploitation or independently validate evidence. Resource names and evidence are displayed as text.</p>',
        '<table><caption>Supplied severity counts</caption><thead><tr><th scope="col">Severity</th><th scope="col">Observations</th></tr></thead><tbody>',
    ]
    for severity in SEVERITIES:
        parts.append(f'<tr><th scope="row">{severity.title()}</th><td>{counts[severity]}</td></tr>')
    parts.append('</tbody></table>\n<section aria-label="Scanner observations">')
    if not findings:
        parts.append('<p>No observations supplied. An empty report does not establish that a system is secure.</p>')
    for finding in findings:
        parts.extend([
            f'<article class="{finding["severity"]}">',
            f'<p class="meta">{escape(finding["id"])} · Severity: {finding["severity"]} · Confidence: {finding["confidence"]}</p>',
            f'<h2>{escape(finding["title"])}</h2>',
            f'<p class="resource"><strong>Resource:</strong> <code>{escape(finding["resource"])}</code></p>',
            '<h3>Supplied evidence</h3><ul>',
        ])
        for item in finding["evidence"]:
            parts.append(f"<li><pre>{escape(item)}</pre></li>")
        parts.append("</ul></article>")
    parts.append('</section><footer>Generated locally from normalized JSON. Findings require human review before remediation or risk decisions.</footer>\n</main>\n</body>\n</html>\n')
    return "\n".join(parts)


def write_report(source, output, html):
    """Publish a complete temporary file with an atomic no-clobber hard link."""
    temporary = None
    try:
        output = Path(output)
        if Path(source).resolve() == output.resolve():
            raise ReportError("input and output must be different files")
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="\n",
                                         prefix=".scan-report-", suffix=".tmp",
                                         dir=output.parent, delete=False) as target:
            temporary = Path(target.name)
            target.write(html)
            target.flush()
            os.fsync(target.fileno())
        # Both files are on the same filesystem; link creation fails if output exists.
        os.link(temporary, output)
    except FileExistsError as error:
        raise ReportError("output already exists; choose a new filename") from error
    except (OSError, RuntimeError, UnicodeError) as error:
        raise ReportError("output could not be created; use a writable local folder with hard-link support") from error
    finally:
        if temporary is not None:
            try:
                temporary.unlink(missing_ok=True)
            except OSError as error:
                raise ReportError("temporary file cleanup failed; the output may already exist") from error


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="normalized JSON input file")
    parser.add_argument("output", help="new HTML output file; never overwritten")
    args = parser.parse_args(argv)
    try:
        data = load_report(args.input)
        html = render_report(data)
        write_report(args.input, args.output, html)
    except ReportError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    print(f"Wrote {len(data['findings'])} observations.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
