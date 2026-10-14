"""Tests for scripts/thank_contributors.py.

The comment it posts is public and goes to strangers, so the parts worth pinning
are who gets thanked and for what: a new entry yes, a reworded existing entry no,
a bot or the maintainer no, and never twice.
"""

from __future__ import annotations

import build_site
import thank_contributors

ROW = "| [Acme MCP](https://github.com/acme/mcp) | Acme widget API | Go |"
ROW_EDITED = (
    "| [Acme MCP](https://github.com/acme/mcp) | Acme widget and gadget API | Go |"
)
BULLET = "- [Acme Guide](https://acme.dev/guide) - How to run Acme."


# --- which entries a diff adds -------------------------------------------------


def test_an_added_row_is_a_new_entry():
    patch = f"@@ -1,2 +1,3 @@\n context\n+{ROW}\n"

    assert thank_contributors.added_entries(patch) == [
        ("Acme MCP", "https://github.com/acme/mcp")
    ]


def test_an_added_bullet_is_a_new_entry():
    patch = f"+{BULLET}\n"

    assert thank_contributors.added_entries(patch) == [
        ("Acme Guide", "https://acme.dev/guide")
    ]


def test_a_reworded_row_is_not_a_new_entry():
    """#144: a contributor updating their own description is already listed."""
    patch = f"-{ROW}\n+{ROW_EDITED}\n"

    assert thank_contributors.added_entries(patch) == []


def test_file_headers_and_context_lines_are_ignored():
    patch = f"--- a/README.md\n+++ b/README.md\n {ROW}\n"

    assert thank_contributors.added_entries(patch) == []


def test_a_table_header_is_not_an_entry():
    patch = (
        "+| Server | Description | Language |\n+|--------|-------------|----------|\n"
    )

    assert thank_contributors.added_entries(patch) == []


# --- who is thanked -------------------------------------------------------------


def _pr(login: str, kind: str = "User", base: str = "main") -> dict:
    return {"number": 1, "user": {"login": login, "type": kind}, "base": {"ref": base}}


def test_a_contributor_pull_request_is_thanked():
    assert thank_contributors.skip_reason(_pr("someone")) is None


def test_a_bot_pull_request_is_left_to_the_issue():
    """Form submissions are opened by the bot; their issue thanks the author."""
    assert thank_contributors.skip_reason(_pr("github-actions[bot]", "Bot"))


def test_the_maintainer_is_not_thanked():
    assert thank_contributors.skip_reason(_pr(thank_contributors.OWNER))


def test_a_pull_request_into_another_branch_is_not_thanked():
    assert thank_contributors.skip_reason(_pr("someone", base="develop"))


def test_an_unreadable_comment_list_counts_as_already_thanked(monkeypatch):
    """A missed thank-you is better than a duplicate on a stranger's PR."""
    monkeypatch.setattr(thank_contributors, "api", lambda *a, **k: (None, 502))

    assert thank_contributors.already_thanked(1) is True


def test_a_marker_in_any_comment_counts_as_already_thanked(monkeypatch):
    comments = [{"body": "lgtm"}, {"body": f"{thank_contributors.MARKER}\nThanks"}]
    monkeypatch.setattr(thank_contributors, "api", lambda *a, **k: (comments, None))

    assert thank_contributors.already_thanked(1) is True


# --- what the comment says ------------------------------------------------------


def test_the_comment_carries_the_marker_badge_and_a_search_link():
    body = thank_contributors.render_thanks("someone", [("Acme MCP", "https://x")])

    assert body.startswith(thank_contributors.MARKER)
    assert "@someone" in body
    assert build_site.BADGE_MARKDOWN in body
    assert f"{build_site.SITE_URL}?q=Acme%20MCP" in body


def test_the_star_ask_says_it_is_optional():
    body = thank_contributors.render_thanks("someone", [("Acme MCP", "https://x")])

    assert "Neither is required" in body


def test_several_entries_are_named_together():
    body = thank_contributors.render_thanks(
        "someone",
        [("Alpha", "https://a"), ("Beta", "https://b"), ("Gamma", "https://c")],
    )

    assert "**Alpha**, **Beta** and **Gamma** are on the list" in body


def test_the_badge_links_to_the_repository_where_stars_happen():
    assert build_site.BADGE_MARKDOWN.endswith(f"({build_site.REPO_URL})")
