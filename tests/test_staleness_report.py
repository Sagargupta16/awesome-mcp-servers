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
