"""Reading a file out of a git ref, safely, in one place.

Three scripts need the same two things: a check that a command-line ref really
looks like a revision, and the contents of one path at that revision.
`validate.py --baseline`, `check_submission.py --base-ref` and
`check_new_links.py --base-ref` each had their own copy, which meant the security
guard existed in triplicate and could be widened in one place without the others.
"""

from __future__ import annotations

import re
import subprocess

# Shape of an acceptable ref. The leading character is constrained because
# nothing is run through a shell, but a value beginning with `-` would still be
# read by git as an option rather than a revision.
REF_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/~^@{}-]*$")


def is_valid_ref(ref: str) -> bool:
    return bool(REF_RE.match(ref))


def show(ref: str, path: str) -> tuple[str | None, str]:
    """Return (contents, error) for `path` at `ref`.

    `contents` is None when git could not read it, in which case `error` carries
    git's own message. Callers word their own failure, since what an unreadable
    base means differs between a validator and a link checker.
    """
    proc = subprocess.run(
        ["git", "show", f"{ref}:{path}"],
        capture_output=True,
        check=False,
        shell=False,
    )
    if proc.returncode != 0:
        return None, proc.stderr.decode("utf-8", "replace").strip()
    return proc.stdout.decode("utf-8", "replace"), ""
