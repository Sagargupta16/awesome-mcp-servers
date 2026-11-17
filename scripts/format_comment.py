#!/usr/bin/env python3
"""Tell a pull request author what the format check found, in one comment.

`Validate format` in lint.yml fails a pull request that breaks the list's rules,
but its findings sit in the check log, which most submitters never open. This
posts them on the pull request instead: one marker comment listing the problems
the pull request adds, rewritten when a push changes them, and turned into a
short "passes now" note once they are gone. A pull request with nothing new
wrong gets no comment at all.

It runs from main on pull_request_target, so nothing from the pull request
executes or is even fetched: this script reads the pull request's README.md as
text through the contents API, at the head commit, and checks it with main's
validate.py.

    python scripts/format_comment.py            # the triggering pull request, or
                                                # every open pull request
    python scripts/format_comment.py --dry-run  # print the comment, never write

Needs GITHUB_TOKEN.
"""

from __future__ import annotations

import argparse
import base64
import binascii
import json
import os
import re
import sys
from pathlib import Path

import validate
from star_check import BOT, seg
from thank_contributors import REPO, api

MARKER = f"<!-- {REPO.split('/')[-1]}:format-check -->"

# A long list buries the first fix; past this many the comment points at the log.
MAX_SHOWN = 20

# A head commit sha, which is all that ever goes into the contents API query.
SHA_RE = re.compile(r"[0-9a-f]{40}")


def head_readme(sha: str) -> tuple[str | None, str]:
    """(README.md at commit `sha`, error), read as data through the contents API.

    The pull request's commits are reachable from this repository through its
    pull request ref, so a fork's head reads here without fetching anything.
    """
    data, err = api("GET", f"repos/{REPO}/contents/README.md?ref={sha}")
    if err or not isinstance(data, dict) or data.get("encoding") != "base64":
        return None, str(err or "no base64 content")
    try:
        return base64.b64decode(data["content"]).decode("utf-8", "replace"), ""
    except (binascii.Error, KeyError) as exc:
        return None, f"undecodable content ({exc})"


def new_problems(head_text: str, base_text: str) -> list[str]:
    """Problems in `head_text` that `base_text` does not already have.

    Matched by validate.problem_key, so a row added above an old problem does
    not make that problem look new.
    """
    head, _, _ = validate.run_checks(head_text.splitlines(keepends=True))
    base, _, _ = validate.run_checks(base_text.splitlines(keepends=True))
    known = {validate.problem_key(e) for e in base}
    return [e for e in head if validate.problem_key(e) not in known]


def problems_body(problems: list[str], login: str) -> str:
    """The comment for a pull request that adds format problems.

    The problems quote the pull request's own text, so they go inside a fenced
    block with backticks swapped out: nothing a submitter writes can close the
    fence or render as markup in a comment the bot signs.
    """
    shown = [p.replace("`", "'") for p in problems[:MAX_SHOWN]]
    more = len(problems) - len(shown)
    lines = [
        MARKER,
        f"Thanks for the submission, @{login}! The format check found "
        f"{len(problems)} problem(s) this pull request adds to `README.md`:",
        "",
        "```text",
        *shown,
        "```",
    ]
    if more:
        lines += ["", f"...and {more} more in the `Validate format` check log."]
    lines += [
        "",
        "`python scripts/validate.py --fix` repairs ordering, table alignment, "
        "whitespace and dashes. Anything else needs an edit to the row; "
        f"[CONTRIBUTING.md](https://github.com/{REPO}/blob/main/CONTRIBUTING.md) "
        "has the rules. Push the "
        "fix to this branch and this comment updates itself.",
    ]
    return "\n".join(lines)


PASSES_BODY = "\n".join([MARKER, "The format check passes now. Thanks for fixing it!"])


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


def check(pr: dict, base_text: str, dry_run: bool) -> None:
    """Post, rewrite or settle the format comment on one pull request."""
    number = pr["number"]
    sha = (pr.get("head") or {}).get("sha") or ""
    if not SHA_RE.fullmatch(sha):
        print(f"  #{number}: no usable head sha; skipped")
        return
    head_text, detail = head_readme(sha)
    if head_text is None:
        print(f"  #{number}: cannot read README.md at {sha[:7]} ({detail}); skipped")
        return

    problems = new_problems(head_text, base_text)
    existing = our_comment(number)
    if problems:
        body = problems_body(problems, (pr.get("user") or {}).get("login", ""))
    elif existing:
        body = PASSES_BODY
    else:
        print(f"  #{number}: no new format problems")
        return

    if existing and existing.get("body") == body:
        print(f"  #{number}: comment already up to date")
        return
    print(
        f"  #{number}: {len(problems)} new problem(s), comment {'updated' if existing else 'posted'}"
    )
    if dry_run:
        print(body)
        return
    if existing:
        api(
            "PATCH",
            f"repos/{REPO}/issues/comments/{seg(existing['id'])}",
            {"body": body},
        )
    else:
        api("POST", f"repos/{REPO}/issues/{seg(number)}/comments", {"body": body})


def open_prs() -> list[dict]:
    prs, err = api("GET", f"repos/{REPO}/pulls?state=open&per_page=100")
    if err:
        print(f"could not list pull requests ({err})", file=sys.stderr)
        return []
    return prs


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--dry-run", action="store_true", help="print, never write")
    args = ap.parse_args()

    base_text = validate.README.read_text(encoding="utf-8")
    event_path = os.environ.get("GITHUB_EVENT_PATH")
    event = (
        json.loads(Path(event_path).read_text(encoding="utf-8")) if event_path else {}
    )
    if os.environ.get("GITHUB_EVENT_NAME") == "pull_request_target":
        check(event["pull_request"], base_text, args.dry_run)
    else:
        # a dispatch, or a local run, has no pull request: check every open one
        for pr in open_prs():
            check(pr, base_text, args.dry_run)
    return 0


if __name__ == "__main__":
    sys.exit(main())
