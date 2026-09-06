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
import base64
import json
import os
import re
import subprocess
import sys
import tomllib
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

API = "https://api.github.com"

# Tunables. These encode the quality bar in CONTRIBUTING.md.
#
# There is deliberately no star or repo-age minimum. Anyone may submit their own
# MCP server, including a brand-new one with no traction. What is checked is
# whether the thing is real: a working implementation, a licence, documentation,
# and recent activity. Stars measure popularity, which is a different question.
MAX_SERVERS_PER_PR = 1
STALE_DAYS = 180
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

# A build manifest at the root is positive evidence of a real project, where the
# MANIFEST_ONLY list above is only evidence of a known-bad shape.
PROJECT_MARKERS = {
    "package.json",
    "pyproject.toml",
    "setup.py",
    "requirements.txt",
    "go.mod",
    "cargo.toml",
    "pom.xml",
    "build.gradle",
    "build.gradle.kts",
    "gemfile",
    "composer.json",
    "pubspec.yaml",
    "mix.exs",
    "build.zig",
    "package.swift",
    "makefile",
    "dockerfile",
    "deno.json",
    "bun.lockb",
}

# Package manifests that can carry a licence declaration. CONTRIBUTING.md accepts
# one of these when there is no LICENSE file at the root, because GitHub's licence
# API only reads the root file and so reports such a project as unlicensed.
MANIFEST_LICENCE_FILES = (
    "package.json",
    "pyproject.toml",
    "Cargo.toml",
    "pom.xml",
    "composer.json",
    "deno.json",
)

# Values that fill the licence field without granting open-source terms. npm
# documents `UNLICENSED` for a package that is deliberately not open source and
# `SEE LICENSE IN <file>` for terms the API cannot read. `Unlicense` -- the
# public-domain dedication -- is a real licence and is deliberately not here.
NOT_OPEN_SOURCE = {
    "unlicensed",
    "proprietary",
    "commercial",
    "closed",
    "closed-source",
    "none",
    "noassertion",
}
NOT_OPEN_SOURCE_PREFIXES = ("see license in", "see licence in")

# Maven has no JSON or TOML form to parse, so this one manifest stays a regex.
POM_LICENCE_RE = re.compile(
    r"<licenses?>.*?<name>\s*([^<]+?)\s*</name>", re.DOTALL | re.IGNORECASE
)

ROW_RE = re.compile(
    r"^\|\s*\[(?P<name>[^\]]+)\]\((?P<url>[^)\s]+)\)\s*\|(?P<rest>.*)\|\s*$"
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


def is_open_source(licence: str) -> bool:
    """False for a licence field that names no open-source terms.

    The field being filled in is not the same as the terms being open source:
    `UNLICENSED` is npm's documented marker for a package that is explicitly not.
    """
    value = licence.strip().lower()
    if value in NOT_OPEN_SOURCE:
        return False
    return not value.startswith(NOT_OPEN_SOURCE_PREFIXES)


def _first_licence_string(value) -> str | None:
    """Pull a licence name out of the shapes the manifest formats allow.

    A plain string, npm's legacy `{"type": "MIT"}` object, a composer array, or
    PEP 621's `{text = "MIT"}` table. A `{file = ...}` or `license-file` pointer
    names no terms, so it is not treated as a declaration.
    """
    if isinstance(value, str):
        return value.strip() or None
    if isinstance(value, dict):
        for key in ("type", "text"):
            found = _first_licence_string(value.get(key))
            if found:
                return found
        return None
    if isinstance(value, list):
        for item in value:
            found = _first_licence_string(item)
            if found:
                return found
    return None


def parse_manifest_licence(filename: str, text: str) -> str | None:
    """Read the declared licence out of one manifest, or None.

    Parsed rather than pattern-matched: a regex over the raw text reads a nested
    `"license"` key belonging to some other object as the package's own.
    """
    name = filename.lower()
    try:
        if name.endswith(".json"):
            data = json.loads(text)
            if not isinstance(data, dict):
                return None
            return _first_licence_string(data.get("license") or data.get("licenses"))
        if name.endswith(".toml"):
            data = tomllib.loads(text)
            # `[project]` is PEP 621, `[package]` is Cargo.
            for table in ("project", "package"):
                section = data.get(table)
                if isinstance(section, dict):
                    found = _first_licence_string(section.get("license"))
                    if found:
                        return found
            return None
        if name.endswith(".xml"):
            match = POM_LICENCE_RE.search(text)
            return match.group(1) if match else None
    except (json.JSONDecodeError, tomllib.TOMLDecodeError, UnicodeDecodeError):
        return None
    return None


def manifest_licence(slug: str) -> tuple[str | None, str | None]:
    """Return (manifest filename, licence) for the first manifest that declares one.

    GitHub's licence endpoint only looks at a `LICENSE` file in the repository
    root, so a project that declares its licence in `package.json` or
    `pyproject.toml` reports as having none at all. CONTRIBUTING.md accepts a
    manifest declaration, so look for one before blocking a submission.
    """
    for name in MANIFEST_LICENCE_FILES:
        data, _ = gh_api(f"repos/{slug}/contents/{name}")
        if not isinstance(data, dict) or not data.get("content"):
            continue
        try:
            text = base64.b64decode(data["content"]).decode("utf-8", "replace")
        except ValueError:
            continue
        licence = parse_manifest_licence(name, text)
        if licence:
            return name, licence
    return None, None


def parse_rows(text: str) -> dict:
    """Map normalised URL to Submission for every table row in a README."""
    rows = {}
    for line in text.splitlines():
        m = ROW_RE.match(line)
        if not m:
            continue
        cells = [c.strip() for c in m.group("rest").split("|")]
        url = m.group("url").strip()
        key = re.sub(r"^https?://(www\.)?", "", url.rstrip("/")).lower()
        rows[key] = Submission(
            name=m.group("name").strip(),
            url=url,
            desc=cells[0] if cells else "",
            third=cells[1] if len(cells) > 1 else "",
        )
    return rows


def added_rows(base_ref: str) -> list:
    """Entries present at HEAD but not at the base.

    Compares the two parsed entry sets rather than reading `+` lines from the
    diff. Reordering a table rewrites every moved row, so a diff-based reading
    reports untouched entries as new submissions and then blocks the pull
    request over rot that was already on the base branch.
    """
    base = subprocess.run(
        ["git", "show", f"{base_ref}:README.md"],
        capture_output=True,
        check=False,
    )
    if base.returncode != 0:
        print(
            f"warning: could not read README.md at {base_ref}: "
            f"{base.stderr.decode('utf-8', 'replace').strip()}",
            file=sys.stderr,
        )
        return []

    before = parse_rows(base.stdout.decode("utf-8", "replace"))
    after = parse_rows(Path("README.md").read_text(encoding="utf-8"))
    return [sub for key, sub in after.items() if key not in before]


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
    # "NOASSERTION" means GitHub found a licence file it could not classify,
    # which is a different thing from having none. The official MCP SDKs all
    # report it. Only a genuinely absent licence blocks.
    if licence in (None, "", "NOASSERTION"):
        lic_file, lic_err = gh_api(f"repos/{slug}/license")
        if isinstance(lic_file, dict) and lic_file.get("name"):
            sub.facts["license"] = f"{lic_file['name']} (unrecognised by GitHub)"
            sub.soft.append(
                f"GitHub cannot classify `{lic_file['name']}`, so it reports no SPDX "
                f"licence. Confirm by hand that the terms are open source. Common for "
                f"a vendor repo with a customised header, suspicious for a small one."
            )
        else:
            man_file, man_lic = manifest_licence(slug)
            if man_lic and not is_open_source(man_lic):
                sub.facts["license"] = f"{man_lic} (declared in {man_file})"
                sub.hard.append(
                    f"`{man_file}` declares `{man_lic}`, which states that the terms "
                    f"are not open source rather than naming a licence. "
                    f"CONTRIBUTING.md requires an open-source licence."
                )
            elif man_lic:
                sub.facts["license"] = f"{man_lic} (declared in {man_file})"
                sub.soft.append(
                    f"No `LICENSE` file at the repository root; the licence is declared "
                    f"as `{man_lic}` in `{man_file}`. CONTRIBUTING.md accepts that, but "
                    f"a root `LICENSE` file is what GitHub reads. Confirm the terms."
                )
            else:
                sub.hard.append(
                    f"No licence anywhere ({lic_err}): no `LICENSE` file at the root and "
                    f"no licence field in a package manifest. CONTRIBUTING.md requires a "
                    f"clearly stated licence."
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
        elif not (names & PROJECT_MARKERS) and not any(
            f["type"] == "dir" for f in tree
        ):
            # The check above only catches roots made entirely of known manifest
            # names, so an unrecognised file slips past it. Look for a positive
            # signal instead: a build manifest, or any directory to hold source.
            sub.soft.append(
                f"No build manifest or source directory at the repository root, only "
                f"{sorted(names)}. Confirm by hand that this holds a real MCP "
                f"implementation and is not a listing stub."
            )
    elif tree_err:
        sub.soft.append(
            f"Could not list the repository root ({tree_err}); MCP implementation "
            f"not verified."
        )

    # Star count and repo age are reported in the facts table above as context.
    # Neither is a bar: popularity is not quality, and a new project that works,
    # is licensed and is documented belongs on the list as much as a famous one.


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
        lines.append("> [!CAUTION]")
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
        if hard_total and too_many:
            why = (
                f"{hard_total} blocking problem(s), and it adds {servers} entries "
                f"instead of {MAX_SERVERS_PER_PR}"
            )
        elif hard_total:
            why = f"{hard_total} blocking problem(s)"
        else:
            why = (
                f"every entry passes its checks, but this adds {servers} entries "
                f"instead of {MAX_SERVERS_PER_PR}"
            )
        lines.append(
            f"**Result: blocked.** {why}. Fix that, or a maintainer can add the "
            f"`{OVERRIDE_LABEL}` label to merge anyway."
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

    override = OVERRIDE_LABEL in {label.strip() for label in args.labels.split(",")}
    report, failing = render(subs, override)

    print(report)
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        Path(summary).write_text(report, encoding="utf-8")

    return 1 if failing else 0


if __name__ == "__main__":
    sys.exit(main())
