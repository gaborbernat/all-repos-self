from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from transformers.drop_prettier import main, replace_prettier

if TYPE_CHECKING:
    from .conftest import MakeFleet

_HOOKS = """\
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v6.0.0
    hooks:
      - id: end-of-file-fixer
"""
_PRETTIER = """\
  - repo: https://github.com/rbubley/mirrors-prettier
    rev: v3.6.2
    hooks:
      - id: prettier
        args: ["--print-width=120"]
"""
_RUFF = """\
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.17.3
    hooks:
      - id: ruff
"""
_YAMLFMT = """\
  - repo: https://github.com/google/yamlfmt
    rev: "v0.21.0"
    hooks:
      - id: yamlfmt
"""
_MDFORMAT = """\
  - repo: local
    hooks:
      - id: mdformat
        name: mdformat
        entry: mdformat --wrap 120
        language: python
        types: [markdown]
        additional_dependencies:
          - mdformat-gfm>=1
          - mdformat-ruff>=0.1.3
"""


@pytest.mark.usefixtures("tools")
def test_main_replaces_prettier_only_where_configured(make_fleet: MakeFleet) -> None:
    fleet = make_fleet({
        "styled": {
            ".pre-commit-config.yaml": f"{_HOOKS}{_PRETTIER}{_RUFF}",
            ".prettierrc": "{}\n",
            "prettier.config.js": "module.exports = {};\n",
        },
        "plain": {".pre-commit-config.yaml": f"{_HOOKS}{_RUFF}"},
    })

    assert main(["-C", str(fleet.config)]) == 0

    assert {name: fleet.files(name) for name in ("styled", "plain")} == {
        "styled": {
            ".pre-commit-config.yaml": f"{_HOOKS}{_YAMLFMT}{_MDFORMAT}{_RUFF}",
            "tools.log": "pre-commit run --all-files\npre-commit run --all-files\n",
        },
        "plain": {".pre-commit-config.yaml": f"{_HOOKS}{_RUFF}", "tools.log": ""},
    }


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        pytest.param(f"{_HOOKS}{_RUFF}", f"{_HOOKS}{_RUFF}", id="no-prettier"),
        pytest.param(f"{_HOOKS}{_PRETTIER}", f"{_HOOKS}{_YAMLFMT}{_MDFORMAT}", id="prettier-last"),
        pytest.param(f"{_HOOKS}{_PRETTIER}\n{_RUFF}", f"{_HOOKS}{_YAMLFMT}{_MDFORMAT}{_RUFF}", id="blank-line-after"),
        pytest.param(f"{_HOOKS}{_YAMLFMT}{_PRETTIER}", f"{_HOOKS}{_YAMLFMT}{_MDFORMAT}", id="keeps-yamlfmt"),
        pytest.param(f"{_HOOKS}{_PRETTIER}{_MDFORMAT}", f"{_HOOKS}{_YAMLFMT}{_MDFORMAT}", id="keeps-mdformat"),
        pytest.param(
            "- repo: https://github.com/rbubley/mirrors-prettier\n  rev: v3.6.2\n",
            "".join(line[2:] for line in f"{_YAMLFMT}{_MDFORMAT}".splitlines(keepends=True)),
            id="unindented",
        ),
    ],
)
def test_replace_prettier(text: str, expected: str) -> None:
    assert replace_prettier(text) == expected
