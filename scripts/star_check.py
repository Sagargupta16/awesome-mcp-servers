#!/usr/bin/env python3
"""Ask pull request authors to star the repository, and let a star skip the wait.

A pull request from someone who has not starred gets the `missing-star` label
and one comment asking. When that person stars, the label comes off, the
comment turns into a thank-you, and any of their pull requests that were held
with `needs-review` switch to auto-merge instead. auto-merge.yml and
issue-to-pr.yml ask `--starred` the same question before they hold one.

A star never gets an entry past a failing check. It only skips the maintainer
review that the submission check asks for on `Remote` entries and on findings
it cannot settle itself.

    python scripts/star_check.py                   # the triggering event, or else
                                                   # every open pull request
    python scripts/star_check.py --starred LOGIN   # exit 0 if LOGIN starred
    python scripts/star_check.py --dry-run         # say what would change

Whether someone starred comes from the repository's own stargazer list when the
token may read it (STARGAZERS_TOKEN, else GITHUB_TOKEN), and otherwise from the
person's public starred list, newest first. That fallback misses a star buried
under thousands of newer ones; a miss only means the pull request waits for a
maintainer, which is what it would have done anyway.

Needs GITHUB_TOKEN.
"""

from __future__ import annotations

import argparse
import functools
import json
import os
import re
import sys
import urllib.parse
from pathlib import Path

from thank_contributors import OWNER, REPO, api

LABEL = "missing-star"
REVIEW_LABEL = "needs-review"
MARKER = "<!-- awesome-mcp-servers:star-check -->"
BOT = "github-actions[bot]"
REPO_URL = f"https://github.com/{REPO}"

# Mirrors auto-merge.yml: a pull request touching anything else is never merged
# unattended, star or not, and neither is one a maintainer has stopped.
AUTO_MERGE_FILES = {"README.md", "CHANGELOG.md"}
STOP_LABELS = {"no-auto-merge", "maintainer-override"}

# The fallback reads newest stars first; past this many pages it gives up.
MAX_PAGES = 20

# GitHub's own rule for usernames: letters, digits and single hyphens, at most 39.
LOGIN_RE = re.compile(r"[A-Za-z0-9](?:-?[A-Za-z0-9]){0,38}")


def seg(value: object) -> str:
    """One URL path segment, with anything that could end or climb it escaped.

    Pull request numbers come from the event file, which is data: quoting them
    means no value can turn `issues/N/labels` into a different API path.
    """
    return urllib.parse.quote(str(value), safe="")


@functools.cache
def stargazers() -> frozenset[str] | None:
    """Lowercased logins from the repository's own list, or None if it is closed."""
    token = os.environ.get("STARGAZERS_TOKEN") or None
    names: set[str] = set()
    for page in range(1, MAX_PAGES + 1):
        data, err = api(
            "GET", f"repos/{REPO}/stargazers?per_page=100&page={page}", token=token
        )
        if err:
            print(
                f"  stargazer list unavailable ({err}); using starred lists",
                file=sys.stderr,
            )
            return None
        names |= {user["login"].lower() for user in data}
        if len(data) < 100:
            break
    return frozenset(names)


@functools.cache
def repo_id() -> int | None:
    repo, err = api("GET", f"repos/{REPO}")
    return None if err else repo["id"]


def has_starred(login: str) -> bool:
    """Whether `login` has starred the repository, as far as the API can tell.

    `login` reaches this from the command line, so anything that is not a GitHub
    login is refused before it can become part of an API path: `../` in it would
    walk the request somewhere else under the workflow's token.
    """
    if not LOGIN_RE.fullmatch(login):
        print(f"  {login!r} is not a GitHub login", file=sys.stderr)
        return False
    names = stargazers()
    if names is not None:
        return login.lower() in names
    target = repo_id()
    user = urllib.parse.quote(login, safe="")
    for page in range(1, MAX_PAGES + 1):
        starred, err = api(
            "GET",
            f"users/{user}/starred?sort=created&direction=desc&per_page=100&page={page}",
        )
        if err:
            print(f"  could not read {login}'s stars ({err})", file=sys.stderr)
            return False
        if any(r.get("id") == target for r in starred):
            return True
        if len(starred) < 100:
            return False
    return False


def ask_body(login: str) -> str:
    return "\n".join(
        [
            MARKER,
            f"Thanks for the submission, @{login}!",
            "",
            "It looks like you haven't starred this repository yet. Every entry is "
            "checked by CI and by hand, and a star is the one thing the list asks "
            "for in return: it is how other people find it. You can star it at the "
            f"top of {REPO_URL}, or from a terminal:",
            "",
            "```bash",
            f"gh api -X PUT /user/starred/{REPO}",
            "```",
            "",
            f"Once you have, the `{LABEL}` label comes off by itself, and if this "
            f"pull request is waiting for a maintainer (`{REVIEW_LABEL}`) it merges "
            "itself as soon as the checks pass instead. If you already starred and "
            "this has not noticed, a maintainer will sort it out.",
        ]
    )


THANKS_BODY = "\n".join(
    [MARKER, f"Thank you for the star! The `{LABEL}` label has been removed."]
)


def our_comment(number: int) -> dict | None:
    """The comment this script posted on a pull request, if any."""
    comments, err = api(
        "GET", f"repos/{REPO}/issues/{seg(number)}/comments?per_page=100"
    )
    if err:
        print(f"  #{number}: could not read comments ({err})", file=sys.stderr)
        return None
    for c in comments:
        if (c.get("user") or {}).get("login") == BOT and MARKER in (
            c.get("body") or ""
        ):
            return c
    return None


def upsert_comment(number: int, body: str, create: bool) -> None:
    """Write `body` into our comment, creating it only when `create` is set.

    An unchanged body is left alone, so a re-run sends nobody a notification.
    """
    existing = our_comment(number)
    if existing:
        if existing.get("body") != body:
            api(
                "PATCH",
                f"repos/{REPO}/issues/comments/{seg(existing['id'])}",
                {"body": body},
            )
    elif create:
        api("POST", f"repos/{REPO}/issues/{seg(number)}/comments", {"body": body})


def labels_of(pr: dict) -> set[str]:
    return {label["name"] for label in pr.get("labels") or []}


def flag(pr: dict, dry_run: bool) -> None:
    number, login = pr["number"], pr["user"]["login"]
    print(f"  #{number}: {login} has not starred, labelling {LABEL}")
    if dry_run:
        return
    api("POST", f"repos/{REPO}/issues/{seg(number)}/labels", {"labels": [LABEL]})
    upsert_comment(number, ask_body(login), create=True)


def clear(pr: dict, dry_run: bool) -> None:
    number = pr["number"]
    print(f"  #{number}: {pr['user']['login']} has starred")
    if dry_run:
        return
    if LABEL in labels_of(pr):
        # a 404 means someone removed it by hand already, which is the goal
        api("DELETE", f"repos/{REPO}/issues/{seg(number)}/labels/{LABEL}")
    # only a pull request that was asked gets the thank-you
    upsert_comment(number, THANKS_BODY, create=False)


def may_auto_merge(pr: dict) -> bool:
    """The same file and label rules auto-merge.yml applies."""
    if labels_of(pr) & STOP_LABELS:
        return False
    number = pr["number"]
    files, err = api("GET", f"repos/{REPO}/pulls/{seg(number)}/files?per_page=100")
    if err:
        print(f"  #{number}: could not list files ({err})", file=sys.stderr)
        return False
    return {f["filename"] for f in files} <= AUTO_MERGE_FILES


def release(pr: dict, dry_run: bool) -> None:
    """Swap `needs-review` for auto-merge on a starrer's held pull request."""
    number = pr["number"]
    if not may_auto_merge(pr):
        print(f"  #{number}: stays with a maintainer (files or labels)")
        return
    print(f"  #{number}: starred, so auto-merge replaces {REVIEW_LABEL}")
    if dry_run:
        return
    api("DELETE", f"repos/{REPO}/issues/{seg(number)}/labels/{REVIEW_LABEL}")
    data, err = api(
        "POST",
        "graphql",
        {
            "query": "mutation($id: ID!) { enablePullRequestAutoMerge("
            "input: {pullRequestId: $id, mergeMethod: SQUASH}) { clientMutationId } }",
            "variables": {"id": pr["node_id"]},
        },
    )
    if err or (data or {}).get("errors"):
        print(
            f"  #{number}: could not enable auto-merge ({err or data['errors']})",
            file=sys.stderr,
        )


def skip_reason(pr: dict) -> str | None:
    user = pr.get("user") or {}
    if user.get("type") == "Bot":
        return "opened by a bot"
    if user.get("login") == OWNER:
        return "the maintainer's own"
    return None


def check(pr: dict, dry_run: bool) -> None:
    reason = skip_reason(pr)
    if reason:
        print(f"  #{pr['number']}: skipped, {reason}")
        return
    if has_starred(pr["user"]["login"]):
        clear(pr, dry_run)
        if REVIEW_LABEL in labels_of(pr):
            release(pr, dry_run)
    else:
        flag(pr, dry_run)


def open_prs() -> list[dict]:
    prs, err = api("GET", f"repos/{REPO}/pulls?state=open&per_page=100")
    if err:
        print(f"error: could not list open pull requests ({err})", file=sys.stderr)
        return []
    return prs


def on_star(login: str, dry_run: bool) -> None:
    """Clear the label from the starrer's pull requests and release held ones.

    The `watch` event is the proof of the star, so nothing is looked up.
    """
    theirs = [pr for pr in open_prs() if pr["user"]["login"].lower() == login.lower()]
    if not theirs:
        print(f"  {login} starred; no open pull request of theirs")
    for pr in theirs:
        if LABEL in labels_of(pr):
            clear(pr, dry_run)
        if REVIEW_LABEL in labels_of(pr):
            release(pr, dry_run)


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--starred", metavar="LOGIN", help="exit 0 if LOGIN has starred")
    ap.add_argument("--dry-run", action="store_true", help="print, never write")
    args = ap.parse_args()

    if args.starred:
        return 0 if has_starred(args.starred) else 1

    event_name = os.environ.get("GITHUB_EVENT_NAME", "")
    event_path = os.environ.get("GITHUB_EVENT_PATH")
    event = (
        json.loads(Path(event_path).read_text(encoding="utf-8")) if event_path else {}
    )

    if event_name == "watch":
        on_star(event["sender"]["login"], args.dry_run)
    elif event_name == "pull_request_target":
        check(event["pull_request"], args.dry_run)
    else:
        # a dispatch, or a local run, has no pull request: check every open one
        for pr in open_prs():
            check(pr, args.dry_run)
    return 0


if __name__ == "__main__":
    sys.exit(main())
