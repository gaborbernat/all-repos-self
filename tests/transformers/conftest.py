from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Protocol

import pytest
from all_repos import autofix_lib, clone

if TYPE_CHECKING:
    from pytest_mock import MockerFixture


@dataclass(frozen=True, slots=True, kw_only=True)
class Fleet:
    config: Path
    origins: Path

    def files(self, name: str) -> dict[str, str]:
        origin = self.origins / f"{name}.git"
        names = _git(origin, "ls-tree", "-r", "--name-only", "HEAD").splitlines()
        return {path: _git(origin, "show", f"HEAD:{path}") for path in names}


class MakeFleet(Protocol):
    def __call__(self, repos: dict[str, dict[str, str]]) -> Fleet: ...


@pytest.fixture
def make_fleet(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> MakeFleet:
    # keep the user's git config (signing, hooks, default branch) out of the commits all-repos makes
    (git_config := tmp_path / "gitconfig").touch()
    for key, value in {
        "GIT_CONFIG_GLOBAL": str(git_config),
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_AUTHOR_NAME": "tester",
        "GIT_AUTHOR_EMAIL": "tester@example.com",
        "GIT_COMMITTER_NAME": "tester",
        "GIT_COMMITTER_EMAIL": "tester@example.com",
    }.items():
        monkeypatch.setenv(key, value)

    def make(repos: dict[str, dict[str, str]]) -> Fleet:
        origins = tmp_path / "origins"
        for name, files in repos.items():
            (seed := tmp_path / "seed" / name).mkdir(parents=True)
            for path, content in {**files, "tools.log": ""}.items():
                (seed / path).write_text(content, encoding="utf-8")
            _git(seed, "init", "--quiet", "--initial-branch", "main")
            _git(seed, "add", ".")
            _git(seed, "commit", "--quiet", "--message", "seed")
            _git(tmp_path, "clone", "--quiet", "--bare", str(seed), str(origins / f"{name}.git"))
        (repos_file := tmp_path / "repos.json").write_text(
            json.dumps({name: str(origins / f"{name}.git") for name in repos}), encoding="utf-8"
        )
        config = tmp_path / "all-repos.json"
        config.write_text(
            json.dumps({
                "output_dir": str(tmp_path / "output"),
                "source": "all_repos.source.json_file",
                "source_settings": {"filename": str(repos_file)},
                "push": "all_repos.push.merge_to_master",
                "push_settings": {},
            }),
            encoding="utf-8",
        )
        config.chmod(0o600)  # all-repos refuses a config others can read
        clone.main(["-C", str(config), "-j", "1"])
        return Fleet(config=config, origins=origins)

    return make


@pytest.fixture
def tools(mocker: MockerFixture) -> None:
    real_run = autofix_lib.run

    def run(*cmd: str, check: bool = True) -> subprocess.CompletedProcess[str]:
        if cmd[0] == "git":
            return real_run(*cmd, check=check)
        # stand in for pre-commit and bump-deps-index, which need the network, by logging the call into a tracked file
        with Path("tools.log").open("a", encoding="utf-8") as log:
            log.write(f"{' '.join((Path(cmd[0]).name, *cmd[1:]))}\n")
        return subprocess.CompletedProcess(cmd, 0)

    mocker.patch.object(autofix_lib, "run", side_effect=run)


def _git(cwd: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True).stdout
