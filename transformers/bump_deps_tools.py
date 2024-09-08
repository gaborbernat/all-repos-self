from __future__ import annotations

import argparse
import os
import sys
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any
from unittest.mock import patch

from all_repos import autofix_lib
from all_repos.grep import repos_matching

if TYPE_CHECKING:
    from collections.abc import Sequence

    from all_repos.config import Config

PC = str(Path(sys.executable).parent / "pre-commit")


def find_repos(config: Config) -> set[str]:
    return repos_matching(config, ("", "--", ".pre-commit-config.yaml"))


def apply_fix() -> None:
    autofix_lib.run(sys.executable, "-m", "bump_deps_index", "-p", "no")
    autofix_lib.run(PC, "autoupdate", "-j", "12")
    autofix_lib.run(PC, "run", "--all-files", check=False)


def check_fix(**kwargs: Any) -> None:  # noqa: ARG001,ANN401
    return None  # create PR even if the check fails


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    autofix_lib.add_fixer_args(parser)
    args = parser.parse_args(argv)
    autofix_lib.assert_importable("bump_deps_index", install="bump-deps-index")
    autofix_lib.require_version_gte("pre-commit", "3.8")

    today = datetime.now(tz=UTC).strftime("%Y-%m-%d")
    repos, config, commit, autofix_settings = autofix_lib.from_cli(
        args,
        find_repos=find_repos,
        msg="Bump deps and tools",
        branch_name=f"bump-{today}",
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
