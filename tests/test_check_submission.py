"""Tests for scripts/check_submission.py.

The two behaviours worth pinning are the ones a comment currently protects: that
reordering a table is not read as a batch of new submissions, and that a licence
declared only in a package manifest is recognised.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

import check_submission

ROW_A = "| [Alpha](https://github.com/acme/alpha) | Alpha widget | Go |"
ROW_B = "| [Beta](https://github.com/acme/beta) | Beta widget | Go |"
ROW_C = "| [Gamma](https://github.com/acme/gamma) | Gamma widget | Go |"


# --- row parsing -------------------------------------------------------------


def test_parse_rows_reads_name_url_and_columns():
    rows = check_submission.parse_rows(ROW_A + "\n")

    (sub,) = rows.values()
    assert sub.name == "Alpha"
    assert sub.url == "https://github.com/acme/alpha"
    assert sub.desc == "Alpha widget"
    assert sub.third == "Go"


def test_parse_rows_is_independent_of_row_order():
    """The invariant that lets added_rows() survive a re-sorted table."""
    forward = check_submission.parse_rows(f"{ROW_A}\n{ROW_B}\n")
    reversed_ = check_submission.parse_rows(f"{ROW_B}\n{ROW_A}\n")

    assert set(forward) == set(reversed_)


def test_parse_rows_normalises_trailing_slashes_and_case():
    with_slash = check_submission.parse_rows(
        "| [Alpha](https://github.com/Acme/Alpha/) | Alpha widget | Go |\n"
    )

    assert set(with_slash) == {"github.com/acme/alpha"}


# --- added_rows against a real git history -----------------------------------


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
    (tmp_path / "README.md").write_text(f"{ROW_A}\n{ROW_B}\n", encoding="utf-8")
    _git(tmp_path, "add", "README.md")
    _git(tmp_path, "commit", "-m", "base")
    return tmp_path


def test_added_rows_ignores_a_reordered_table(repo: Path, monkeypatch):
    (repo / "README.md").write_text(f"{ROW_B}\n{ROW_A}\n", encoding="utf-8")
    monkeypatch.chdir(repo)

    assert check_submission.added_rows("HEAD") == []


def test_added_rows_reports_a_new_row(repo: Path, monkeypatch):
    (repo / "README.md").write_text(f"{ROW_A}\n{ROW_B}\n{ROW_C}\n", encoding="utf-8")
    monkeypatch.chdir(repo)

    added = check_submission.added_rows("HEAD")

    assert [sub.name for sub in added] == ["Gamma"]


def test_added_rows_reports_one_row_when_a_table_is_both_sorted_and_extended(
    repo: Path, monkeypatch
):
    (repo / "README.md").write_text(f"{ROW_C}\n{ROW_B}\n{ROW_A}\n", encoding="utf-8")
    monkeypatch.chdir(repo)

    added = check_submission.added_rows("HEAD")

    assert [sub.name for sub in added] == ["Gamma"]


# --- manifest licence detection ----------------------------------------------


def _licence(text: str) -> str | None:
    match = check_submission.MANIFEST_LICENCE_RE.search(text)
    if not match:
        return None
    return next(group for group in match.groups() if group)


def test_package_json_licence_is_read():
    assert _licence('{\n  "name": "acme",\n  "license": "MIT"\n}') == "MIT"


def test_pyproject_licence_is_read():
    assert (
        _licence('[project]\nname = "acme"\nlicense = "Apache-2.0"\n') == "Apache-2.0"
    )


def test_pom_xml_licence_is_read():
    pom = "<licenses><license><name>MIT License</name></license></licenses>"

    assert _licence(pom) == "MIT License"


def test_manifest_without_a_licence_reads_as_none():
    assert _licence('{\n  "name": "acme",\n  "version": "1.0.0"\n}') is None


# --- report rendering --------------------------------------------------------


def test_render_blocks_on_a_hard_failure():
    sub = check_submission.Submission(
        name="Alpha",
        url="https://github.com/acme/alpha",
        desc="Alpha widget",
        third="Go",
    )
    sub.hard.append("The repository is archived.")

    report, failing = check_submission.render([sub], override=False)

    assert failing is True
    assert "Result: blocked." in report


def test_render_honours_the_maintainer_override_label():
    sub = check_submission.Submission(
        name="Alpha",
        url="https://github.com/acme/alpha",
        desc="Alpha widget",
        third="Go",
    )
    sub.hard.append("The repository is archived.")

    report, failing = check_submission.render([sub], override=True)

    assert failing is False
    assert check_submission.OVERRIDE_LABEL in report


def test_render_blocks_a_pull_request_that_adds_more_than_one_entry():
    subs = [
        check_submission.Submission(
            name=name, url=f"https://github.com/acme/{name}", desc="Widget", third="Go"
        )
        for name in ("alpha", "beta")
    ]

    _, failing = check_submission.render(subs, override=False)

    assert failing is True


def test_render_passes_a_clean_single_entry():
    sub = check_submission.Submission(
        name="Alpha",
        url="https://github.com/acme/alpha",
        desc="Alpha widget",
        third="Go",
    )

    report, failing = check_submission.render([sub], override=False)

    assert failing is False
    assert "Result: passed." in report
