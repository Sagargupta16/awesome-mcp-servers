"""Tests for scripts/staleness_report.py.

The monthly audit is the mechanism that catches rot, so what matters is that its
entry regex actually reaches every listed repository. It previously matched only
a bare `owner/repo` link and silently skipped the entries that point into a
subdirectory.
"""

from __future__ import annotations

import staleness_report


def slugs(line: str) -> list[str]:
    return [
        f"{m.group('owner')}/{m.group('repo')}"
        for m in staleness_report.ENTRY_RE.finditer(line)
    ]


def test_plain_repository_link_is_matched():
    row = "| [Acme](https://github.com/acme/mcp-server) | Acme widget | Go |"

    assert slugs(row) == ["acme/mcp-server"]


def test_trailing_slash_link_is_matched():
    row = "| [Acme](https://github.com/acme/mcp-server/) | Acme widget | Go |"

    assert slugs(row) == ["acme/mcp-server"]


def test_subdirectory_link_resolves_to_the_parent_repository():
    row = "| [Graphiti](https://github.com/getzep/graphiti/tree/main/mcp_server) | Memory | Python |"

    assert slugs(row) == ["getzep/graphiti"]


def test_bullet_link_is_matched():
    bullet = (
        "- [MCP Inspector](https://github.com/modelcontextprotocol/inspector) - Tool."
    )

    assert slugs(bullet) == ["modelcontextprotocol/inspector"]


def test_non_github_link_is_not_matched():
    row = "| [Linear MCP](https://linear.app/docs/mcp) | Hosted | Remote |"

    assert slugs(row) == []


def test_collect_skips_this_repositorys_own_links():
    """The CI badge and the issue links are not list entries."""
    collected = staleness_report.collect()

    assert staleness_report.SELF_SLUG not in {
        f"{owner}/{repo}".lower() for _, owner, repo, _ in collected
    }


def test_collect_finds_a_subdirectory_entry_from_the_real_readme():
    collected = {f"{owner}/{repo}" for _, owner, repo, _ in staleness_report.collect()}

    assert "getzep/graphiti" in collected


# --- hosted (`Remote`) entries ---------------------------------------------------

STALE_UNLICENSED = {
    "nameWithOwner": "acme/docs",
    "stargazerCount": 0,
    "pushedAt": "2020-01-01T00:00:00Z",
    "isArchived": False,
    "licenseInfo": None,
}
ENTRY = ("Acme", "acme", "docs", "Productivity")


def test_a_hosted_entrys_repository_is_not_judged_on_licence_or_push():
    """The gate skips both checks for `Remote` rows, so the report must too."""
    now = staleness_report.datetime.now(staleness_report.timezone.utc)

    buckets = staleness_report.classify({ENTRY: STALE_UNLICENSED}, now, {"acme/docs"})

    assert buckets["stale"] == []
    assert buckets["no_licence"] == []


def test_an_ordinary_entry_is_still_judged_on_licence_and_push():
    now = staleness_report.datetime.now(staleness_report.timezone.utc)

    buckets = staleness_report.classify({ENTRY: STALE_UNLICENSED}, now)

    assert len(buckets["stale"]) == 1
    assert len(buckets["no_licence"]) == 1


def test_an_archived_hosted_repository_is_still_reported():
    now = staleness_report.datetime.now(staleness_report.timezone.utc)
    archived = STALE_UNLICENSED | {"isArchived": True}

    buckets = staleness_report.classify({ENTRY: archived}, now, {"acme/docs"})

    assert len(buckets["archived"]) == 1


def test_the_real_readme_has_hosted_entries_and_their_slugs_resolve():
    hosted = staleness_report.remote_entries()

    assert hosted
    assert all(sub.third == "Remote" for sub in hosted)
    assert "usenetstate/statsnet-mcp" in staleness_report.remote_slugs(hosted)


def test_check_hosted_reports_findings_but_not_the_standing_review_note(monkeypatch):
    import check_submission

    def fake_inspect(sub):
        sub.soft.append(check_submission.REMOTE_REVIEW)
        if sub.name == "Dead":
            sub.soft.append("No URL the documentation names answered.")

    monkeypatch.setattr(staleness_report, "inspect", fake_inspect)
    subs = [
        check_submission.Submission("Live", "https://a.dev", "", "Remote"),
        check_submission.Submission("Dead", "https://b.dev", "", "Remote"),
    ]

    assert staleness_report.check_hosted(subs) == [
        ("Dead", "https://b.dev", ["No URL the documentation names answered."])
    ]
