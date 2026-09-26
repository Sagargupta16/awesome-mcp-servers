"""Tests for scripts/issue_to_pr.py, which turns the issue form into a README row."""

from __future__ import annotations

import json

import pytest

import issue_to_pr

FORM = """### Name

Acme MCP

### Repository or project URL

https://github.com/acme/mcp-server/

### Section

Servers

### Category

Security

### Language

typescript

### Description

scans acme widgets for secrets.

### Affiliation

I am the author or maintainer

### Anything else

_No response_
"""

README = """## Servers

### Security

| Server | Description | Language |
|--------|-------------|----------|
| [Beta MCP](https://github.com/beta/mcp) | Beta scanner | Go |
| [Zeta MCP](https://github.com/zeta/mcp) | Zeta scanner | Go |

### Web Browsing & Scraping

| Server | Description | Language |
|--------|-------------|----------|
| [Web MCP](https://github.com/web/mcp) | Web pages | Python |
"""


def _lines(text: str) -> list[str]:
    return text.splitlines(True)


def test_parse_form_reads_answers_and_drops_no_response():
    fields = issue_to_pr.parse_form(FORM)

    assert fields["Name"] == "Acme MCP"
    assert fields["Category"] == "Security"
    assert fields["Anything else"] == ""


def test_build_row_normalises_the_answers():
    section, row = issue_to_pr.build_row(issue_to_pr.parse_form(FORM))

    assert section == "Security"
    assert row == (
        "| [Acme MCP](https://github.com/acme/mcp-server) | "
        "Scans acme widgets for secrets | TypeScript |"
    )


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("Name", "Bad | Name", "cannot contain"),
        ("Repository or project URL", "http://github.com/a/b", "https://"),
        ("Repository or project URL", "https://x.com/a b", "https://"),
        ("Description", "x" * 81, "81 characters"),
        ("Language", "Cobol", "not a language"),
        ("Category", "n/a", "server categories"),
    ],
)
def test_build_row_rejects_broken_answers(field, value, message):
    fields = issue_to_pr.parse_form(FORM)
    fields[field] = value

    with pytest.raises(issue_to_pr.Rejected, match=message):
        issue_to_pr.build_row(fields)


def test_sections_the_form_does_not_fill_are_left_to_a_maintainer():
    fields = issue_to_pr.parse_form(FORM)
    fields["Section"] = "Clients"

    with pytest.raises(LookupError):
        issue_to_pr.build_row(fields)


def test_insert_row_lands_in_its_table_in_order():
    row = "| [Gamma MCP](https://github.com/gamma/mcp) | Gamma scanner | Go |"

    out = "".join(issue_to_pr.insert_row(_lines(README), "Security", row))

    security = out.split("### Web Browsing")[0]
    assert (
        security.index("Beta MCP")
        < security.index("Gamma MCP")
        < security.index("Zeta MCP")
    )
    assert out.count("Gamma MCP") == 1


def test_insert_row_refuses_a_link_already_listed():
    row = "| [Web Again](https://github.com/web/mcp/) | Same repo | Python |"

    with pytest.raises(issue_to_pr.Rejected, match="already on the list"):
        issue_to_pr.insert_row(_lines(README), "Security", row)


def test_main_writes_the_readme_and_reports_ok(tmp_path, monkeypatch):
    (tmp_path / "README.md").write_text(README, encoding="utf-8")
    event = tmp_path / "event.json"
    event.write_text(
        json.dumps({"issue": {"number": 7, "body": FORM}}), encoding="utf-8"
    )
    out = tmp_path / "out.txt"
    monkeypatch.setattr(issue_to_pr, "ROOT", tmp_path)
    monkeypatch.setenv("GITHUB_EVENT_PATH", str(event))
    monkeypatch.setenv("GITHUB_OUTPUT", str(out))

    assert issue_to_pr.main() == 0

    assert "status=ok" in out.read_text(encoding="utf-8")
    assert "name=Acme MCP" in out.read_text(encoding="utf-8")
    assert "[Acme MCP]" in (tmp_path / "README.md").read_text(encoding="utf-8")


def test_main_explains_a_rejection_without_touching_the_readme(tmp_path, monkeypatch):
    (tmp_path / "README.md").write_text(README, encoding="utf-8")
    body = FORM.replace("typescript", "Cobol")
    event = tmp_path / "event.json"
    event.write_text(
        json.dumps({"issue": {"number": 7, "body": body}}), encoding="utf-8"
    )
    out = tmp_path / "out.txt"
    monkeypatch.setattr(issue_to_pr, "ROOT", tmp_path)
    monkeypatch.setenv("GITHUB_EVENT_PATH", str(event))
    monkeypatch.setenv("GITHUB_OUTPUT", str(out))

    assert issue_to_pr.main() == 0

    assert "status=invalid" in out.read_text(encoding="utf-8")
    assert "Cobol" in (tmp_path / "issue-comment.md").read_text(encoding="utf-8")
    assert (tmp_path / "README.md").read_text(encoding="utf-8") == README
