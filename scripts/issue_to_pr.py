#!/usr/bin/env python3
"""Turn an "Suggest a server" issue into the README row a pull request would add.

Run by .github/workflows/issue-to-pr.yml on an issue carrying the `addition` label.
It reads the issue form from the event payload, builds the row with the same rules
the validator enforces, inserts it into the right table of README.md, and reports
one of three outcomes through $GITHUB_OUTPUT:

    status=ok       README.md changed; the workflow opens a pull request
    status=manual   a section the form cannot fill on its own (a maintainer adds it)
    status=invalid  something in the form breaks a rule; the reason is commented

The issue text is untrusted input, so nothing from it reaches a shell: the workflow
passes the event payload file in, and gets back plain values and a comment file.
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

import validate

ROOT = Path(__file__).resolve().parent.parent
AUTOMATED = {"Servers", "Frameworks & Libraries"}
NO_RESPONSE = "_No response_"
URL_RE = re.compile(r"^https://[^\s()<>|\[\]]+$")


class Rejected(ValueError):
    """The submission breaks a rule; the message is shown to the submitter."""


def parse_form(body: str) -> dict[str, str]:
    """Return an issue form's answers by field label ('### Label' then the answer)."""
    fields: dict[str, str] = {}
    label = None
    lines: list[str] = []
    for line in (body or "").splitlines():
        if line.startswith("### "):
            if label is not None:
                fields[label] = "\n".join(lines).strip()
            label, lines = line[4:].strip(), []
        elif label is not None:
            lines.append(line)
    if label is not None:
        fields[label] = "\n".join(lines).strip()
    return {k: ("" if v == NO_RESPONSE else v) for k, v in fields.items()}


def _clean_name(raw: str) -> str:
    name = " ".join(raw.split())
    if not name:
        raise Rejected("The name is empty.")
    if any(ch in name for ch in "[]|"):
        raise Rejected("The name cannot contain `[`, `]` or `|`.")
    return name


def _clean_url(raw: str) -> str:
    url = raw.strip().rstrip("/")
    if not URL_RE.match(url):
        raise Rejected(
            "The URL must be one https:// link with no spaces, brackets or `|`."
        )
    return url


def _clean_description(raw: str) -> str:
    desc = " ".join(raw.split()).rstrip(".").strip()
    if not desc:
        raise Rejected("The description is empty.")
    if "|" in desc:
        raise Rejected("The description cannot contain `|`.")
    desc = desc[0].upper() + desc[1:]
    if len(desc) > validate.MAX_DESC:
        raise Rejected(
            f"The description is {len(desc)} characters; the list allows "
            f"{validate.MAX_DESC}. State what the server does, not the pitch."
        )
    return desc


def _clean_language(raw: str) -> str:
    by_lower = {lang.lower(): lang for lang in validate.LANGUAGES}
    lang = by_lower.get(raw.strip().lower())
    if lang is None:
        options = ", ".join(sorted(validate.LANGUAGES))
        raise Rejected(
            f"`{raw.strip()}` is not a language the list uses. Pick one of: {options}."
        )
    return lang


def build_row(fields: dict[str, str]) -> tuple[str, str]:
    """Return (README section, table row) for a form, or raise Rejected / LookupError.

    LookupError means the section is one the form does not fill automatically.
    """
    section = fields.get("Section", "").strip()
    if section not in AUTOMATED:
        raise LookupError(section)
    name = _clean_name(fields.get("Name", ""))
    url = _clean_url(fields.get("Repository or project URL", ""))
    desc = _clean_description(fields.get("Description", ""))
    lang = _clean_language(fields.get("Language", ""))
    if section == "Servers":
        category = fields.get("Category", "").strip()
        if category not in validate.SERVER_CATEGORIES:
            raise Rejected("A server needs one of the server categories, not `n/a`.")
        section = category
    return section, f"| [{name}]({url}) | {desc} | {lang} |"


def insert_row(lines: list[str], section: str, row: str) -> list[str]:
    """Return README lines with the row added to the section's table, in order."""
    entries, heading_lines, _ = validate.parse(lines)
    wanted = validate.normalize_url(row.split("](", 1)[1].split(")", 1)[0])
    for rows in entries.values():
        for e in rows:
            if validate.normalize_url(e.url) == wanted:
                raise Rejected(
                    f"That link is already on the list, as {e.name} in {e.section}."
                )
    start = heading_lines.get(section)
    if start is None:
        raise Rejected(f"The README has no `{section}` section.")
    i = start  # 0-based index of the line after the heading
    while i < len(lines) and not lines[i].startswith("|"):
        i += 1
    while i < len(lines) and lines[i].startswith("|"):
        i += 1
    return validate.fix(lines[:i] + [row + "\n"] + lines[i:])


def _write_outputs(values: dict[str, str]) -> None:
    out = os.environ.get("GITHUB_OUTPUT")
    text = "".join(f"{k}={v}\n" for k, v in values.items())
    if out:
        with open(out, "a", encoding="utf-8") as fh:
            fh.write(text)
    else:
        print(text, end="")


def main() -> int:
    event = json.loads(
        Path(os.environ["GITHUB_EVENT_PATH"]).read_text(encoding="utf-8")
    )
    issue = event["issue"]
    comment = ROOT / "issue-comment.md"
    fields = parse_form(issue.get("body") or "")
    try:
        section, row = build_row(fields)
        readme = ROOT / "README.md"
        lines = readme.read_text(encoding="utf-8").splitlines(True)
        readme.write_text("".join(insert_row(lines, section, row)), encoding="utf-8")
    except LookupError:
        comment.write_text(
            "Thanks! The form adds servers and frameworks on its own; this section is "
            "added by a maintainer, who will pick it up from here.\n",
            encoding="utf-8",
        )
        _write_outputs({"status": "manual"})
        return 0
    except Rejected as exc:
        comment.write_text(
            f"This could not be added automatically: {exc}\n\n"
            "Edit the issue to fix it and the bot will try again. The rules are in "
            "[CONTRIBUTING.md](https://github.com/Sagargupta16/awesome-mcp-servers/"
            "blob/main/CONTRIBUTING.md#quality-standards).\n",
            encoding="utf-8",
        )
        _write_outputs({"status": "invalid"})
        return 0
    # the name reaches git and gh only through the environment, never the command text
    name = row.split("](", 1)[0].removeprefix("| [")
    _write_outputs({"status": "ok", "name": name, "section": section})
    return 0


if __name__ == "__main__":
    sys.exit(main())
