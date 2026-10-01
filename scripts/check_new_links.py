#!/usr/bin/env python3
"""Check only the links a change introduces.

The full-file link check is the right gate for `main`, and the wrong one for a
pull request. One dead link anywhere in the README fails every incoming
submission regardless of what it touched, which has now blocked six innocent
contributor pull requests across three separate rotted entries (#110, #111,
#125, #127, #128, and sms-florin before them).

This is the link-side counterpart to `validate.py --baseline`: report everything,
but only fail on URLs absent from the base ref. Tolerances and host exclusions
are read out of `lychee.toml` rather than restated, so this and CI cannot drift
apart on what counts as reachable.

    python scripts/check_new_links.py --base-ref origin/main

Exit code 0 = no new dead link, 1 = at least one.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import re
import subprocess
import sys
import tomllib
import urllib.error
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LYCHEE_CONFIG = REPO_ROOT / "lychee.toml"

# The same inputs the Check links job passes to lychee.
SCANNED = ("README.md", "CONTRIBUTING.md", "SECURITY.md", "CHANGELOG.md")

# Shape of an acceptable git ref. Must not start with a dash, or git would read
# it as an option instead of a revision.
REF_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/~^@{}-]*$")

LINK_RE = re.compile(r"\]\((https?://[^)\s]+)\)")
FENCE_RE = re.compile(r"^\s*```")
CODE_SPAN_RE = re.compile(r"`[^`]*`")

DEFAULT_ACCEPT = (200, 206, 403, 429)
UA = (
    "Mozilla/5.0 (compatible; awesome-mcp-servers link check; "
    "+https://github.com/Sagargupta16/awesome-mcp-servers)"
)


def load_lychee_settings() -> tuple[set[int], list[re.Pattern], int]:
    """Read accept codes, host exclusions and timeout out of lychee.toml."""
    if not LYCHEE_CONFIG.exists():
        return set(DEFAULT_ACCEPT), [], 30
    with LYCHEE_CONFIG.open("rb") as fh:
        cfg = tomllib.load(fh)
    accept = {int(c) for c in cfg.get("accept", DEFAULT_ACCEPT)}
    excludes = [re.compile(p) for p in cfg.get("exclude", [])]
    return accept, excludes, int(cfg.get("timeout", 30))


def links_in(text: str) -> set[str]:
    """Every http(s) link target in a markdown document.

    Fenced blocks and inline code spans are illustrations, not links, and the
    README's format example contains a literal `URL` placeholder.
    """
    found: set[str] = set()
    in_fence = False
    for raw in text.splitlines():
        if FENCE_RE.match(raw):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        found.update(LINK_RE.findall(CODE_SPAN_RE.sub("", raw)))
    return found


def links_at_ref(ref: str) -> set[str] | None:
    """Links across the scanned files at `ref`, or None if the ref is unreadable."""
    if not REF_RE.match(ref):
        print(f"error: {ref!r} is not a valid git ref", file=sys.stderr)
        return None

    found: set[str] = set()
    for name in SCANNED:
        proc = subprocess.run(
            ["git", "show", f"{ref}:{name}"],
            capture_output=True,
            check=False,
            shell=False,
        )
        if proc.returncode != 0:
            # A file that does not exist at the base is new, so everything in it
            # is new. That is correct, not an error.
            continue
        found |= links_in(proc.stdout.decode("utf-8", "replace"))
    return found


def links_at_head() -> set[str]:
    found: set[str] = set()
    for name in SCANNED:
        path = REPO_ROOT / name
        if path.exists():
            found |= links_in(path.read_text(encoding="utf-8"))
    return found


def check(url: str, timeout: int) -> tuple[str, object]:
    request = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return url, response.status
    except urllib.error.HTTPError as exc:
        return url, exc.code
    # URLError and TimeoutError both derive from OSError, so this covers all three.
    except OSError as exc:
        return url, f"unreachable: {type(exc).__name__}"


def partition_new(base_ref: str, excludes) -> tuple[list[str], list[str]]:
    """Split the links this change adds into (to check, skipped by lychee.toml)."""
    before = links_at_ref(base_ref)
    if before is None:
        print("Treating every link as new, since the base ref could not be read.")
        before = set()

    new = sorted(links_at_head() - before)
    skipped = [u for u in new if any(p.search(u) for p in excludes)]
    excluded = set(skipped)
    return [u for u in new if u not in excluded], skipped


def check_all(urls, accept: set[int], timeout: int) -> list[tuple[object, str]]:
    """Check every URL concurrently, printing each verdict, and return the dead."""
    dead: list[tuple[object, str]] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        futures = [pool.submit(check, u, timeout) for u in urls]
        for future in concurrent.futures.as_completed(futures):
            url, status = future.result()
            ok = isinstance(status, int) and status in accept
            print(f"  {'ok  ' if ok else 'DEAD'}  {status}  {url}")
            if not ok:
                dead.append((status, url))
    return dead


def report_dead(dead) -> None:
    print(f"\n{len(dead)} new link(s) are dead:", file=sys.stderr)
    for status, url in dead:
        print(f"  {status}  {url}", file=sys.stderr)
    print(
        "\nOnly links this change introduces are checked here. A dead link "
        "already on the base branch is reported by the full sweep on main, "
        "not charged to this pull request.",
        file=sys.stderr,
    )


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--base-ref", default="origin/main", help="ref to compare against")
    args = ap.parse_args()

    accept, excludes, timeout = load_lychee_settings()
    to_check, skipped = partition_new(args.base_ref, excludes)

    if not to_check:
        print(f"No new links to check against {args.base_ref}.")
        if skipped:
            print(f"{len(skipped)} new link(s) on an excluded host, not checked.")
        return 0

    print(f"Checking {len(to_check)} new link(s) against {args.base_ref}.\n")
    dead = check_all(to_check, accept, timeout)

    if skipped:
        print(f"\n{len(skipped)} new link(s) on a host lychee.toml excludes:")
        for url in skipped:
            print(f"  skipped  {url}")

    if dead:
        report_dead(dead)
        return 1

    print("\nEvery new link resolves.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
