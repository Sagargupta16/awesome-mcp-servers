#!/usr/bin/env python3
"""Quality gate for newly submitted entries.

Reads the rows a pull request ADDS to README.md, looks each one up on GitHub,
and reports what the maintainer would otherwise have to check by hand: stars,
licence, last push, archived state, repo age, and whether the repo actually
contains an MCP implementation rather than just a manifest.

Hard failures block the pull request. Soft warnings are printed for a human to
judge. Both land in the GitHub Actions step summary.

    python scripts/check_submission.py --base-ref origin/main

Set GITHUB_TOKEN to raise the API rate limit from 60 to 5000 requests/hour.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

API = "https://api.github.com"

# Tunables. These encode the quality bar in CONTRIBUTING.md.
MAX_SERVERS_PER_PR = 1
STALE_DAYS = 180
MIN_STARS = 150
YOUNG_REPO_DAYS = 90
OVERRIDE_LABEL = "maintainer-override"

# Files that make a repo a manifest-only listing rather than a real project.
MANIFEST_ONLY = {
    "server.json",
    "glama.json",
    "mcp.json",
    "plugin.json",
    "readme.md",
    "logo.png",
    "license",
}

ROW_RE = re.compile(
    r"^\+\|\s*\[(?P<name>[^\]]+)\]\((?P<url>[^)\s]+)\)\s*\|(?P<rest>.*)\|\s*$"
)
GH_REPO_RE = re.compile(r"^https://github\.com/(?P<owner>[\w.-]+)/(?P<repo>[\w.-]+)/?$")


@dataclass
class Submission:
    name: str
    url: str
    desc: str
    third: str
    hard: list = field(default_factory=list)
    soft: list = field(default_factory=list)
    facts: dict = field(default_factory=dict)


def gh_api(path: str):
    req = urllib.request.Request(
        f"{API}/{path}",
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "awesome-mcp-servers-submission-check",
        },
    )
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8")), None
    except urllib.error.HTTPError as exc:
        return None, exc.code
    except (urllib.error.URLError, TimeoutError) as exc:
        return None, f"network: {exc}"


def added_rows(base_ref: str) -> list:
    diff = subprocess.run(
        ["git", "diff", "--unified=0", f"{base_ref}...HEAD", "--", "README.md"],
        capture_output=True,
        text=True,
        check=False,
    )
    if diff.returncode != 0:
        print(f"warning: git diff failed: {diff.stderr.strip()}", file=sys.stderr)
        return []

    rows = []
    for line in diff.stdout.splitlines():
        m = ROW_RE.match(line)
        if not m:
            continue
        cells = [c.strip() for c in m.group("rest").split("|")]
        rows.append(
            Submission(
                name=m.group("name").strip(),
                url=m.group("url").strip(),
                desc=cells[0] if cells else "",
                third=cells[1] if len(cells) > 1 else "",
            )
        )
    return rows


def inspect(sub: Submission) -> None:
    m = GH_REPO_RE.match(sub.url)
    if not m:
        sub.soft.append(
            "Not a plain GitHub repository URL, so it cannot be checked "
            "automatically. A maintainer must verify it by hand."
        )
        return

    slug = f"{m.group('owner')}/{m.group('repo')}"
    data, err = gh_api(f"repos/{slug}")
    if data is None:
        if err == 404:
            sub.hard.append(
                f"`{slug}` returns 404. The repository is private, renamed, or deleted."
            )
        else:
            sub.soft.append(f"Could not reach the GitHub API for `{slug}` ({err}).")
        return

    pushed = datetime.fromisoformat(data["pushed_at"].replace("Z", "+00:00"))
    created = datetime.fromisoformat(data["created_at"].replace("Z", "+00:00"))
    now = datetime.now(timezone.utc)
    stale_days = (now - pushed).days
    age_days = (now - created).days
    licence = (data.get("license") or {}).get("spdx_id")
    stars = data["stargazers_count"]

    sub.facts = {
        "repo": slug,
        "stars": stars,
        "license": licence or "none",
        "last push": f"{data['pushed_at'][:10]} ({stale_days}d ago)",
        "created": f"{data['created_at'][:10]} ({age_days}d old)",
        "archived": data["archived"],
        "fork": data["fork"],
        "language": data.get("language") or "unknown",
    }

    if data["archived"]:
        sub.hard.append(
            "The repository is archived. Archived projects are not accepted."
        )
    if data["fork"]:
        sub.hard.append(
            "The repository is a fork. Submit the upstream project instead."
        )
    if licence in (None, "", "NOASSERTION"):
        sub.hard.append(
            "No recognised open-source licence. CONTRIBUTING.md requires a clearly "
            "stated licence; add a LICENSE file GitHub can detect."
        )
    if stale_days > STALE_DAYS:
        sub.hard.append(
            f"Last push was {stale_days} days ago, over the {STALE_DAYS}-day "
            f"maintenance threshold."
        )

    tree, tree_err = gh_api(f"repos/{slug}/contents")
    if isinstance(tree, list):
        names = {f["name"].lower() for f in tree}
        if not any(
            n in names for n in ("readme.md", "readme.rst", "readme", "readme.txt")
        ):
            sub.hard.append(
                "No README at the repository root. CONTRIBUTING.md requires install "
                "and usage documentation."
            )
        if names and names <= MANIFEST_ONLY:
            sub.hard.append(
                f"The repository root contains only {sorted(names)} -- a README plus "
                f"registry manifests, with no MCP implementation. Publish the server "
                f"source, or submit the repository that holds it."
            )
    elif tree_err:
        sub.soft.append(
            f"Could not list the repository root ({tree_err}); MCP implementation "
            f"not verified."
        )

    if stars < MIN_STARS:
        sub.soft.append(
            f"{stars} stars, below the {MIN_STARS} guideline. Acceptable only if this "
            f"is the vendor's own official server for a well-known product -- a "
            f"maintainer must confirm that."
        )
    if age_days < YOUNG_REPO_DAYS:
        sub.soft.append(
            f"The repository is only {age_days} days old. New projects are welcome but "
            f"get extra scrutiny for self-promotion."
        )


def render(subs: list, override: bool) -> tuple[str, bool]:
    lines = ["## Submission check", ""]
    hard_total = sum(len(s.hard) for s in subs)

    if not subs:
        lines.append("No new entries detected in `README.md`. Nothing to check.")
        return "\n".join(lines) + "\n", False

    servers = len(subs)
    lines.append(f"Found **{servers}** new entr{'y' if servers == 1 else 'ies'}.")
    lines.append("")

    too_many = servers > MAX_SERVERS_PER_PR
    if too_many:
        lines.append(f"> [!CAUTION]")
        lines.append(
            f"> This pull request adds {servers} entries. CONTRIBUTING.md asks for "
            f"**one server per pull request** so each can be reviewed and reverted "
            f"independently. Please split it up."
        )
        lines.append("")

    for s in subs:
        lines.append(f"### {s.name}")
        lines.append(f"{s.url}")
        lines.append("")
        if s.facts:
            lines.append("| Check | Value |")
            lines.append("|-------|-------|")
            for k, v in s.facts.items():
                lines.append(f"| {k} | {v} |")
            lines.append("")
        if s.hard:
            lines.append("**Blocking:**")
            lines.extend(f"- {h}" for h in s.hard)
            lines.append("")
        if s.soft:
            lines.append("**Needs a maintainer decision:**")
            lines.extend(f"- {w}" for w in s.soft)
            lines.append("")
        if not s.hard and not s.soft:
            lines.append("Passes every automated check.")
            lines.append("")

    failing = (hard_total > 0 or too_many) and not override
    if override:
        lines.append(f"Gate bypassed by the `{OVERRIDE_LABEL}` label.")
    elif failing:
        lines.append(
            f"**Result: blocked.** {hard_total} blocking problem(s). Fix them, or a "
            f"maintainer can add the `{OVERRIDE_LABEL}` label to merge anyway."
        )
    else:
        lines.append("**Result: passed.** No blocking problems.")

    return "\n".join(lines) + "\n", failing


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--base-ref", default="origin/main", help="ref to diff against")
    ap.add_argument("--labels", default="", help="comma-separated pull request labels")
    args = ap.parse_args()

    subs = added_rows(args.base_ref)
    for s in subs:
        inspect(s)

    override = OVERRIDE_LABEL in {l.strip() for l in args.labels.split(",")}
    report, failing = render(subs, override)

    print(report)
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        Path(summary).write_text(report, encoding="utf-8")

    return 1 if failing else 0


if __name__ == "__main__":
    sys.exit(main())
