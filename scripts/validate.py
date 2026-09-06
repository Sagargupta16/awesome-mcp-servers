#!/usr/bin/env python3
"""Structural validator for README.md.

Enforces every rule CONTRIBUTING.md promises, so a pull request cannot merge
while it breaks the list's format. Run with no arguments to check, or with
--fix to auto-repair the mechanical problems (ordering, whitespace, dashes).

    python scripts/validate.py
    python scripts/validate.py --fix

Exit code 0 = clean, 1 = at least one error.
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

README = Path(__file__).resolve().parent.parent / "README.md"

# Canonical server categories, in the order they must appear in README.md.
# Adding a category here is deliberate: CONTRIBUTING.md requires an issue
# discussion first, so this list is the enforcement point for that rule.
SERVER_CATEGORIES = [
    "Data & Databases",
    "Developer Tools",
    "Cloud & Infrastructure",
    "Productivity",
    "Search & Knowledge",
    "Communication",
    "File Systems & Storage",
    "AI & ML",
    "Finance",
    "Monitoring & Observability",
    "Design & Creative",
    "Testing & QA",
    "Security",
    "Web Browsing & Scraping",
    "Media & Entertainment",
    "Travel & Location",
    "E-commerce",
    "Game Development",
    "IoT & Home Automation",
    "Marketing & Analytics",
    "Knowledge Management",
]

TOP_SECTIONS = [
    "Official",
    "Servers",
    "Frameworks & Libraries",
    "Clients",
    "Tutorials & Articles",
    "Videos",
    "Community",
]

# Sections whose body is a markdown table, and the header row each must use.
TABLE_HEADERS = {
    "Frameworks & Libraries": ["Project", "Description", "Language"],
    "Clients": ["Client", "Description", "MCP Support"],
    **{c: ["Server", "Description", "Language"] for c in SERVER_CATEGORIES},
}

# Sections whose body is a bullet list.
BULLET_SECTIONS = ["Official", "Tutorials & Articles", "Videos", "Community"]

LANGUAGES = {
    "TypeScript",
    "JavaScript",
    "Python",
    "Go",
    "Rust",
    "Java",
    "Kotlin",
    "C#",
    "C++",
    "C",
    "Ruby",
    "PHP",
    "Swift",
    "Elixir",
    "Scala",
    "Dart",
    "Lua",
    "Shell",
    "Zig",
    "Multiple",
    "Remote",
    "Built-in",
}

# Capability tiers for the Clients table, derived from which MCP primitives each
# client actually implements. The README carries the same legend for readers.
#   Full              tools, resources, prompts, and sampling or elicitation
#   Standard          tools, resources and prompts
#   Tools + resources tools and resources, no prompts
#   Tools only        tools only
#   Partial           tools plus some but not all of resources and prompts
CLIENT_SUPPORT = {
    "Full",
    "Standard",
    "Tools + resources",
    "Tools only",
    "Partial",
    "Experimental",
}

# Table rows are scanned, so they stay terse. Bullet sections are prose and
# get more room.
MAX_DESC = 80
MAX_BULLET_DESC = 160
DASHES = {chr(0x2014): "em-dash", chr(0x2013): "en-dash"}

ROW_RE = re.compile(
    r"^\|\s*\[(?P<name>[^\]]+)\]\((?P<url>[^)\s]+)\)\s*\|(?P<rest>.*)\|\s*$"
)
BULLET_RE = re.compile(r"^- \[(?P<name>[^\]]+)\]\((?P<url>[^)\s]+)\) - (?P<desc>.+)$")
TOC_RE = re.compile(r"^\s*- \[(?P<label>[^\]]+)\]\(#(?P<anchor>[a-z0-9-]+)\)\s*$")


@dataclass
class Entry:
    line: int
    name: str
    url: str
    desc: str
    third: str
    section: str


@dataclass
class Report:
    errors: list = field(default_factory=list)

    def err(self, line, msg: str) -> None:
        where = f"README.md:{line}" if line else "README.md"
        self.errors.append(f"{where}: {msg}")


def slugify(heading: str) -> str:
    """GitHub's heading-anchor algorithm, for the subset of characters used here."""
    s = heading.strip().lower()
    s = re.sub(r"[^\w\s-]", "", s, flags=re.UNICODE)
    # One hyphen per whitespace character, not per run: "Data & Databases"
    # loses the ampersand and becomes "data--databases".
    return re.sub(r"\s", "-", s)


def normalize_url(url: str) -> str:
    return re.sub(r"^https?://(www\.)?", "", url.rstrip("/")).lower()


def sort_key(name: str) -> str:
    """Case-insensitive, leading-punctuation-insensitive name ordering."""
    return re.sub(r"^[^\w]+", "", name).casefold()


def parse(lines):
    """Return entries per section, heading line numbers, and heading order."""
    entries = defaultdict(list)
    heading_lines = {}
    order = []
    section = None

    for i, raw in enumerate(lines, 1):
        line = raw.rstrip("\n")
        m = re.match(r"^(#{2,3})\s+(.*)$", line)
        if m:
            section = m.group(2).strip()
            heading_lines[section] = i
            order.append(section)
            entries.setdefault(section, [])
            continue
        if section is None:
            continue

        rm = ROW_RE.match(line)
        if rm:
            cells = [c.strip() for c in rm.group("rest").split("|")]
            desc = cells[0] if cells else ""
            third = cells[1] if len(cells) > 1 else ""
            entries[section].append(
                Entry(
                    i,
                    rm.group("name").strip(),
                    rm.group("url").strip(),
                    desc,
                    third,
                    section,
                )
            )
            continue

        bm = BULLET_RE.match(line)
        if bm and section in BULLET_SECTIONS:
            entries[section].append(
                Entry(
                    i,
                    bm.group("name").strip(),
                    bm.group("url").strip(),
                    bm.group("desc").strip(),
                    "",
                    section,
                )
            )

    return entries, heading_lines, order


def check_structure(lines, order, heading_lines, rep: Report) -> None:
    top = [h for h in order if lines[heading_lines[h] - 1].startswith("## ")]
    top = [h for h in top if h not in ("Contents", "Contributing", "License")]
    if top != TOP_SECTIONS:
        rep.err(
            None,
            f"top-level sections {top} do not match the canonical order {TOP_SECTIONS}",
        )

    subs = [h for h in order if lines[heading_lines[h] - 1].startswith("### ")]
    if subs != SERVER_CATEGORIES:
        extra = [c for c in subs if c not in SERVER_CATEGORIES]
        missing = [c for c in SERVER_CATEGORIES if c not in subs]
        if extra:
            rep.err(
                None,
                f"unknown server category {extra} -- new categories need an issue "
                f"discussion first, then an entry in SERVER_CATEGORIES in scripts/validate.py",
            )
        if missing:
            rep.err(None, f"server category missing from README: {missing}")
        if not extra and not missing:
            rep.err(None, "server categories are present but out of canonical order")


def check_toc(lines, heading_lines, rep: Report) -> None:
    try:
        start = next(i for i, l in enumerate(lines) if l.startswith("## Contents"))
        end = next(
            i
            for i, l in enumerate(lines[start + 1 :], start + 1)
            if l.startswith("---")
        )
    except StopIteration:
        rep.err(None, "could not locate the '## Contents' block")
        return

    anchors, labels = [], []
    for i in range(start + 1, end):
        m = TOC_RE.match(lines[i].rstrip("\n"))
        if m:
            anchors.append((i + 1, m.group("anchor")))
            labels.append(m.group("label"))

    valid = {slugify(h) for h in heading_lines}
    for line_no, anchor in anchors:
        if anchor not in valid:
            rep.err(
                line_no, f"table-of-contents anchor #{anchor} has no matching heading"
            )

    expected = ["Official", "Servers"] + SERVER_CATEGORIES + TOP_SECTIONS[2:]
    if labels != expected:
        rep.err(
            start + 1,
            "table of contents does not list every section in canonical order "
            f"(expected {len(expected)} entries, found {len(labels)})",
        )


def check_table_headers(lines, heading_lines, rep: Report) -> None:
    for section, cols in TABLE_HEADERS.items():
        start = heading_lines.get(section)
        if start is None:
            continue
        header = None
        # Wide enough to skip an explanatory paragraph between heading and table.
        for i in range(start, min(start + 15, len(lines))):
            if lines[i].startswith("|"):
                header = (
                    i + 1,
                    [c.strip() for c in lines[i].strip().strip("|").split("|")],
                )
                break
        if header is None:
            rep.err(start, f"section '{section}' has no table")
            continue
        line_no, got = header
        if got != cols:
            rep.err(line_no, f"section '{section}' header is {got}, expected {cols}")


def check_entries(entries, rep: Report) -> None:
    for section, rows in entries.items():
        if section in ("Contents", "Contributing", "License", "Servers"):
            continue
        is_bullet = section in BULLET_SECTIONS

        for e in rows:
            if not e.url.startswith("https://"):
                rep.err(e.line, f"'{e.name}' URL must be https:// (got {e.url})")
            if not e.desc:
                rep.err(e.line, f"'{e.name}' has an empty description")
                continue
            cap = MAX_BULLET_DESC if is_bullet else MAX_DESC
            if len(e.desc) > cap:
                rep.err(
                    e.line,
                    f"'{e.name}' description is {len(e.desc)} chars, max {cap}",
                )
            if not (e.desc[0].isupper() or e.desc[0].isdigit()):
                rep.err(
                    e.line, f"'{e.name}' description must start with a capital letter"
                )
            if is_bullet and not e.desc.endswith("."):
                rep.err(e.line, f"'{e.name}' bullet description must end with a period")
            if not is_bullet and e.desc.endswith("."):
                rep.err(
                    e.line, f"'{e.name}' table description must not end with a period"
                )

            if is_bullet:
                continue
            if section == "Clients":
                if e.third not in CLIENT_SUPPORT:
                    rep.err(
                        e.line,
                        f"'{e.name}' MCP Support is '{e.third}', expected one of "
                        f"{sorted(CLIENT_SUPPORT)}",
                    )
            elif e.third not in LANGUAGES:
                rep.err(
                    e.line,
                    f"'{e.name}' language is '{e.third}', expected one of "
                    f"{sorted(LANGUAGES)}",
                )


def check_duplicates(entries, rep: Report) -> None:
    by_url = defaultdict(list)
    by_name = defaultdict(list)
    for section, rows in entries.items():
        # Every entry appears exactly once across the whole list. Official holds
        # the protocol and its tooling; the SDKs live in Frameworks & Libraries.
        if section in ("Contents", "Contributing", "License", "Servers"):
            continue
        for e in rows:
            by_url[normalize_url(e.url)].append(e)
            by_name[e.name.casefold()].append(e)

    for url, es in by_url.items():
        if len(es) > 1:
            where = ", ".join(f"{e.section} L{e.line}" for e in es)
            rep.err(es[0].line, f"duplicate URL {url} listed {len(es)} times ({where})")
    for _, es in by_name.items():
        if len(es) > 1:
            where = ", ".join(f"{e.section} L{e.line}" for e in es)
            rep.err(
                es[0].line,
                f"duplicate name '{es[0].name}' listed {len(es)} times ({where})",
            )


def check_alphabetical(entries, rep: Report) -> None:
    for section, rows in entries.items():
        if section in TABLE_HEADERS and len(rows) > 1:
            for prev, cur in zip(rows, rows[1:]):
                if sort_key(cur.name) < sort_key(prev.name):
                    rep.err(
                        cur.line,
                        f"'{cur.name}' is out of alphabetical order "
                        f"(must come before '{prev.name}')",
                    )


def check_local_links(lines, heading_lines, rep: Report) -> None:
    """Every non-http link must resolve: a real file, or a real heading anchor.

    The link checker in CI treats a relative target as a filesystem path, so
    GitHub's `../../issues/new/choose` form passes review and then fails the
    build. Catch both cases here instead.
    """
    root = README.parent
    anchors = {slugify(h) for h in heading_lines}
    in_fence = False
    for i, raw in enumerate(lines, 1):
        line = raw.rstrip("\n")
        # Fenced blocks hold format examples like `| [Name](URL) |`, which are
        # illustrations rather than links. The CI link checker skips them too.
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        # Inline code spans are illustrations too, as in `| [Name](URL) | ... |`.
        line = re.sub(r"`[^`]*`", "", line)
        for target in re.findall(r"\]\(([^)\s]+)\)", line):
            if target.startswith(("http://", "https://", "mailto:")):
                continue
            if target.startswith("#"):
                if target[1:] not in anchors:
                    rep.err(i, f"link to #{target[1:]} has no matching heading")
                continue
            if target.startswith(".."):
                rep.err(
                    i,
                    f"relative link '{target}' escapes the repository; the link "
                    f"checker resolves it as a file path and fails. Use the full "
                    f"https://github.com/... URL instead",
                )
                continue
            path = target.partition("#")[0]
            if path and not (root / path).exists():
                rep.err(i, f"link target '{path}' does not exist")


def check_whitespace_and_dashes(lines, rep: Report) -> None:
    for i, raw in enumerate(lines, 1):
        line = raw.rstrip("\n")
        for ch, label in DASHES.items():
            if ch in line:
                rep.err(i, f"contains a {label}; use '--' or '-' instead")
        if line != line.rstrip():
            rep.err(i, "trailing whitespace")
    if lines and not lines[-1].endswith("\n"):
        rep.err(len(lines), "file must end with a newline")


def fix(lines):
    """Repair the mechanical problems: table ordering, whitespace, dashes."""
    out = list(lines)
    entries, _, _ = parse(out)

    for section, rows in entries.items():
        if section not in TABLE_HEADERS or len(rows) < 2:
            continue
        block = [out[e.line - 1] for e in rows]
        ordered = [
            b for _, b in sorted(zip(rows, block), key=lambda p: sort_key(p[0].name))
        ]
        for e, new in zip(rows, ordered):
            out[e.line - 1] = new

    out = [l.rstrip() + "\n" for l in out]
    for ch in DASHES:
        out = [l.replace(ch, "--") for l in out]
    while len(out) > 1 and out[-1].strip() == "":
        out.pop()
    return out


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument(
        "--fix", action="store_true", help="auto-repair ordering, whitespace and dashes"
    )
    args = ap.parse_args()

    if not README.exists():
        print(f"error: {README} not found", file=sys.stderr)
        return 1

    with README.open(encoding="utf-8", newline="") as fh:
        lines = fh.readlines()

    if args.fix:
        fixed = fix(lines)
        if fixed != lines:
            with README.open("w", encoding="utf-8", newline="") as fh:
                fh.writelines(fixed)
            print("README.md: applied automatic fixes (ordering, whitespace, dashes)")
        else:
            print("README.md: nothing to fix")
        lines = fixed

    rep = Report()
    entries, heading_lines, order = parse(lines)
    check_structure(lines, order, heading_lines, rep)
    check_toc(lines, heading_lines, rep)
    check_table_headers(lines, heading_lines, rep)
    check_entries(entries, rep)
    check_duplicates(entries, rep)
    check_alphabetical(entries, rep)
    check_local_links(lines, heading_lines, rep)
    check_whitespace_and_dashes(lines, rep)

    counted = {
        k: v
        for k, v in entries.items()
        if k not in ("Contents", "Contributing", "License", "Servers")
    }
    total = sum(len(v) for v in counted.values())
    if rep.errors:
        print(
            f"{len(rep.errors)} problem(s) found in {total} entries:\n", file=sys.stderr
        )
        for e in rep.errors:
            print(f"  {e}", file=sys.stderr)
        print(
            "\nRun 'python scripts/validate.py --fix' to repair ordering, whitespace and "
            "dashes automatically. Everything else needs a human edit.",
            file=sys.stderr,
        )
        return 1

    print(
        f"README.md is valid: {total} entries across {len(SERVER_CATEGORIES)} server "
        f"categories, no duplicates, all alphabetically ordered."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
