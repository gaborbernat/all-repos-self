from __future__ import annotations

from typing import TYPE_CHECKING

from tasks import install_uv_python

if TYPE_CHECKING:
    from pathlib import Path

    import pytest
    from pytest_mock import MockerFixture


def test_run_installs_and_links_interpreters(
    mocker: MockerFixture, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("HOME", str(tmp_path))
    check_call = mocker.patch.object(install_uv_python, "check_call")

    install_uv_python.run()

    src, dest = tmp_path / "Library/Application Support/uv/python", tmp_path / ".local/bin"
    assert [" ".join(map(str, call.args[0])) for call in check_call.call_args_list] == [
        "uv python install cpython-3.8.20 --no-progress -r",
        f"ln -s -f {src}/cpython-3.8.20-macos-aarch64-none/bin/python {dest}/python3.8",
        "uv python install cpython-3.9.21 --no-progress -r",
        f"ln -s -f {src}/cpython-3.9.21-macos-aarch64-none/bin/python {dest}/python3.9",
        "uv python install cpython-3.10.16 --no-progress -r",
        f"ln -s -f {src}/cpython-3.10.16-macos-aarch64-none/bin/python {dest}/python3.10",
        "uv python install cpython-3.11.11 --no-progress -r",
        f"ln -s -f {src}/cpython-3.11.11-macos-aarch64-none/bin/python {dest}/python3.11",
        "uv python install cpython-3.12.9 --no-progress -r",
        f"ln -s -f {src}/cpython-3.12.9-macos-aarch64-none/bin/python {dest}/python3.12",
        "uv python install cpython-3.13.2 --no-progress -r",
        f"ln -s -f {src}/cpython-3.13.2-macos-aarch64-none/bin/python {dest}/python3.13",
        "uv python install pypy-3.8.16 --no-progress -r",
        f"ln -s -f {src}/pypy-3.8.16-macos-aarch64-none/bin/python {dest}/pypy3.8",
        "uv python install pypy-3.9.19 --no-progress -r",
        f"ln -s -f {src}/pypy-3.9.19-macos-aarch64-none/bin/python {dest}/pypy3.9",
        "uv python install pypy-3.10.14 --no-progress -r",
        f"ln -s -f {src}/pypy-3.10.14-macos-aarch64-none/bin/python {dest}/pypy3.10",
        f"ln -s -f {src}/cpython-3.13.2-macos-aarch64-none/bin/python {dest}/python",
    ]
