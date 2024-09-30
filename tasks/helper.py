"""Interact with GitHub."""

from __future__ import annotations

import json
import os
import subprocess
from abc import ABC, abstractmethod
from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser, Namespace
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import cached_property
from pathlib import Path
from typing import TYPE_CHECKING, Generic, TypeVar

from github import Auth, Github, PullRequest, Repository
from rich.align import Align
from rich.console import Console
from rich.table import Table

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable, Iterator

_T = TypeVar("_T")
_V = TypeVar("_V")


class GH(Github):
    def __init__(self) -> None:
        super().__init__(auth=Auth.Token(os.environ["GITHUB_TOKEN"]))

    @cached_property
    def repo_names(self) -> list[str]:
        raw_text = (Path(__file__).parents[1] / "repos.json").read_text()
        return [url[15:] for url in json.loads(raw_text).values()]

    @cached_property
    def open_prs(self) -> list[tuple[Repository, PullRequest]]:
        def _get_pulls(name: str) -> Iterator[tuple[Repository, PullRequest]]:
            repo = self.get_repo(name)
            for pr in repo.get_pulls():
                yield repo, pr

        return self._parallel(self.repo_names, _get_pulls)

    @staticmethod
    def _parallel(data: Iterable[_T], func: Callable[[_T], Iterator[_V]]) -> list[_V]:
        result: list[_T] = []
        with ThreadPoolExecutor(max_workers=12) as executor:
            future_to_url = {executor.submit(func, d): d for d in data}
            for future in as_completed(future_to_url):
                data = future.result()
                result.extend(data)
        return result


class CmdNamespace(Namespace):
    """Options for tox-ini-fmt tool."""

    cmd_name: str


T = TypeVar("T", bound=CmdNamespace)


class BaseCmd(ABC, Generic[T]):
    @staticmethod
    @abstractmethod
    def parser_name_alias_help() -> tuple[str, str, str]:
        raise NotImplementedError

    def __init__(self, parser: ArgumentParser) -> None:
        """Setup."""
        self.define_args(parser)

    @abstractmethod
    def define_args(self, parser: ArgumentParser) -> None:
        raise NotImplementedError

    @abstractmethod
    def run(self, opts: T, github: GH) -> None:
        raise NotImplementedError


class OpenPRsOption(CmdNamespace):
    open: bool


class OpenPRs(BaseCmd[OpenPRsOption]):
    @staticmethod
    def parser_name_alias_help() -> tuple[str, str, str]:
        return "pr", "p", "show open PRs"

    def define_args(self, parser: ArgumentParser) -> None:
        parser.add_argument("-o", "--open", action="store_true")

    def run(self, opts: OpenPRsOption, github: GH) -> None:
        prefix = os.path.commonprefix([pr.updated_at.isoformat() for _, pr in github.open_prs])
        table = Table(title=f"Pull requests @ {prefix}")
        for header in ["Date", "Org", "Repo", Align("Title", align="center")]:
            table.add_column(header)
        for repo, pr in sorted(
            github.open_prs,
            key=lambda d: (d[0].owner.login, d[0].name, d[1].updated_at.isoformat()),
            reverse=True,
        ):
            if opts.open:
                subprocess.check_call(["open", pr.html_url])
            table.add_row(
                pr.updated_at.isoformat()[len(prefix) :],
                repo.owner.login,
                repo.name,
                f'[link="{pr.html_url}"]{pr.title.strip()}[/link]',
            )
        Console().print(table)


class OpensOption(CmdNamespace):
    suffix: str


class Open(BaseCmd[OpensOption]):
    @staticmethod
    def parser_name_alias_help() -> tuple[str, str, str]:
        return "open", "o", "open GitHub page"

    def define_args(self, parser: ArgumentParser) -> None:
        parser.add_argument("suffix", default="", nargs="?", help="suffix")

    def run(self, opts: OpensOption, github: GH) -> None:
        table = Table(title="Open")
        for header in ["Org", Align("Repo", align="center")]:
            table.add_column(header)
        for org, repo in (i.split("/") for i in github.repo_names):
            url = f"https://github.com/{org}/{repo}/{opts.suffix}"
            subprocess.check_call(["open", url])
            table.add_row(org, f'[link="{url}"]{repo}[/link]')
        Console().print(table)


class HelpFormatter(ArgumentDefaultsHelpFormatter):
    def __init__(self, prog: str) -> None:
        super().__init__(prog, max_help_position=42, width=240)


def main() -> int:
    parser = ArgumentParser(formatter_class=HelpFormatter, prog="maintain", description="Maintainer helper")
    parser.add_argument("--github", action="store_true", default=False)
    sub_parsers = parser.add_subparsers(title="commands", help="command to execute", dest="cmd_name")
    sub_parsers.required = True

    commands: list[BaseCmd] = []
    cmd_classes: list[type[BaseCmd]] = [
        OpenPRs,
        Open,
    ]
    for cmd_class in cmd_classes:
        name, alias, help_text = cmd_class.parser_name_alias_help()
        sub_parser = sub_parsers.add_parser(name, aliases=[alias], help=help_text, formatter_class=HelpFormatter)
        commands.append(cmd_class(sub_parser))

    opts = CmdNamespace()
    parser.parse_args(namespace=opts)

    to_run = next(c for c in commands if opts.cmd_name in c.parser_name_alias_help()[:2])  # pragma: no branch
    github = GH()
    user = github.get_user()
    print(f"Running with user {user.name} ({user.login})")
    to_run.run(opts, github)


if __name__ == "__main__":
    main()
