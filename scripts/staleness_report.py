#!/usr/bin/env python3
"""Health report for every GitHub repository on the list.

Groups entries into what needs action: gone (404), archived, unlicensed, and
stale. Written to be run on a schedule and piped into a single tracking issue,
so the report replaces itself instead of accumulating noise.

    python scripts/staleness_report.py > report.md

Set GITHUB_TOKEN to raise the API rate limit from 60 to 5000 requests/hour.
"""

from __future__ import annotations

import json
import os
import re
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

README = Path(__file__).resolve().parent.parent / "README.md"
API = "https://api.github.com/graphql"
STALE_DAYS = 180
BATCH = 50

# Matches an entry link and stops at the first path separator, so an entry that
# points into a subdirectory -- `.../getzep/graphiti/tree/main/mcp_server` -- still
# resolves to its parent repository instead of being skipped. Requiring a bare
# `owner/repo)` previously left 13 entries unchecked.
ENTRY_RE = re.compile(
    r"\[(?P<name>[^\]]+)\]\(https://github\.com/(?P<owner>[\w.-]+)/(?P<repo>[\w.-]+)(?:[/)]|$)"
)

# This repository's own links (the CI badge, the issue links) are not entries.
SELF_SLUG = "sagargupta16/awesome-mcp-servers"


def graphql(query: str):
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        sys.exit("error: GITHUB_TOKEN is required for the GraphQL API")
    req = urllib.request.Request(
        API,
        data=json.dumps({"query": query}).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "awesome-mcp-servers-staleness",
        },
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))


def collect():
    """Return (name, owner, repo, section) for every GitHub entry, deduplicated."""
    section = None
    seen = set()
    out = []
    for line in README.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^#{2,3}\s+(.*)$", line)
        if m:
            section = m.group(1).strip()
            continue
        for e in ENTRY_RE.finditer(line):
            slug = f"{e.group('owner')}/{e.group('repo')}"
            if slug.lower() == SELF_SLUG or slug.lower() in seen:
                continue
            seen.add(slug.lower())
            out.append(
                (e.group("name"), e.group("owner"), e.group("repo"), section or "?")
            )
    return out


def fetch(entries):
    results = {}
    for start in range(0, len(entries), BATCH):
        chunk = entries[start : start + BATCH]
        parts = [
            f'r{i}: repository(owner: "{o}", name: "{r}") '
            f"{{ nameWithOwner stargazerCount pushedAt isArchived licenseInfo {{ spdxId }} }}"
            for i, (_, o, r, _) in enumerate(chunk)
        ]
        data = graphql("query{" + " ".join(parts) + "}")
        payload = data.get("data") or {}
        for i, entry in enumerate(chunk):
            results[entry] = payload.get(f"r{i}")
    return results


def main() -> int:
    entries = collect()
    results = fetch(entries)
    now = datetime.now(timezone.utc)

    gone, archived, unlicensed, stale, moved = [], [], [], [], []
    for entry, info in results.items():
        name, owner, repo, section = entry
        slug = f"{owner}/{repo}"
        if info is None:
            gone.append((name, slug, section))
            continue
        # GitHub serves a renamed or transferred repository over a redirect, so the
        # listed URL keeps working right up until someone claims the old name.
        if info["nameWithOwner"].lower() != slug.lower():
            moved.append((name, slug, info["nameWithOwner"], section))
        pushed = datetime.fromisoformat(info["pushedAt"].replace("Z", "+00:00"))
        days = (now - pushed).days
        licence = (info.get("licenseInfo") or {}).get("spdxId")
        if info["isArchived"]:
            archived.append((name, slug, section, days))
        if licence in (None, "", "NOASSERTION"):
            unlicensed.append(
                (name, slug, section, licence or "none", info["stargazerCount"])
            )
        if days > STALE_DAYS and not info["isArchived"]:
            stale.append((days, name, slug, section, info["stargazerCount"]))

    checked = len(entries)
    out = [
        f"Automated health check of the {checked} GitHub repositories behind the entries "
        f"in `README.md`. Entries hosted elsewhere are covered only by the lychee link "
        f"check in `.github/workflows/lint.yml`.",
        "",
        f"- **{len(gone)}** gone (404 -- deleted or made private)",
        f"- **{len(moved)}** reachable only through a rename or transfer redirect",
        f"- **{len(archived)}** archived upstream",
        f"- **{len(unlicensed)}** with no recognised licence",
        f"- **{len(stale)}** not pushed in over {STALE_DAYS} days",
        "",
        "This issue is rewritten in place on every run, so it always reflects the current state.",
        "",
    ]

    if gone:
        out += [
            "## Gone: remove these",
            "",
            "These URLs 404. Per CONTRIBUTING.md they should be removed.",
            "",
            "| Entry | Repo | Section |",
            "|-------|------|---------|",
        ]
        out += [f"| {n} | `{s}` | {sec} |" for n, s, sec in sorted(gone)]
        out.append("")

    if moved:
        out += [
            "## Moved: update the URL",
            "",
            "These resolve through a redirect, which only holds while the old name stays "
            "unclaimed. Rewrite the URL, and check the entry name and description too if "
            "the project was renamed rather than just transferred.",
            "",
            "| Entry | Listed as | Now | Section |",
            "|-------|-----------|-----|---------|",
        ]
        out += [
            f"| {n} | `{s}` | `{actual}` | {sec} |"
            for n, s, actual, sec in sorted(moved)
        ]
        out.append("")

    if archived:
        out += [
            "## Archived upstream",
            "",
            "The maintainer has archived these. Remove them, or note them as unmaintained.",
            "",
            "| Entry | Repo | Section | Last push |",
            "|-------|------|---------|-----------|",
        ]
        out += [
            f"| {n} | `{s}` | {sec} | {d}d ago |" for n, s, sec, d in sorted(archived)
        ]
        out.append("")

    if stale:
        out += [
            f"## Stale: no push in over {STALE_DAYS} days",
            "",
            "Not automatically disqualifying -- a finished, working server can sit still. "
            "Check whether each still works against the current MCP spec.",
            "",
            "| Days | Entry | Repo | Section | Stars |",
            "|------|-------|------|---------|-------|",
        ]
        out += [
            f"| {d} | {n} | `{s}` | {sec} | {st} |"
            for d, n, s, sec, st in sorted(stale, reverse=True)
        ]
        out.append("")

    if unlicensed:
        out += [
            "## No recognised licence",
            "",
            "CONTRIBUTING.md requires a clearly stated licence. Neither value below is "
            "automatically a rejection. `NOASSERTION` means GitHub found a licence file "
            "it could not identify -- usually fine for a large vendor repo, suspicious "
            "for a small one. `none` means there is no `LICENSE` file in the repository "
            "root, which is also what GitHub reports for a project that declares its "
            "licence in `package.json` or `pyproject.toml`; check the manifest before "
            "acting, because CONTRIBUTING.md accepts that.",
            "",
            "| Entry | Repo | Section | Licence | Stars |",
            "|-------|------|---------|---------|-------|",
        ]
        out += [
            f"| {n} | `{s}` | {sec} | {lic} | {st} |"
            for n, s, sec, lic, st in sorted(unlicensed, key=lambda x: x[4])
        ]
        out.append("")

    if not (gone or moved or archived or stale or unlicensed):
        out.append(
            "Every entry is live, licensed, maintained, and unarchived. Nothing to do."
        )

    print("\n".join(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
