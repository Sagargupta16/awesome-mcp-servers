"""Tests for scripts/check_submission.py.

The two behaviours worth pinning are the ones a comment currently protects: that
reordering a table is not read as a batch of new submissions, and that a licence
declared only in a package manifest is recognised.
"""

from __future__ import annotations

import base64
import shutil
import subprocess
from datetime import datetime, timezone
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


def _licence(filename: str, text: str) -> str | None:
    return check_submission.parse_manifest_licence(filename, text)


def test_package_json_licence_is_read():
    assert (
        _licence("package.json", '{\n  "name": "acme",\n  "license": "MIT"\n}') == "MIT"
    )


def test_package_json_legacy_object_licence_is_read():
    manifest = '{"name": "acme", "license": {"type": "MIT", "url": "http://x/y"}}'

    assert _licence("package.json", manifest) == "MIT"


def test_composer_array_licence_is_read():
    """CONTRIBUTING.md lists composer.json, which allows an array of licences."""
    assert _licence("composer.json", '{"license": ["MIT", "GPL-3.0"]}') == "MIT"


def test_pyproject_string_licence_is_read():
    assert (
        _licence("pyproject.toml", '[project]\nname = "acme"\nlicense = "Apache-2.0"\n')
        == "Apache-2.0"
    )


def test_pyproject_table_licence_is_read():
    """PEP 621's `license = {text = "..."}` form, which a text search misses."""
    manifest = '[project]\nname = "acme"\nlicense = {text = "Apache-2.0"}\n'

    assert _licence("pyproject.toml", manifest) == "Apache-2.0"


def test_cargo_licence_is_read():
    assert _licence("Cargo.toml", '[package]\nlicense = "MIT OR Apache-2.0"\n') == (
        "MIT OR Apache-2.0"
    )


def test_licence_pointing_at_a_file_is_not_a_declaration():
    """A file pointer names no terms, and GitHub already read the root files."""
    manifest = '[project]\nname = "acme"\nlicense = {file = "LICENSE.txt"}\n'

    assert _licence("pyproject.toml", manifest) is None


def test_pom_xml_licence_is_read():
    pom = "<licenses><license><name>MIT License</name></license></licenses>"

    assert _licence("pom.xml", pom) == "MIT License"


def test_manifest_without_a_licence_reads_as_none():
    assert (
        _licence("package.json", '{\n  "name": "acme",\n  "version": "1.0.0"\n}')
        is None
    )


def test_a_nested_licence_key_is_not_read_as_the_packages_own():
    """The reason this is parsed rather than pattern-matched."""
    manifest = '{"name": "acme", "dependencies": {"dep": {"license": "MIT"}}}'

    assert _licence("package.json", manifest) is None


def test_unparseable_manifest_reads_as_none():
    assert _licence("package.json", "{not json") is None
    assert _licence("pyproject.toml", "[project") is None


# --- open-source check on the declared value ---------------------------------


@pytest.mark.parametrize(
    "value",
    [
        "UNLICENSED",
        "unlicensed",
        "SEE LICENSE IN proprietary.txt",
        "Proprietary",
        "none",
    ],
)
def test_a_field_that_withholds_open_source_terms_is_rejected(value: str):
    assert check_submission.is_open_source(value) is False


@pytest.mark.parametrize(
    "value", ["MIT", "Apache-2.0", "Unlicense", "MIT OR Apache-2.0"]
)
def test_a_real_licence_is_accepted(value: str):
    assert check_submission.is_open_source(value) is True


# --- manifest_licence over the API -------------------------------------------


def _fake_api(files: dict):
    """Stand in for gh_api, serving base64 file contents for the paths given."""

    def fake(path: str):
        for name, text in files.items():
            if path.endswith(f"/contents/{name}"):
                content = base64.b64encode(text.encode("utf-8")).decode("ascii")
                return {"content": content}, None
        return None, 404

    return fake


def test_manifest_licence_returns_the_first_manifest_that_declares_one(monkeypatch):
    monkeypatch.setattr(
        check_submission,
        "gh_api",
        _fake_api(
            {
                "package.json": '{"name": "acme"}',
                "pyproject.toml": '[project]\nlicense = {text = "Apache-2.0"}\n',
            }
        ),
    )

    assert check_submission.manifest_licence("acme/alpha") == (
        "pyproject.toml",
        "Apache-2.0",
    )


def test_manifest_licence_returns_nothing_when_no_manifest_exists(monkeypatch):
    monkeypatch.setattr(check_submission, "gh_api", _fake_api({}))

    assert check_submission.manifest_licence("acme/alpha") == (None, None)


# --- inspect(), with the GitHub API stubbed ----------------------------------


def _repo_api(files: dict):
    """Serve a live, licence-less, MIT-free repository plus the given manifests."""
    fresh = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    repo = {
        "pushed_at": fresh,
        "created_at": fresh,
        "license": None,
        "stargazers_count": 3,
        "archived": False,
        "fork": False,
        "language": "TypeScript",
    }
    manifests = _fake_api(files)

    def fake(path: str):
        if path == "repos/acme/alpha":
            return repo, None
        if path == "repos/acme/alpha/license":
            return None, 404
        if path == "repos/acme/alpha/contents":
            return [
                {"name": "README.md", "type": "file"},
                {"name": "src", "type": "dir"},
            ], None
        return manifests(path)

    return fake


def _inspected(files: dict, monkeypatch) -> check_submission.Submission:
    monkeypatch.setattr(check_submission, "gh_api", _repo_api(files))
    sub = check_submission.Submission(
        name="Alpha",
        url="https://github.com/acme/alpha",
        desc="Alpha widget",
        third="TypeScript",
    )
    check_submission.inspect(sub)
    return sub


def test_inspect_blocks_a_manifest_that_declares_unlicensed(monkeypatch):
    """npm's marker for a package that is explicitly not open source."""
    sub = _inspected({"package.json": '{"license": "UNLICENSED"}'}, monkeypatch)

    assert any("UNLICENSED" in problem for problem in sub.hard)


def test_inspect_blocks_a_manifest_that_points_at_proprietary_terms(monkeypatch):
    sub = _inspected(
        {"package.json": '{"license": "SEE LICENSE IN proprietary.txt"}'}, monkeypatch
    )

    assert sub.hard != []


def test_inspect_accepts_a_manifest_licence_with_a_maintainer_note(monkeypatch):
    sub = _inspected({"package.json": '{"license": "Apache-2.0"}'}, monkeypatch)

    assert sub.hard == []
    assert any("package.json" in note for note in sub.soft)
    assert sub.facts["license"] == "Apache-2.0 (declared in package.json)"


def test_inspect_blocks_a_repository_with_no_licence_anywhere(monkeypatch):
    sub = _inspected({}, monkeypatch)

    assert any("No licence anywhere" in problem for problem in sub.hard)


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
