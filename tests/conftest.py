"""Shared test setup: importable gate scripts, and a throwaway git repository.

`scripts/` is a directory of standalone entry points rather than an installed
package, so pytest cannot import them until the directory is on `sys.path`.

Two suites need a real git history to test their `--base-ref` diffing against,
so the repository fixture lives here rather than in each of them. Seeding is left
to the caller: one wants a base carrying entry rows, the other a base carrying a
dead link.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = REPO_ROOT / "scripts"

if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


def git(cwd: Path, *args: str) -> None:
    """Run git in `cwd`, with signing off so a signing key is not required."""
    subprocess.run(
        ["git", "-c", "commit.gpgsign=false", *args],
        cwd=cwd,
        check=True,
        capture_output=True,
    )


@pytest.fixture
def git_repo(tmp_path: Path) -> Path:
    """An initialised, configured, empty git repository on `main`."""
    if shutil.which("git") is None:
        pytest.skip("git is not available")
    git(tmp_path, "init", "-b", "main")
    git(tmp_path, "config", "user.email", "test@example.invalid")
    git(tmp_path, "config", "user.name", "Test")
    return tmp_path


def commit_readme(repo: Path, body: str, message: str = "base") -> None:
    """Write README.md and commit it, so a later diff has something to compare."""
    (repo / "README.md").write_text(body, encoding="utf-8")
    git(repo, "add", "README.md")
    git(repo, "commit", "-m", message)
