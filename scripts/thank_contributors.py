#!/usr/bin/env python3
"""Thank a contributor once their entry merges, and hand them the listing badge.

The list gets plenty of contributions and few stars: of 43 people whose entries
merged between 2026-09-01 and 2026-10-14, one had starred the repository. Making
a star a condition of merging would buy worthless stars and contradict the
"anyone can contribute" promise, so this asks once more, after the merge;
scripts/star_check.py asks when the pull request opens.
The badge is the part that matters more: a contributor wants their project seen,
and the badge in their README sends readers back to the list.

    python scripts/thank_contributors.py --dry-run         # sweep, print only
    python scripts/thank_contributors.py                   # sweep and post
    python scripts/thank_contributors.py --pr 165          # one pull request
    python scripts/thank_contributors.py --issue 119 --pr 120   # print the body
                                                           # for a form issue

The sweep exists because auto-merge lands contributor pull requests with
GITHUB_TOKEN, and a merge made that way starts no workflow run, so a `closed`
event never fires for the pull requests this is for. A hidden marker in the
comment keeps the sweep and the event path from posting twice.

Needs GITHUB_TOKEN.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

import build_site
import validate

REPO = os.environ.get("GITHUB_REPOSITORY", build_site.REPO)
OWNER = REPO.split("/")[0]
API = "https://api.github.com"
MARKER = "<!-- awesome-mcp-servers:thanks -->"

# Never thank anything merged before this shipped, however wide the window, so a
# first run or a manual dispatch cannot reach back over the whole history.
NOT_BEFORE = datetime(2026, 10, 14, tzinfo=timezone.utc)
LOOKBACK = timedelta(days=3)


def api(method: str, path: str, payload: dict | None = None, token: str | None = None):
    """Call the GitHub REST API as GITHUB_TOKEN, or `token`. Returns (data, error)."""
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(
        f"{API}/{path}",
        data=data,
        method=method,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "awesome-mcp-servers-thanks",
        },
    )
    token = token or os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    if data is not None:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8") or "null"), None
    except urllib.error.HTTPError as exc:
        return None, exc.code
    # URLError and TimeoutError both derive from OSError
    except OSError as exc:
        return None, f"network: {exc}"


def added_entries(patch: str) -> list[tuple[str, str]]:
    """(name, url) for each entry a README diff adds.

    A row whose URL also appears on a removed line is an edit to an existing
    entry, such as a reworded description, not a new listing, so it is left out.
    """
    added: dict[str, tuple[str, str]] = {}
    removed: set[str] = set()
    for line in patch.splitlines():
        if line.startswith(("+++", "---")) or line[:1] not in ("+", "-"):
            continue
        body = line[1:]
        m = validate.ROW_RE.match(body) or validate.BULLET_RE.match(body)
        if not m:
            continue
        url = m.group("url").strip()
        key = validate.normalize_url(url)
        if line[0] == "+":
            added[key] = (m.group("name").strip(), url)
        else:
            removed.add(key)
    return [entry for key, entry in added.items() if key not in removed]


def site_link(name: str) -> str:
    """A link that opens the website already searched down to this entry."""
    return f"{build_site.SITE_URL}?q={urllib.parse.quote(name)}"


def render_thanks(login: str, entries: list[tuple[str, str]], lead: str = "") -> str:
    """The comment body. `lead` prefixes a sentence, as on a form issue."""
    names = [f"**{name}**" for name, _ in entries]
    listed = names[0] if len(names) == 1 else f"{', '.join(names[:-1])} and {names[-1]}"
    verb = "is" if len(names) == 1 else "are"
    first = entries[0][0]
    return "\n".join(
        [
            MARKER,
            f"{lead}Thanks @{login}! {listed} {verb} on the list now, and on the "
            f"[website]({site_link(first)}) within the hour.",
            "",
            "If you want to show it, here is a badge for your README. It links back "
            "to the list, so people who find your project can find the others:",
            "",
            build_site.BADGE_MARKDOWN,
            "",
            "```markdown",
            build_site.BADGE_MARKDOWN,
            "```",
            "",
            f"And if the list is useful to you, a [star]({build_site.REPO_URL}) helps "
            "other people find it. Neither is required.",
        ]
    )


def pr_entries(number: int) -> list[tuple[str, str]]:
    files, err = api("GET", f"repos/{REPO}/pulls/{number}/files?per_page=100")
    if err:
        print(f"  #{number}: could not list files ({err})", file=sys.stderr)
        return []
    for f in files:
        if f.get("filename") == "README.md":
            return added_entries(f.get("patch") or "")
    return []


def already_thanked(number: int) -> bool:
    comments, err = api("GET", f"repos/{REPO}/issues/{number}/comments?per_page=100")
    if err:
        # unknown is treated as thanked: a missed thank-you beats a duplicate
        print(f"  #{number}: could not read comments ({err})", file=sys.stderr)
        return True
    return any(MARKER in (c.get("body") or "") for c in comments)


def skip_reason(pr: dict) -> str | None:
    """Why a merged pull request gets no thank-you, or None if it should."""
    user = pr.get("user") or {}
    if user.get("type") == "Bot":
        # form submissions are opened by the bot; the issue thanks their author
        return "opened by a bot"
    if user.get("login") == OWNER:
        return "opened by the maintainer"
    if (pr.get("base") or {}).get("ref") != "main":
        return "not merged into main"
    return None


def thank_pr(pr: dict, dry_run: bool) -> bool:
    """Post the thank-you on one merged pull request. True if one was posted."""
    number = pr["number"]
    reason = skip_reason(pr)
    if reason:
        print(f"  #{number}: skipped, {reason}")
        return False
    entries = pr_entries(number)
    if not entries:
        print(f"  #{number}: skipped, adds no new entry")
        return False
    if already_thanked(number):
        print(f"  #{number}: skipped, already thanked")
        return False

    body = render_thanks(pr["user"]["login"], entries)
    if dry_run:
        print(
            f"  #{number}: would thank @{pr['user']['login']} for {[n for n, _ in entries]}"
        )
        return False
    _, err = api("POST", f"repos/{REPO}/issues/{number}/comments", {"body": body})
    if err:
        print(f"  #{number}: could not comment ({err})", file=sys.stderr)
        return False
    print(f"  #{number}: thanked @{pr['user']['login']}")
    return True


def recently_merged(now: datetime) -> list[dict]:
    """Pull requests merged into main since the lookback window opened."""
    since = max(now - LOOKBACK, NOT_BEFORE)
    pulls, err = api(
        "GET",
        f"repos/{REPO}/pulls?state=closed&base=main&sort=updated&direction=desc&per_page=100",
    )
    if err:
        print(f"could not list pull requests ({err})", file=sys.stderr)
        return []
    merged = []
    for pr in pulls:
        at = pr.get("merged_at")
        if at and datetime.fromisoformat(at.replace("Z", "+00:00")) >= since:
            merged.append(pr)
    return merged


def issue_body(issue: int, pr: int) -> str | None:
    """The closing comment for a form issue whose pull request merged."""
    data, err = api("GET", f"repos/{REPO}/issues/{issue}")
    if err:
        print(f"could not read issue #{issue} ({err})", file=sys.stderr)
        return None
    entries = pr_entries(pr)
    if not entries:
        return None
    return render_thanks(data["user"]["login"], entries, lead=f"Merged in #{pr}. ")


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--pr", type=int, help="thank one merged pull request")
    ap.add_argument("--issue", type=int, help="print the closing body for a form issue")
    ap.add_argument("--dry-run", action="store_true", help="print, never post")
    args = ap.parse_args()

    if args.issue:
        if not args.pr:
            ap.error("--issue needs --pr")
        body = issue_body(args.issue, args.pr)
        if body is None:
            return 1
        print(body)
        return 0

    if args.pr:
        pr, err = api("GET", f"repos/{REPO}/pulls/{args.pr}")
        if err or not pr.get("merged_at"):
            print(f"#{args.pr} is not a merged pull request ({err or 'open'})")
            return 0
        thank_pr(pr, args.dry_run)
        return 0

    candidates = recently_merged(datetime.now(timezone.utc))
    print(f"{len(candidates)} pull request(s) merged in the window")
    posted = sum(thank_pr(pr, args.dry_run) for pr in candidates)
    print(f"posted {posted} thank-you comment(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
