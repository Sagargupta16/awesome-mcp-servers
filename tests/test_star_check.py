"""Tests for scripts/star_check.py.

The script writes on strangers' pull requests and can switch on auto-merge, so
the parts worth pinning are who gets asked, what a star releases, and that a
star never releases anything auto-merge.yml would not merge itself.
"""

from __future__ import annotations

import pytest

import star_check

REPO_ID = 1172129536


class FakeAPI:
    """Stand in for thank_contributors.api: canned answers, every call recorded."""

    def __init__(self, routes: dict):
        self.routes = routes
        self.calls: list[tuple[str, str, dict | None]] = []

    def __call__(self, method, path, payload=None, token=None):
        self.calls.append((method, path, payload))
        # longest prefix wins, so `pulls/7` never shadows `pulls/7/files`
        matches = [
            (prefix, answer)
            for (m, prefix), answer in self.routes.items()
            if m == method and path.startswith(prefix)
        ]
        if not matches:
            return None, None
        _, answer = max(matches, key=lambda match: len(match[0]))
        return answer(path) if callable(answer) else answer

    def writes(self) -> list[tuple[str, str]]:
        return [(m, p) for m, p, _ in self.calls if m != "GET"]


@pytest.fixture
def fake(monkeypatch):
    """Install a FakeAPI with the given routes; caches are cleared per test."""
    star_check.stargazers.cache_clear()
    star_check.repo_id.cache_clear()

    def install(routes: dict) -> FakeAPI:
        api = FakeAPI(routes)
        monkeypatch.setattr(star_check, "api", api)
        return api

    yield install
    star_check.stargazers.cache_clear()
    star_check.repo_id.cache_clear()


def _pr(login="someone", labels=(), kind="User", number=7) -> dict:
    return {
        "number": number,
        "node_id": f"PR_{number}",
        "user": {"login": login, "type": kind},
        "labels": [{"name": n} for n in labels],
    }


STARGAZERS = ("GET", f"repos/{star_check.REPO}/stargazers")
CLOSED_LIST = {STARGAZERS: (None, 403)}
NO_COMMENTS = ("GET", f"repos/{star_check.REPO}/issues/7/comments")


# --- who has starred -------------------------------------------------------------


def test_the_stargazer_list_is_read_case_insensitively(fake):
    fake({STARGAZERS: ([{"login": "MilleniumSpark"}], None)})

    assert star_check.has_starred("milleniumspark") is True
    assert star_check.has_starred("someone-else") is False


def test_a_closed_stargazer_list_falls_back_to_the_persons_stars(fake):
    """A workflow's own token may be refused the stargazer list."""
    fake(
        CLOSED_LIST
        | {
            ("GET", f"repos/{star_check.REPO}"): ({"id": REPO_ID}, None),
            ("GET", "users/fan/starred"): ([{"id": 1}, {"id": REPO_ID}], None),
        }
    )

    assert star_check.has_starred("fan") is True


def test_the_fallback_stops_at_a_short_page(fake):
    api = fake(
        CLOSED_LIST
        | {
            ("GET", f"repos/{star_check.REPO}"): ({"id": REPO_ID}, None),
            ("GET", "users/someone/starred"): ([{"id": 1}], None),
        }
    )

    assert star_check.has_starred("someone") is False
    assert sum(p.startswith("users/") for _, p, _ in api.calls) == 1


def test_an_unreadable_starred_list_counts_as_not_starred(fake):
    """The safe direction: the pull request waits for a maintainer."""
    fake(
        CLOSED_LIST
        | {
            ("GET", f"repos/{star_check.REPO}"): ({"id": REPO_ID}, None),
            ("GET", "users/someone/starred"): (None, 502),
        }
    )

    assert star_check.has_starred("someone") is False


@pytest.mark.parametrize(
    "login", ["../../repos/x/y", "a/b", "-lead", "trail-", "a--b", ""]
)
def test_anything_but_a_github_login_is_refused_before_any_request(fake, login):
    """The login becomes part of an API path; `../` would walk it elsewhere."""
    api = fake({STARGAZERS: ([], None)})

    assert star_check.has_starred(login) is False
    assert api.calls == []


# --- the ask -----------------------------------------------------------------------


def test_the_ask_carries_the_marker_command_and_what_a_star_does():
    body = star_check.ask_body("someone")

    assert body.startswith(star_check.MARKER)
    assert "@someone" in body
    assert f"gh api -X PUT /user/starred/{star_check.REPO}" in body
    assert "merges itself" in body


@pytest.mark.parametrize(
    ("pr", "reason"),
    [(_pr(kind="Bot"), "bot"), (_pr(login=star_check.OWNER), "maintainer")],
)
def test_bots_and_the_maintainer_are_never_asked(fake, pr, reason):
    api = fake({STARGAZERS: ([], None)})

    star_check.check(pr, dry_run=False)

    assert reason in star_check.skip_reason(pr)
    assert api.writes() == []


def test_someone_who_has_not_starred_gets_the_label_and_one_comment(fake):
    api = fake(
        {
            STARGAZERS: ([], None),
            ("GET", f"repos/{star_check.REPO}/issues/7/comments"): ([], None),
        }
    )

    star_check.check(_pr(), dry_run=False)

    assert api.writes() == [
        ("POST", f"repos/{star_check.REPO}/issues/7/labels"),
        ("POST", f"repos/{star_check.REPO}/issues/7/comments"),
    ]


def test_an_unchanged_comment_is_not_rewritten(fake):
    """A re-run must not notify anyone."""
    ours = {
        "id": 9,
        "user": {"login": star_check.BOT},
        "body": star_check.ask_body("someone"),
    }
    api = fake({("GET", f"repos/{star_check.REPO}/issues/7/comments"): ([ours], None)})

    star_check.upsert_comment(7, star_check.ask_body("someone"), create=True)

    assert api.writes() == []


def test_a_thank_you_is_only_written_where_someone_was_asked(fake):
    api = fake({("GET", f"repos/{star_check.REPO}/issues/7/comments"): ([], None)})

    star_check.upsert_comment(7, star_check.THANKS_BODY, create=False)

    assert api.writes() == []


def test_a_comment_quoting_the_marker_is_not_taken_for_ours(fake):
    human = {"id": 3, "user": {"login": "someone"}, "body": star_check.MARKER}
    fake({("GET", f"repos/{star_check.REPO}/issues/7/comments"): ([human], None)})

    assert star_check.our_comment(7) is None


# --- what a star releases ----------------------------------------------------------


def _files(*names):
    return ([{"filename": n} for n in names], None)


def _release_routes(state: str, *files: str) -> dict:
    return {
        ("GET", f"repos/{star_check.REPO}/pulls/7/files"): _files(
            *(files or ("README.md",))
        ),
        ("GET", f"repos/{star_check.REPO}/pulls/7"): ({"mergeable_state": state}, None),
    }


def test_a_held_pull_request_with_pending_checks_gets_auto_merge(fake):
    api = fake(_release_routes("blocked"))

    star_check.release(_pr(labels=["missing-star"]), dry_run=False)

    graphql = [payload for m, p, payload in api.calls if p == "graphql"]
    assert len(graphql) == 1
    assert graphql[0]["variables"] == {"id": "PR_7"}
    assert not any(m == "PUT" for m, _ in api.writes())


@pytest.mark.parametrize("state", sorted(star_check.MERGEABLE_NOW))
def test_a_held_pull_request_that_can_merge_now_is_merged(fake, state):
    """GitHub refuses auto-merge once every required check has passed."""
    api = fake(_release_routes(state))

    star_check.release(_pr(labels=["missing-star"]), dry_run=False)

    assert api.writes() == [("PUT", f"repos/{star_check.REPO}/pulls/7/merge")]
    assert api.calls[-1][2] == {"merge_method": "squash"}


def test_a_pull_request_touching_a_workflow_is_never_released(fake):
    """A star must not open the door auto-merge.yml keeps shut."""
    api = fake(_release_routes("clean", "README.md", ".github/workflows/x.yml"))

    star_check.release(_pr(), dry_run=False)

    assert api.writes() == []


@pytest.mark.parametrize("stop", sorted(star_check.STOP_LABELS))
def test_a_maintainer_stop_label_keeps_a_pull_request_held(fake, stop):
    api = fake(_release_routes("clean"))

    star_check.release(_pr(labels=[stop]), dry_run=False)

    assert api.writes() == []


def test_a_draft_is_never_released(fake):
    api = fake(_release_routes("clean"))

    star_check.release(_pr() | {"draft": True}, dry_run=False)

    assert api.writes() == []


def test_a_star_clears_and_releases_only_the_starrers_pull_requests(fake):
    theirs = _pr(login="Fan", labels=["missing-star"], number=7) | {"auto_merge": None}
    other = _pr(login="other", labels=["missing-star"], number=8) | {"auto_merge": None}
    api = fake(
        {
            ("GET", f"repos/{star_check.REPO}/pulls?"): ([theirs, other], None),
            ("GET", f"repos/{star_check.REPO}/issues/7/comments"): ([], None),
        }
        | _release_routes("clean")
    )

    star_check.on_star("fan", dry_run=False)

    assert api.writes() == [
        ("DELETE", f"repos/{star_check.REPO}/issues/7/labels/missing-star"),
        ("PUT", f"repos/{star_check.REPO}/pulls/7/merge"),
    ]


def test_a_pull_request_event_leaves_the_merge_decision_to_auto_merge(fake):
    """auto-merge.yml decides on the event; only a sweep releases held ones."""
    api = fake(
        {STARGAZERS: ([{"login": "someone"}], None), NO_COMMENTS: ([], None)}
        | _release_routes("clean")
    )

    star_check.check(_pr() | {"auto_merge": None}, dry_run=False)

    assert not any(m == "PUT" for m, _ in api.writes())


def test_a_sweep_releases_a_starrers_held_pull_request(fake):
    api = fake(
        {
            STARGAZERS: ([{"login": "someone"}], None),
            ("GET", f"repos/{star_check.REPO}/issues/7/comments"): ([], None),
        }
        | _release_routes("clean")
    )

    star_check.check(_pr() | {"auto_merge": None}, dry_run=False, release_held=True)

    assert ("PUT", f"repos/{star_check.REPO}/pulls/7/merge") in api.writes()


def test_a_sweep_leaves_a_pull_request_already_auto_merging_alone(fake):
    api = fake(
        {STARGAZERS: ([{"login": "someone"}], None), NO_COMMENTS: ([], None)}
        | _release_routes("blocked")
    )

    star_check.check(
        _pr() | {"auto_merge": {"merge_method": "squash"}},
        dry_run=False,
        release_held=True,
    )

    assert api.writes() == []


def test_dry_run_writes_nothing(fake):
    api = fake({STARGAZERS: ([], None)})

    star_check.check(_pr(), dry_run=True)

    assert api.writes() == []


# --- the --starred probe the workflows call ------------------------------------------


@pytest.mark.parametrize(("stars", "code"), [([{"login": "fan"}], 0), ([], 1)])
def test_starred_probe_exit_code(fake, monkeypatch, stars, code):
    fake({STARGAZERS: (stars, None)})
    monkeypatch.setattr("sys.argv", ["star_check.py", "--starred", "fan"])

    assert star_check.main() == code
