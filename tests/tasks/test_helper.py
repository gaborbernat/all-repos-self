from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING
from unittest.mock import MagicMock, call

import pytest
from github import GithubException

from tasks import helper

if TYPE_CHECKING:
    from pytest_mock import MockerFixture

_URL = "https://github.com/tox-dev/tox/pull/1"
_CHECKS = "get_commits.return_value.reversed.__getitem__.return_value.get_check_runs.return_value"


def _check(app: str, conclusion: str) -> MagicMock:
    # built at collection time for the parameter table, before the mocker fixture exists
    return MagicMock(conclusion=conclusion, **{"app.url": app})


@pytest.fixture
def github(mocker: MockerFixture, monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    monkeypatch.setenv("GITHUB_TOKEN", "token")
    monkeypatch.setenv("COLUMNS", "120")
    user = mocker.MagicMock(login="gaborbernat")
    user.configure_mock(name="Bernat Gabor")  # name is a Mock constructor argument, so it cannot be set via kwargs
    mocker.patch.object(helper.GH, "get_user", return_value=user)
    mocker.patch.object(helper.GH, "repo_names", ["tox-dev/tox", "pypa/virtualenv"])
    return mocker.patch.object(helper.GH, "get_repo")


@pytest.fixture
def pull(mocker: MockerFixture, github: MagicMock, request: pytest.FixtureRequest) -> MagicMock:
    pull = mocker.MagicMock(
        html_url=_URL,
        title=" Bump deps ",
        updated_at=datetime(2026, 11, 5, 10, 30, tzinfo=UTC),
        **{"user.login": "dependabot[bot]", **getattr(request, "param", {})},
    )
    repo = mocker.MagicMock(**{"owner.login": "tox-dev", "get_pulls.return_value": [pull]})
    repo.configure_mock(name="tox")
    github.side_effect = {
        "tox-dev/tox": repo,
        "pypa/virtualenv": mocker.MagicMock(**{"get_pulls.return_value": []}),
    }.get
    return pull


@pytest.fixture
def check_call(mocker: MockerFixture) -> MagicMock:
    return mocker.patch.object(helper.subprocess, "check_call")


@pytest.mark.usefixtures("pull", "check_call")
def test_pr_lists_open_pull_requests(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    monkeypatch.setattr("sys.argv", ["maintain", "pr"])

    helper.main()

    assert [line.rstrip() for line in capsys.readouterr().out.splitlines()] == [
        "Running with user Bernat Gabor (gaborbernat)",
        "           Pull requests @",
        "      2026-11-05T10:30:00+00:00",
        "┏━━━━━━┳━━━━━━━━━┳━━━━━━┳━━━━━━━━━━━┓",
        "┃ Date ┃ Org     ┃ Repo ┃   Title   ┃",
        "┡━━━━━━╇━━━━━━━━━╇━━━━━━╇━━━━━━━━━━━┩",
        "│      │ tox-dev │ tox  │ Bump deps │",
        "└──────┴─────────┴──────┴───────────┘",
    ]


@pytest.mark.parametrize("pull", [pytest.param({"user.login": "gaborbernat"}, id="human")], indirect=True)
@pytest.mark.usefixtures("pull")
def test_pr_open_launches_browser(monkeypatch: pytest.MonkeyPatch, check_call: MagicMock) -> None:
    monkeypatch.setattr("sys.argv", ["maintain", "pr", "--open"])

    helper.main()

    assert check_call.call_args_list == [call(["open", _URL])]


@pytest.mark.parametrize(
    ("pull", "expected"),
    [
        pytest.param(
            {_CHECKS: [_check("/apps/github-actions", "success"), _check("/apps/dependabot", "failure")]},
            (True, False, []),
            id="green-bot-approved",
        ),
        pytest.param(
            {
                _CHECKS: [_check("/apps/github-actions", "skipped")],
                "enable_automerge.side_effect": GithubException(405),
            },
            (True, False, []),
            id="automerge-refused-still-approved",
        ),
        pytest.param(
            {_CHECKS: [_check("/apps/github-actions", "failure")]},
            (False, True, [f"{_URL}: checks /apps/github-actions: failure"]),
            id="red-bot-opened",
        ),
        pytest.param(
            {"get_commits.side_effect": GithubException(500, {"message": "boom"})},
            (False, True, [f'{_URL}: GithubException(500 {{"message": "boom"}})']),
            id="checks-unreadable",
        ),
        pytest.param(
            {_CHECKS: [], "create_review.side_effect": GithubException(403, {"message": "denied"})},
            (True, True, [f'{_URL}: GithubException(403 {{"message": "denied"}})']),
            id="review-refused",
        ),
        pytest.param({"user.login": "gaborbernat"}, (False, True, []), id="human-ignored"),
    ],
    indirect=["pull"],
)
def test_pr_merge_green_bots(
    monkeypatch: pytest.MonkeyPatch,
    pull: MagicMock,
    check_call: MagicMock,
    capsys: pytest.CaptureFixture[str],
    expected: tuple[bool, bool, list[str]],
) -> None:
    monkeypatch.setattr("sys.argv", ["maintain", "pr", "--open", "--merge-green-bots"])

    helper.main()

    assert (
        pull.create_review.call_args_list == [call(event="APPROVE", body="LGTM!")],
        check_call.call_args_list == [call(["open", _URL])],
        [line for line in capsys.readouterr().out.splitlines() if line.startswith(_URL)],
    ) == expected


@pytest.mark.usefixtures("github")
def test_open_launches_each_repository(monkeypatch: pytest.MonkeyPatch, check_call: MagicMock) -> None:
    monkeypatch.setattr("sys.argv", ["maintain", "open", "issues"])

    helper.main()

    assert check_call.call_args_list == [
        call(["open", "https://github.com/tox-dev/tox/issues"]),
        call(["open", "https://github.com/pypa/virtualenv/issues"]),
    ]


def test_repo_names_strips_ssh_prefix(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GITHUB_TOKEN", "token")

    assert "tox-dev/tox" in helper.GH().repo_names
