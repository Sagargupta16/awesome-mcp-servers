"""Tests for scripts/validate.py.

Every pull request to this repository is gated by this validator, so a silent
regression in it weakens every gate while CI stays green. These tests pin the
rules CONTRIBUTING.md promises against small fixtures rather than the real
README, plus one integration check that the validator survives the real file.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import validate

REPO_ROOT = Path(__file__).resolve().parent.parent
GOOD_ROW = "| [Acme MCP](https://github.com/acme/mcp-server) | Acme widget API | Go |"


def _lines(body: str) -> list[str]:
    return [line + "\n" for line in body.strip("\n").split("\n")]


def entry_errors(body: str) -> list[str]:
    """Run the per-entry checks over a snippet and return the messages."""
    rep = validate.Report()
    entries, _, _ = validate.parse(_lines(body))
    validate.check_entries(entries, rep)
    return rep.errors


def duplicate_errors(body: str) -> list[str]:
    rep = validate.Report()
    entries, _, _ = validate.parse(_lines(body))
    validate.check_duplicates(entries, rep)
    return rep.errors


def order_errors(body: str) -> list[str]:
    rep = validate.Report()
    entries, _, _ = validate.parse(_lines(body))
    validate.check_alphabetical(entries, rep)
    return rep.errors


def structure_errors(categories: list[str]) -> list[str]:
    """Build a headings-only skeleton and run the section-order check on it."""
    lines: list[str] = []
    for top in validate.TOP_SECTIONS:
        lines.append(f"## {top}\n")
        if top == "Servers":
            lines.extend(f"### {c}\n" for c in categories)
    rep = validate.Report()
    _, heading_lines, order = validate.parse(lines)
    validate.check_structure(lines, order, heading_lines, rep)
    return rep.errors


# --- description rules -------------------------------------------------------


def test_over_length_table_description_is_reported():
    long_desc = "A" * 81
    errors = entry_errors(
        f"## Security\n\n| [Acme](https://x.dev) | {long_desc} | Go |"
    )

    assert any("description is 81 chars, max 80" in e for e in errors)


def test_lowercase_description_is_reported():
    errors = entry_errors("## Security\n\n| [Acme](https://x.dev) | acme widget | Go |")

    assert any("must start with a capital letter" in e for e in errors)


def test_table_description_ending_in_a_period_is_reported():
    errors = entry_errors(
        "## Security\n\n| [Acme](https://x.dev) | Acme widget. | Go |"
    )

    assert any("must not end with a period" in e for e in errors)


def test_bullet_description_without_a_period_is_reported():
    errors = entry_errors("## Official\n\n- [Acme](https://x.dev) - Acme widget")

    assert any("must end with a period" in e for e in errors)


def test_non_https_url_is_reported():
    errors = entry_errors("## Security\n\n| [Acme](http://x.dev) | Acme widget | Go |")

    assert any("must be https://" in e for e in errors)


# --- column vocabularies -----------------------------------------------------


def test_unknown_language_is_reported():
    errors = entry_errors(
        "## Security\n\n| [Acme](https://x.dev) | Acme widget | Cobol |"
    )

    assert any("language is 'Cobol'" in e for e in errors)


def test_every_documented_language_is_accepted():
    body = "## Security\n\n" + "\n".join(
        f"| [Acme {i}](https://x.dev/{i}) | Acme widget | {lang} |"
        for i, lang in enumerate(sorted(validate.LANGUAGES))
    )

    assert entry_errors(body) == []


def test_unknown_client_support_tier_is_reported():
    errors = entry_errors(
        "## Clients\n\n| [Acme](https://x.dev) | Acme client | Some |"
    )

    assert any("MCP Support is 'Some'" in e for e in errors)


# --- duplicates and ordering -------------------------------------------------


def test_duplicate_url_across_sections_is_reported():
    body = (
        "## Security\n\n| [Acme](https://github.com/acme/mcp) | Acme widget | Go |\n"
        "## Finance\n\n| [Acme Two](https://github.com/acme/mcp/) | Acme widget | Go |"
    )

    assert any("duplicate URL" in e for e in duplicate_errors(body))


def test_duplicate_name_across_sections_is_reported():
    body = (
        "## Security\n\n| [Acme](https://github.com/acme/one) | Acme widget | Go |\n"
        "## Finance\n\n| [acme](https://github.com/acme/two) | Acme widget | Go |"
    )

    assert any("duplicate name" in e for e in duplicate_errors(body))


def test_rows_out_of_alphabetical_order_are_reported():
    body = (
        "## Security\n\n"
        "| [Zeta](https://x.dev/z) | Zeta widget | Go |\n"
        "| [Alpha](https://x.dev/a) | Alpha widget | Go |"
    )

    assert any("out of alphabetical order" in e for e in order_errors(body))


def test_sorted_rows_pass_the_order_check():
    body = (
        "## Security\n\n"
        "| [Alpha](https://x.dev/a) | Alpha widget | Go |\n"
        "| [Zeta](https://x.dev/z) | Zeta widget | Go |"
    )

    assert order_errors(body) == []


# --- structure and table of contents ----------------------------------------


def test_unknown_server_category_is_reported():
    errors = structure_errors([*validate.SERVER_CATEGORIES, "Blockchain"])

    assert any("unknown server category ['Blockchain']" in e for e in errors)


def test_missing_server_category_is_reported():
    errors = structure_errors(validate.SERVER_CATEGORIES[1:])

    assert any("server category missing from README" in e for e in errors)


def test_canonical_categories_pass_the_structure_check():
    assert structure_errors(validate.SERVER_CATEGORIES) == []


def test_toc_anchor_without_a_matching_heading_is_reported():
    lines = _lines("## Contents\n\n- [Official](#no-such-heading)\n\n---")
    rep = validate.Report()
    _, heading_lines, _ = validate.parse(lines)
    validate.check_toc(lines, heading_lines, rep)

    assert any("#no-such-heading has no matching heading" in e for e in rep.errors)


def test_slugify_matches_githubs_double_hyphen_for_ampersands():
    assert validate.slugify("Data & Databases") == "data--databases"


# --- whitespace and dashes ---------------------------------------------------


def test_em_dash_is_reported():
    rep = validate.Report()
    validate.check_whitespace_and_dashes([f"a {chr(0x2014)} b\n"], rep)

    assert any("contains a em-dash" in e for e in rep.errors)


def test_en_dash_is_reported():
    rep = validate.Report()
    validate.check_whitespace_and_dashes([f"a {chr(0x2013)} b\n"], rep)

    assert any("contains a en-dash" in e for e in rep.errors)


def test_trailing_whitespace_is_reported():
    rep = validate.Report()
    validate.check_whitespace_and_dashes(["Acme  \n"], rep)

    assert any("trailing whitespace" in e for e in rep.errors)


# --- the --fix path ----------------------------------------------------------


def test_fix_reorders_rows_without_adding_or_dropping_any():
    lines = _lines(
        "### Security\n\n"
        "| Server | Description | Language |\n"
        "|--------|-------------|----------|\n"
        "| [Zeta](https://x.dev/z) | Zeta widget | Go |\n"
        "| [Alpha](https://x.dev/a) | Alpha widget | Go |"
    )

    fixed = validate.fix(lines)

    assert sorted(fixed) == sorted(line.rstrip() + "\n" for line in lines)
    assert fixed[-2:] == [
        "| [Alpha](https://x.dev/a) | Alpha widget | Go |\n",
        "| [Zeta](https://x.dev/z) | Zeta widget | Go |\n",
    ]


def test_fix_is_idempotent():
    lines = _lines(
        "### Security\n\n"
        "| Server | Description | Language |\n"
        "|--------|-------------|----------|\n"
        "| [Zeta](https://x.dev/z) | Zeta widget | Go |\n"
        "| [Alpha](https://x.dev/a) | Alpha widget | Go |"
    )

    once = validate.fix(lines)
    twice = validate.fix(once)

    assert once == twice


def test_fix_rewrites_an_em_dash_as_two_hyphens():
    fixed = validate.fix([f"Acme {chr(0x2014)} widget\n"])

    assert fixed == ["Acme -- widget\n"]


# --- drift guards ------------------------------------------------------------


def test_contributing_category_table_matches_the_enforced_list():
    """The docs and the enforcement list must not disagree silently."""
    body = (REPO_ROOT / "CONTRIBUTING.md").read_text(encoding="utf-8")
    table = body.split("| Category | Scope |", 1)[1]

    categories = []
    for line in table.splitlines():
        if not line.startswith("|"):
            if categories:
                break
            continue
        cell = line.strip().strip("|").split("|")[0].strip()
        if set(cell) <= {"-", " "}:
            continue
        categories.append(cell)

    assert categories == validate.SERVER_CATEGORIES


def test_validator_runs_cleanly_against_the_real_readme():
    """The validator must survive the real file and give a verdict, not crash.

    Whether the README currently passes is the Validate format job's business,
    not this suite's: on a pull request that job compares against the base
    branch, so an author is not failed for a bad row someone else merged.

    Asserting returncode == 0 here would put that judgement back into the test
    suite without the baseline, which is how #88 went red for #87's mistake.
    """
    result = subprocess.run(
        [sys.executable, "scripts/validate.py"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode in (0, 1), (
        f"validator crashed instead of reporting: {result.returncode}\n{result.stderr}"
    )
    assert "Traceback" not in result.stderr, result.stderr


# --- baseline mode -----------------------------------------------------------


def test_problem_key_ignores_the_line_number():
    a = "README.md:12: 'Acme' description is 90 chars, max 80"
    b = "README.md:400: 'Acme' description is 90 chars, max 80"

    assert validate.problem_key(a) == validate.problem_key(b)


def test_problem_key_keeps_the_message():
    key = validate.problem_key("README.md:12: 'Acme' is out of alphabetical order")

    assert key == "'Acme' is out of alphabetical order"


def test_baseline_errors_returns_none_for_an_unreadable_ref():
    assert validate.baseline_errors("refs/heads/definitely-not-a-real-ref") is None


def test_run_checks_reports_a_long_description_and_counts_entries():
    body = """
## Official

## Servers

### Security

| Server | Description | Language |
|--------|-------------|----------|
| [Acme](https://github.com/acme/acme) | {} | Go |
""".format("x" * 90)

    errors, total = validate.run_checks(_lines(body))

    assert total == 1
    assert any("chars, max 80" in e for e in errors)
