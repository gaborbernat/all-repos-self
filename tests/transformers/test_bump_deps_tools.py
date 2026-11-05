from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from transformers.bump_deps_tools import main

if TYPE_CHECKING:
    from .conftest import MakeFleet


@pytest.mark.usefixtures("tools")
def test_main_bumps_repos_with_pre_commit(make_fleet: MakeFleet) -> None:
    fleet = make_fleet({"hooked": {".pre-commit-config.yaml": "repos: []\n"}, "bare": {"README.md": "bare\n"}})

    assert main(["-C", str(fleet.config)]) == 0

    assert {name: fleet.files(name) for name in ("hooked", "bare")} == {
        "hooked": {
            ".pre-commit-config.yaml": "repos: []\n",
            "tools.log": ("python -m bump_deps_index -p no\npre-commit autoupdate -j 12\npre-commit run --all-files\n"),
        },
        "bare": {"README.md": "bare\n", "tools.log": ""},
    }
