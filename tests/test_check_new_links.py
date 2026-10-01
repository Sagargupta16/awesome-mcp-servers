"""Tests for scripts/check_new_links.py.

The point of this script is that a pull request is only failed for links it
introduces. A regression here either blames contributors for rot on the base
branch, which is what it was written to stop, or stops catching a dead link
somebody actually added.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

import check_new_links
import gitref

ALIVE = "https://github.com/python/cpython"
DEAD = "https://github.com/Sagargupta16/this-repo-does-not-exist-xyz"


# --- link extraction ---------------------------------------------------------


def test_markdown_link_is_found():
    assert check_new_links.links_in(f"see [cpython]({ALIVE}) here") == {ALIVE}


def test_table_row_link_is_found():
    row = f"| [Acme]({ALIVE}) | Acme widget | Go |"

    assert check_new_links.links_in(row) == {ALIVE}


def test_fenced_block_is_ignored():
    body = f"```\n[Example]({ALIVE})\n```"

    assert check_new_links.links_in(body) == set()


def test_inline_code_span_is_ignored():
    """The README's format example carries a literal `| [Name](URL) |`."""
    assert check_new_links.links_in("format: `| [Name](URL) |`") == set()


def test_non_http_target_is_ignored():
    assert check_new_links.links_in("[Security](SECURITY.md)") == set()


def test_anchor_is_ignored():
    assert check_new_links.links_in("[Official](#official)") == set()


# --- lychee.toml is the single source of tolerances --------------------------


def test_accept_codes_come_from_lychee_config():
    accept, _, _ = check_new_links.load_lychee_settings()

    # 403 and 429 are bot-blocks and rate limits, not dead links.
    assert {200, 403, 429} <= accept


def test_excluded_hosts_come_from_lychee_config():
    _, excludes, _ = check_new_links.load_lychee_settings()

    assert any(p.search("https://x.com/someone") for p in excludes)


# --- ref handling ------------------------------------------------------------


def test_option_like_ref_is_refused(capsys):
    assert check_new_links.links_at_ref("-upload-pack=evil") is None
    assert "not a valid git ref" in capsys.readouterr().err


def test_ordinary_revisions_match_the_ref_pattern():
    """The pattern lives in gitref now, shared by all three gate scripts."""
    valid = ["main", "origin/main", "HEAD~1", "refs/heads/main"]

    assert all(gitref.is_valid_ref(r) for r in valid)


def test_option_like_refs_are_refused_by_the_shared_guard():
    hostile = ["-upload-pack=evil", "--exec=bad", "main;rm -rf /", "$(whoami)"]

    assert [r for r in hostile if gitref.is_valid_ref(r)] == []


# --- the diff against a real git history ------------------------------------


def _git(cwd: Path, *args: str) -> None:
    subprocess.run(
        ["git", "-c", "commit.gpgsign=false", *args],
        cwd=cwd,
        check=True,
        capture_output=True,
    )


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    if shutil.which("git") is None:
        pytest.skip("git is not available")
    _git(tmp_path, "init", "-b", "main")
    _git(tmp_path, "config", "user.email", "test@example.invalid")
    _git(tmp_path, "config", "user.name", "Test")
    # The base already carries a dead link, exactly like main did.
    (tmp_path / "README.md").write_text(
        f"| [Rotted]({DEAD}) | x | Go |\n", encoding="utf-8"
    )
    _git(tmp_path, "add", "README.md")
    _git(tmp_path, "commit", "-m", "base")
    return tmp_path


def test_a_link_already_on_the_base_is_not_reported_as_new(repo: Path, monkeypatch):
    """The whole point: rot on the base branch is not this change's fault."""
    monkeypatch.setattr(check_new_links, "REPO_ROOT", repo)
    monkeypatch.chdir(repo)

    before = check_new_links.links_at_ref("HEAD")
    after = check_new_links.links_at_head()

    assert after - before == set()


def test_an_added_link_is_reported_as_new(repo: Path, monkeypatch):
    monkeypatch.setattr(check_new_links, "REPO_ROOT", repo)
    monkeypatch.chdir(repo)
    (repo / "README.md").write_text(
        f"| [Rotted]({DEAD}) | x | Go |\n| [New]({ALIVE}) | y | Go |\n",
        encoding="utf-8",
    )

    new = check_new_links.links_at_head() - check_new_links.links_at_ref("HEAD")

    assert new == {ALIVE}


def test_a_file_missing_at_the_base_is_treated_as_all_new(repo: Path, monkeypatch):
    """CHANGELOG.md does not exist in the fixture, so it cannot be diffed away."""
    monkeypatch.setattr(check_new_links, "REPO_ROOT", repo)
    monkeypatch.chdir(repo)
    (repo / "CHANGELOG.md").write_text(f"- [New]({ALIVE}) - added.\n", encoding="utf-8")

    new = check_new_links.links_at_head() - check_new_links.links_at_ref("HEAD")

    assert ALIVE in new
