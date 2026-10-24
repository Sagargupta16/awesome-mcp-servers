#!/usr/bin/env python3
"""Quality gate for newly submitted entries.

Reads the rows a pull request ADDS to README.md, looks each one up on GitHub,
and reports what the maintainer would otherwise have to check by hand: stars,
licence, last push, archived state, repo age, and whether the repo actually
contains an MCP implementation rather than just a manifest.

A `Remote` row is a hosted server with no public source, so it is judged on its
documentation and its endpoint instead: the endpoint the docs name is probed, and
a maintainer confirms the rest.

Hard failures block the pull request. Soft warnings are printed for a human to
judge. Both land in the GitHub Actions step summary.

    python scripts/check_submission.py --base-ref origin/main

Set GITHUB_TOKEN to raise the API rate limit from 60 to 5000 requests/hour.
"""

from __future__ import annotations

import argparse
import base64
import http.client
import ipaddress
import json
import os
import re
import sys
import threading
import tomllib
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

import gitref

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

# The Language value for a hosted server with no public source.
REMOTE = "Remote"

PROBE_TIMEOUT = 20  # seconds for one whole request
SOCKET_TIMEOUT = 5  # seconds for each connect or read inside it
MAX_PROBES = 3
MAX_PAGE_BYTES = 2_000_000
USER_AGENT = (
    "Mozilla/5.0 (compatible; awesome-mcp-servers-submission-check; "
    "+https://github.com/Sagargupta16/awesome-mcp-servers)"
)
# A probe accepts exactly what the MCP spec says a client must: a server on the
# same host as its website served the website to an Accept that included HTML.
MCP_ACCEPT = "application/json, text/event-stream"
PAGE_ACCEPT = "text/html, */*;q=0.8"
INITIALIZE = json.dumps(
    {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2025-06-18",
            "capabilities": {},
            "clientInfo": {
                "name": "awesome-mcp-servers-submission-check",
                "version": "1",
            },
        },
    }
).encode("utf-8")

# Statuses that mean nothing is served at that URL, and the content types an MCP
# server answers `initialize` with. See speaks_mcp().
GONE = {404, 410}
MCP_TYPES = {"application/json", "text/event-stream"}

# Any https URL. Placeholders such as `https://{host}/mcp` fail the host part.
URL_RE = re.compile(r"https://[\w.-]+(?::\d+)?(?:/[^\s\"'<>`(){}\[\]\\|]*)?")

REMOTE_REVIEW = (
    "Hosted server with no public source, so a person should confirm what CI "
    "cannot: the documentation is the operator's own, and it names the "
    "endpoint, the authentication and the tools."
)

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
# The captured group is deliberately `[^<]*` with no surrounding `\s*`: pairing a
# lazy quantifier with whitespace classes that can match the same characters is
# what makes a pattern backtrack super-linearly. Trimming happens in Python.
POM_LICENCE_RE = re.compile(
    r"<licenses?>.*?<name>([^<]*)</name>", re.DOTALL | re.IGNORECASE
)

# Re-exported so the pattern has one definition for all three gate scripts.
REF_RE = gitref.REF_RE

# Root filenames that count as install and usage documentation.
README_NAMES = {"readme.md", "readme.rst", "readme", "readme.txt"}

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
    # OSError covers URLError, timeouts and a dropped connection, which used to
    # escape as RemoteDisconnected and crash the run.
    except (OSError, http.client.HTTPException) as exc:
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


def _licence_from_json(text: str) -> str | None:
    data = json.loads(text)
    if not isinstance(data, dict):
        return None
    return _first_licence_string(data.get("license") or data.get("licenses"))


def _licence_from_toml(text: str) -> str | None:
    data = tomllib.loads(text)
    # `[project]` is PEP 621, `[package]` is Cargo.
    for table in ("project", "package"):
        section = data.get(table)
        if isinstance(section, dict):
            found = _first_licence_string(section.get("license"))
            if found:
                return found
    return None


def _licence_from_pom(text: str) -> str | None:
    match = POM_LICENCE_RE.search(text)
    return match.group(1).strip() if match else None


MANIFEST_READERS = (
    (".json", _licence_from_json),
    (".toml", _licence_from_toml),
    (".xml", _licence_from_pom),
)


def parse_manifest_licence(filename: str, text: str) -> str | None:
    """Read the declared licence out of one manifest, or None.

    Parsed rather than pattern-matched: a regex over the raw text reads a nested
    `"license"` key belonging to some other object as the package's own.
    """
    name = filename.lower()
    try:
        for suffix, reader in MANIFEST_READERS:
            if name.endswith(suffix):
                return reader(text)
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
        text = file_text(f"repos/{slug}/contents/{name}")
        licence = parse_manifest_licence(name, text) if text else None
        if licence:
            return name, licence
    return None, None


def file_text(path: str) -> str | None:
    """Decode a file from the contents API, or None when there is no such file."""
    data, _ = gh_api(path)
    if not isinstance(data, dict) or not data.get("content"):
        return None
    try:
        return base64.b64decode(data["content"]).decode("utf-8", "replace")
    except ValueError:
        return None


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

    `base_ref` arrives from a command line, so it is checked against the shape of
    a git ref first. Nothing is run through a shell, but a value beginning with
    `-` would still be read by git as an option rather than a revision.
    """
    if not gitref.is_valid_ref(base_ref):
        print(
            f"error: {base_ref!r} is not a valid git ref for --base-ref",
            file=sys.stderr,
        )
        return []

    text, detail = gitref.show(base_ref, "README.md")
    if text is None:
        print(
            f"warning: could not read README.md at {base_ref}: {detail}",
            file=sys.stderr,
        )
        return []

    before = parse_rows(text)
    after = parse_rows(Path("README.md").read_text(encoding="utf-8"))
    return [sub for key, sub in after.items() if key not in before]


def inspect(sub: Submission) -> None:
    if sub.third == REMOTE:
        inspect_remote(sub)
        return

    m = GH_REPO_RE.match(sub.url)
    if not m:
        sub.soft.append(
            "Not a plain GitHub repository URL, so it cannot be checked "
            "automatically. A maintainer must verify it by hand."
        )
        return

    slug = f"{m.group('owner')}/{m.group('repo')}"
    data = lookup_repo(sub, slug)
    if data is None:
        return

    licence = (data.get("license") or {}).get("spdx_id")
    if licence in (None, "", "NOASSERTION"):
        check_unclassified_licence(sub, slug)
    stale_days = days_since(data["pushed_at"])
    if stale_days > STALE_DAYS:
        sub.hard.append(
            f"Last push was {stale_days} days ago, over the {STALE_DAYS}-day "
            f"maintenance threshold."
        )

    check_implementation(sub, slug)

    # Star count and repo age are reported in the facts table above as context.
    # Neither is a bar: popularity is not quality, and a new project that works,
    # is licensed and is documented belongs on the list as much as a famous one.


def days_since(stamp: str) -> int:
    then = datetime.fromisoformat(stamp.replace("Z", "+00:00"))
    return (datetime.now(timezone.utc) - then).days


def lookup_repo(sub: Submission, slug: str) -> dict | None:
    """Fetch a repository, record its facts, and block what no entry may be.

    Returns None when there is nothing further to inspect.
    """
    data, err = gh_api(f"repos/{slug}")
    if data is None:
        if err == 404:
            sub.hard.append(
                f"`{slug}` returns 404. The repository is private, renamed, or deleted."
            )
        else:
            sub.soft.append(f"Could not reach the GitHub API for `{slug}` ({err}).")
        return None

    stale_days = days_since(data["pushed_at"])
    age_days = days_since(data["created_at"])
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
    return data


def inspect_remote(sub: Submission) -> None:
    """Judge a hosted server on its documentation and its endpoint.

    There is no source, so the licence, 180-day and implementation checks do not
    apply: nothing is distributed to license, a documentation repository can sit
    quiet while the service runs, and a README beside a `server.json` is exactly
    what one looks like. A missing repository, an archive or a fork still blocks,
    and every `Remote` entry waits for a maintainer.
    """
    sub.soft.append(REMOTE_REVIEW)

    m = GH_REPO_RE.match(sub.url)
    if not m:
        status, _, page = request(sub.url, read=True)
        if status is None or status >= 400:
            sub.soft.append(
                f"Could not read the documentation page "
                f"({page or f'HTTP {status}'}), so no endpoint was looked for."
            )
            return
        check_endpoint(sub, page)
        return

    slug = f"{m.group('owner')}/{m.group('repo')}"
    if lookup_repo(sub, slug) is None:
        return
    readme = file_text(f"repos/{slug}/readme")
    if readme is None:
        sub.hard.append(
            "No README in the repository. For a hosted server the README is the "
            "documentation, so CONTRIBUTING.md requires one."
        )
    manifest = file_text(f"repos/{slug}/contents/server.json") or ""
    check_endpoint(sub, f"{readme or ''}\n{manifest}")


def request(url: str, method: str = "GET", read: bool = False) -> tuple:
    """Send one unauthenticated request: (status, content type, text).

    `text` is the body when `read` is set, and why there was no answer when the
    status is None. A POST carries an MCP `initialize`. The body is only read when
    asked for: an SSE endpoint streams for as long as it is held open, so a probe
    closes the connection as soon as the status line arrives.

    urllib's timeout applies to each socket operation and to each address a host
    resolves to, so a host whose IPv6 addresses hang held one probe for over a
    minute. The request runs on a daemon thread with one deadline for all of it.
    """
    result = [None, "", f"no answer within {PROBE_TIMEOUT}s"]

    def run() -> None:
        result[:] = _request(url, method, read)

    worker = threading.Thread(target=run, daemon=True)
    worker.start()
    worker.join(PROBE_TIMEOUT)
    return tuple(result)


def _request(url: str, method: str, read: bool) -> tuple:
    data = INITIALIZE if method == "POST" else None
    headers = {"User-Agent": USER_AGENT, "Accept": PAGE_ACCEPT if read else MCP_ACCEPT}
    if data:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=SOCKET_TIMEOUT) as resp:
            body = resp.read(MAX_PAGE_BYTES).decode("utf-8", "replace") if read else ""
            return resp.status, resp.headers.get_content_type(), body
    except urllib.error.HTTPError as exc:
        ctype = exc.headers.get_content_type() if exc.headers else ""
        return exc.code, ctype, ""
    except (OSError, ValueError, http.client.HTTPException) as exc:
        return None, "", str(getattr(exc, "reason", exc))


def probe(url: str) -> tuple:
    """How an endpoint answers, as `request` returns it.

    A POST-only route answers GET with 404 and an SSE route answers POST with
    405, so a 404 or 405 to the POST is retried as a GET before it counts.
    """
    answer = request(url, "POST")
    if answer[0] in (404, 405):
        answer = request(url)
    return answer


def speaks_mcp(status: int | None, ctype: str) -> bool:
    """True when an answer came from a server rather than a 404 or a web page.

    An error other than 404 or 410 counts: 401 is what a server says to a request
    with no token. A success counts only as JSON or an event stream, since a 200
    in HTML is a web page that happens to sit at an `/mcp` path.
    """
    if status is None or status in GONE:
        return False
    return status >= 300 or ctype in MCP_TYPES


def _public_host(host: str) -> bool:
    """False for placeholders and addresses no hosted server would publish."""
    if "." not in host or "example" in host.split("."):
        return False
    try:
        ipaddress.ip_address(host)
    except ValueError:
        return True
    return False


def _endpoint_rank(host: str, path: str) -> int:
    """Lower is likelier: an `mcp.` host, then an API host or path, then the rest.

    An `mcp.` host has to be a subdomain. `mcp.so` is a registry, and a README's
    badge linking it would otherwise use up the probes before the endpoint.
    """
    if host.startswith("mcp.") and host.count(".") >= 2:
        return 0
    if host.startswith("api.") or "/api/" in path.lower():
        return 1
    return 2


def find_endpoints(text: str, own_url: str) -> list:
    """MCP endpoint URLs the documentation names, likeliest first.

    A hosted endpoint usually lives on an `mcp.` host or at a path ending in
    `/mcp` or `/sse`. The entry's own URL is the documentation, not the endpoint,
    even when its path also ends in `/mcp`. Ranking matters because only the
    first few are probed, and Noveum's page names its locale copies at `/de/mcp`
    before its endpoint at `/api/mcp`.
    """
    own = own_url.rstrip("/").lower()
    found: dict = {}
    for match in URL_RE.finditer(text):
        # A fragment names a spot on a page, not a different URL to probe.
        url = match.group(0).split("#")[0].rstrip(".,;:!?")
        parts = urllib.parse.urlsplit(url)
        host = (parts.hostname or "").lower()
        last = parts.path.rstrip("/").rsplit("/", 1)[-1].lower()
        if url.rstrip("/").lower() == own or not _public_host(host):
            continue
        rank = _endpoint_rank(host, parts.path)
        # Docs often name just the host. Replicate's root is a landing page while
        # its server answers at /sse and /mcp, so try those paths first.
        if rank == 0 and parts.path in ("", "/"):
            base = url.rstrip("/")
            for path in ("/mcp", "/sse"):
                found.setdefault(f"{base}{path}", rank)
        if rank == 0 or last in ("mcp", "sse"):
            found.setdefault(url, rank)
    return sorted(found, key=found.__getitem__)


def check_endpoint(sub: Submission, docs: str) -> None:
    """Probe the endpoint the documentation names, and say what answered."""
    endpoints = find_endpoints(docs, sub.url)[:MAX_PROBES]
    if not endpoints:
        sub.soft.append(
            "No MCP endpoint URL found in the documentation. A `Remote` entry's "
            "docs must name it; confirm by hand, since a page rendered by "
            "JavaScript hides it from this check."
        )
        return

    tried = []
    for url in endpoints:
        status, ctype, why = probe(url)
        answer = (
            f"HTTP {status}, {ctype}" if status is not None else f"no answer: {why}"
        )
        if speaks_mcp(status, ctype):
            sub.facts["endpoint"] = f"{url} ({answer})"
            return
        tried.append(f"`{url}` ({answer})")
    sub.soft.append(
        f"No URL the documentation names answered like an MCP server: "
        f"{', '.join(tried)}. A listed hosted server must be live; confirm the "
        f"endpoint by hand."
    )


def check_unclassified_licence(sub: Submission, slug: str) -> None:
    """Resolve a licence GitHub could not classify, or block if there is none.

    "NOASSERTION" means GitHub found a licence file it could not classify, which
    is a different thing from having none. The official MCP SDKs all report it.
    Only a genuinely absent licence blocks.
    """
    lic_file, lic_err = gh_api(f"repos/{slug}/license")
    if isinstance(lic_file, dict) and lic_file.get("name"):
        sub.facts["license"] = f"{lic_file['name']} (unrecognised by GitHub)"
        sub.soft.append(
            f"GitHub cannot classify `{lic_file['name']}`, so it reports no SPDX "
            f"licence. Confirm by hand that the terms are open source. Common for "
            f"a vendor repo with a customised header, suspicious for a small one."
        )
        return

    man_file, man_lic = manifest_licence(slug)
    if not man_lic:
        sub.hard.append(
            f"No licence anywhere ({lic_err}): no `LICENSE` file at the root and no "
            f"licence field in a package manifest. CONTRIBUTING.md requires a "
            f"clearly stated licence."
        )
        return

    sub.facts["license"] = f"{man_lic} (declared in {man_file})"
    if not is_open_source(man_lic):
        sub.hard.append(
            f"`{man_file}` declares `{man_lic}`, which states that the terms are not "
            f"open source rather than naming a licence. CONTRIBUTING.md requires an "
            f"open-source licence."
        )
        return
    sub.soft.append(
        f"No `LICENSE` file at the repository root; the licence is declared as "
        f"`{man_lic}` in `{man_file}`. CONTRIBUTING.md accepts that, but a root "
        f"`LICENSE` file is what GitHub reads. Confirm the terms."
    )


def check_implementation(sub: Submission, slug: str) -> None:
    """Look for a README and for evidence the repository holds real source."""
    tree, tree_err = gh_api(f"repos/{slug}/contents")
    if not isinstance(tree, list):
        if tree_err:
            sub.soft.append(
                f"Could not list the repository root ({tree_err}); MCP implementation "
                f"not verified."
            )
        return

    names = {f["name"].lower() for f in tree}
    if not names & README_NAMES:
        sub.hard.append(
            "No README at the repository root. CONTRIBUTING.md requires install "
            "and usage documentation."
        )

    # Dotfiles and dot-directories are tooling, not implementation, and they used
    # to defeat both checks below: `usenetstate/statsnet-mcp` passed with nothing
    # but manifests because a `.gitignore` broke the subset test and a
    # `.cursor-plugin` directory counted as somewhere source might live.
    payload = {n for n in names if not n.startswith(".")}
    source_dirs = [
        f["name"] for f in tree if f["type"] == "dir" and not f["name"].startswith(".")
    ]

    if payload and payload <= MANIFEST_ONLY and not source_dirs:
        sub.hard.append(
            f"The repository root contains only {sorted(payload)} -- a README plus "
            f"registry manifests, with no MCP implementation. Publish the server "
            f"source, or submit the repository that holds it. If the server is "
            f"hosted and its source is closed, list it with `{REMOTE}` as the "
            f"language instead, which CONTRIBUTING.md covers."
        )
        return

    # The check above only catches roots made entirely of known manifest names, so
    # an unrecognised file slips past it. Look for a positive signal instead: a
    # build manifest, or a directory that could hold source.
    if not (payload & PROJECT_MARKERS) and not source_dirs:
        sub.soft.append(
            f"No build manifest or source directory at the repository root, only "
            f"{sorted(payload)}. Confirm by hand that this holds a real MCP "
            f"implementation and is not a listing stub."
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

    # Adding several servers at once is a process preference, not a defect in the
    # entries. It is surfaced for the maintainer and never fails the build: a
    # contributor whose entries are all fine should not see a red check.
    if servers > MAX_SERVERS_PER_PR:
        lines.append("> [!NOTE]")
        lines.append(
            f"> This adds {servers} entries. CONTRIBUTING.md prefers one server per "
            f"pull request, so each can be reviewed and reverted on its own. That is "
            f"a preference, not a requirement, and it does not fail this check -- a "
            f"maintainer may still ask you to split it."
        )
        lines.append("")

    for s in subs:
        lines.extend(render_submission(s))

    # Only a real defect in a submitted entry fails the check.
    failing = hard_total > 0 and not override
    lines.append(render_result(subs, hard_total, override, failing))

    return "\n".join(lines) + "\n", failing


def render_submission(s: Submission) -> list:
    """The per-entry block: facts table, then blocking and advisory findings."""
    lines = [f"### {s.name}", f"{s.url}", ""]
    if s.facts:
        lines.append("| Check | Value |")
        lines.append("|-------|-------|")
        lines.extend(f"| {k} | {v} |" for k, v in s.facts.items())
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
    return lines


def render_result(subs: list, hard_total: int, override: bool, failing: bool) -> str:
    if override:
        return f"Gate bypassed by the `{OVERRIDE_LABEL}` label."
    if not failing:
        return "**Result: passed.** No blocking problems."
    entries = "entry" if len(subs) == 1 else "entries"
    return (
        f"**Result: blocked.** {hard_total} blocking problem(s) across "
        f"{len(subs)} {entries}. Fix those, or a maintainer can add the "
        f"`{OVERRIDE_LABEL}` label to merge anyway."
    )


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
        with Path(summary).open("a", encoding="utf-8") as fh:
            fh.write(report)

    return 1 if failing else 0


if __name__ == "__main__":
    sys.exit(main())
