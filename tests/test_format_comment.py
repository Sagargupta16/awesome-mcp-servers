"""Tests for scripts/format_comment.py.

The script writes on strangers' pull requests, so what is pinned is when it
speaks (only for problems a pull request adds), that what it quotes cannot break
out of its code block, and that it settles its own comment once the row is fixed.
"""

from __future__ import annotations

import base64

import pytest

import format_comment
import validate

BASE = validate.README.read_text(encoding="utf-8")
# 100 characters: over the 80 both lists allow, with a backtick to quote back
LONG_DESCRIPTION = "Compare and price `every` plan " + "x" * 69


def _break_first_row(text: str) -> str:
    """The README with the first entry row's description swapped for a bad one."""
    lines = text.splitlines(keepends=True)
    for i, line in enumerate(lines):
        cells = line.split("|")
        if line.startswith("| [") and len(cells) >= 4:
            cells[2] = f" {LONG_DESCRIPTION} "
            lines[i] = "|".join(cells)
            return "".join(lines)
    raise AssertionError("no entry row found in README.md")


class FakeAPI:
    """Stand in for thank_contributors.api: canned comments, every call recorded."""

    def __init__(self, comments: list[dict]):
        self.comments = comments
        self.calls: list[tuple[str, str, dict | None]] = []

    def __call__(self, method, path, payload=None, token=None):
        self.calls.append((method, path, payload))
        if method == "GET" and path.endswith("/comments?per_page=100"):
            return self.comments, None
        return {}, None

    def writes(self) -> list[tuple[str, str, dict | None]]:
        return [c for c in self.calls if c[0] != "GET"]


@pytest.fixture
def run(monkeypatch):
    """Check one pull request whose README.md is `head`, against main's README."""

    def go(head: str, comments: list[dict]) -> FakeAPI:
        api = FakeAPI(comments)
        monkeypatch.setattr(format_comment, "api", api)
        monkeypatch.setattr(format_comment, "head_readme", lambda sha: (head, ""))
        pr = {"number": 7, "head": {"sha": "a" * 40}, "user": {"login": "someone"}}
        format_comment.check(pr, BASE, dry_run=False)
        return api

    return go


def _ours(body: str) -> dict:
    return {"id": 99, "user": {"login": format_comment.BOT}, "body": body}


def test_no_new_problems_on_an_unchanged_readme():
    assert format_comment.new_problems(BASE, BASE) == []


def test_a_bad_row_is_reported_and_only_its_problems():
    problems = format_comment.new_problems(_break_first_row(BASE), BASE)
    assert problems
    assert all("description" in p for p in problems)
    assert any("max 80" in p for p in problems)


def test_the_body_cannot_close_its_own_code_block():
    body = format_comment.problems_body(["README.md:1: has ```` and `ticks`"], "x")
    fenced = body.split("```text\n", 1)[1].split("\n```", 1)[0]
    assert "`" not in fenced
    assert body.startswith(format_comment.MARKER)
    assert "@x" in body


def test_posts_one_comment_for_a_bad_row(run):
    api = run(_break_first_row(BASE), comments=[])
    [(method, path, payload)] = api.writes()
    assert method == "POST"
    assert path.endswith("issues/7/comments")
    assert "max 80" in payload["body"]


def test_rewrites_its_comment_as_passing_once_fixed(run):
    api = run(BASE, comments=[_ours(f"{format_comment.MARKER}\nold problems")])
    [(method, path, payload)] = api.writes()
    assert method == "PATCH"
    assert path.endswith("issues/comments/99")
    assert payload["body"] == format_comment.PASSES_BODY


def test_says_nothing_to_a_clean_pull_request(run):
    assert run(BASE, comments=[]).writes() == []


def test_leaves_an_up_to_date_comment_alone(run):
    assert run(BASE, comments=[_ours(format_comment.PASSES_BODY)]).writes() == []


def test_ignores_someone_elses_comment_with_the_marker(run):
    forged = {"id": 5, "user": {"login": "someone"}, "body": format_comment.MARKER}
    api = run(BASE, comments=[forged])
    assert api.writes() == []


def test_reads_the_head_readme_through_the_contents_api(monkeypatch):
    text = "# Title" + chr(10)
    encoded = base64.b64encode(text.encode()).decode()
    api_calls = []

    def fake(method, path, payload=None, token=None):
        api_calls.append(path)
        return {"encoding": "base64", "content": encoded}, None

    monkeypatch.setattr(format_comment, "api", fake)
    assert format_comment.head_readme("b" * 40) == (text, "")
    assert api_calls == [
        f"repos/{format_comment.REPO}/contents/README.md?ref={'b' * 40}"
    ]


def test_skips_a_pull_request_without_a_real_sha(monkeypatch):
    api = FakeAPI([])
    monkeypatch.setattr(format_comment, "api", api)
    pr = {"number": 7, "head": {"sha": "main; rm -rf /"}, "user": {"login": "x"}}
    format_comment.check(pr, BASE, dry_run=False)
    assert api.calls == []
