"""Tests for scripts/build_site.py, the website built from README.md."""

from __future__ import annotations

from datetime import datetime, timezone

import build_site

SNIPPET = """
## Official

- [MCP Specification](https://modelcontextprotocol.io/specification) - The official protocol specification.

## Servers

### Data & Databases

| Server | Description | Language |
|--------|-------------|----------|
| [Acme MCP](https://github.com/acme/mcp-server) | Acme widget API | Go |
| [Mono MCP](https://github.com/org/mono/tree/main/src/mcp) | Lives in a monorepo folder | Python |

### Security

| Server | Description | Language |
|--------|-------------|----------|
| [Evil <script>](https://example.com/x?a=1&b=2) | Quotes " and <tags> | Remote |

## Clients

| Client | Description | MCP Support |
|--------|-------------|-------------|
| [Some Client](https://github.com/c/client) | A desktop client | Tools only |
"""


def _items():
    return build_site.load_items(SNIPPET.strip("\n").splitlines(True))


def test_items_carry_their_tab_and_category():
    by_name = {i.name: i for i in _items()}

    assert by_name["Acme MCP"].tab == "servers"
    assert by_name["Acme MCP"].category == "Data & Databases"
    assert by_name["Acme MCP"].tag == "Go"
    assert by_name["Some Client"].tab == "clients"
    assert by_name["Some Client"].tag == "Tools only"
    assert by_name["MCP Specification"].tab == "official"


def test_github_slug_handles_repo_roots_and_monorepo_folders():
    assert (
        build_site.github_slug("https://github.com/acme/mcp-server")
        == "acme/mcp-server"
    )
    assert build_site.github_slug("https://github.com/acme/mcp.git") == "acme/mcp"
    assert (
        build_site.github_slug("https://github.com/org/mono/tree/main/src/mcp")
        == "org/mono"
    )
    assert build_site.github_slug("https://example.com/org/repo") == ""


def test_star_counts_are_short():
    assert build_site._stars(None) == ""
    assert build_site._stars(950) == "950"
    assert build_site._stars(1000) == "1k"
    assert build_site._stars(187076) == "187.1k"


def test_rendered_page_escapes_entry_text():
    template = "<main>{{CARDS}}</main><p>{{SERVER_COUNT}} {{CATEGORY_COUNT}}</p>"
    page = build_site.render_page(
        _items(), template, datetime(2026, 9, 26, tzinfo=timezone.utc)
    )

    assert "<script>" not in page
    assert "Evil &lt;script&gt;" in page
    assert "a=1&amp;b=2" in page
    assert "<p>3 2</p>" in page  # three servers across two categories


def test_every_placeholder_in_the_real_template_is_filled():
    template = (build_site.SITE_SRC / "index.html").read_text(encoding="utf-8")
    page = build_site.render_page(
        _items(), template, datetime(2026, 9, 26, tzinfo=timezone.utc)
    )

    assert "{{" not in page


def test_the_real_readme_builds():
    lines = (build_site.ROOT / "README.md").read_text(encoding="utf-8").splitlines(True)
    items = build_site.load_items(lines)

    assert len([i for i in items if i.tab == "servers"]) > 100
    assert {i.tab for i in items} >= {"servers", "frameworks", "clients"}
