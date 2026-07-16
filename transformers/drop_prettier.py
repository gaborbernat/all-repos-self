from __future__ import annotations

import argparse
import os
import re
import sys
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING, Any, Final
from unittest.mock import patch

from all_repos import autofix_lib
from all_repos.grep import repos_matching

if TYPE_CHECKING:
    from collections.abc import Sequence

    from all_repos.config import Config

PC: Final = str(Path(sys.executable).parent / "pre-commit")
CONFIG: Final = ".pre-commit-config.yaml"
PRETTIER_REPO: Final = re.compile(r"\s*- repo:.*prettier")
YAMLFMT: Final = (
    "- repo: https://github.com/google/yamlfmt",
    '  rev: "v0.21.0"',
    "  hooks:",
    "    - id: yamlfmt",
)
MDFORMAT: Final = (
    "- repo: local",
    "  hooks:",
    "    - id: mdformat",
    "      name: mdformat",
    "      entry: mdformat --wrap 120",
    "      language: python",
    "      types: [markdown]",
    "      additional_dependencies:",
    "        - mdformat-gfm>=1",
    "        - mdformat-ruff>=0.1.3",
)


def replace_prettier(text: str) -> str:
    lines = text.splitlines(keepends=True)
    start = next((i for i, line in enumerate(lines) if PRETTIER_REPO.match(line)), None)
    if start is None:
        return text
    indent = lines[start][: len(lines[start]) - len(lines[start].lstrip())]
    end = start + 1
    while end < len(lines) and not (lines[end].strip() and _indent(lines[end]) <= len(indent)):
        end += 1
    kept = "".join(lines[:start]) + "".join(lines[end:])
    added = (() if "id: yamlfmt" in kept else YAMLFMT) + (() if "id: mdformat" in kept else MDFORMAT)
    block = "".join(f"{indent}{line}\n" for line in added)
    return "".join(lines[:start]) + block + "".join(lines[end:])


def _indent(line: str) -> int:
    return len(line) - len(line.lstrip())


def find_repos(config: Config) -> set[str]:
    return repos_matching(config, ("prettier", "--", CONFIG))


def apply_fix() -> None:
    path = Path(CONFIG)
    path.write_text(replace_prettier(path.read_text(encoding="utf-8")), encoding="utf-8")
    for stray in (*Path().glob(".prettier*"), *Path().glob("prettier.config.*")):
        autofix_lib.run("git", "rm", "--quiet", "--", str(stray))
    for _ in range(2):  # autofixers mutate on the first pass, so a second pass is needed to converge
        autofix_lib.run(PC, "run", "--all-files", check=False)


def check_fix(**kwargs: Any) -> None:  # noqa: ARG001,ANN401
    return None  # create the PR even when the reformat leaves the tree dirty


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    autofix_lib.add_fixer_args(parser)
    args = parser.parse_args(argv)
    autofix_lib.require_version_gte("pre-commit", "3.8")

    repos, config, commit, autofix_settings = autofix_lib.from_cli(
        args,
        find_repos=find_repos,
        msg="Replace prettier with mdformat and yamlfmt",
        branch_name="drop-prettier",
    )
    with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, {"PRE_COMMIT_HOME": tmp}):
        autofix_lib.fix(
            repos,
            apply_fix=apply_fix,
            check_fix=check_fix,
            config=config,
            commit=commit,
            autofix_settings=autofix_settings,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
