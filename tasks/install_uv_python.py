from __future__ import annotations

from pathlib import Path
from subprocess import check_call


def run() -> None:
    home = Path.home()
    src = home / Path("Library/Application Support/uv/python")
    dest = home / ".local" / "bin"
    # feeds from https://github.com/indygreg/python-build-standalone/releases
    py = {
        "cpython": ["3.8.20", "3.9.21", "3.10.16", "3.11.11", "3.12.9", "3.13.2"],
        "pypy": ["3.8.16", "3.9.19", "3.10.14"],
    }
    for impl, versions in py.items():
        for version in versions:
            check_call(["uv", "python", "install", f"{impl}-{version}", "--no-progress", "-r"])
            minor = ".".join(version.split(".")[:2])
            check_call([
                "ln",
                "-s",
                "-f",
                src / f"{impl}-{version}-macos-aarch64-none" / "bin" / "python",
                dest / f"{'python' if impl == 'cpython' else 'pypy'}{minor}",
            ])
    check_call([
        "ln",
        "-s",
        "-f",
        src / f"cpython-{py['cpython'][-1]}-macos-aarch64-none" / "bin" / "python",
        dest / "python",
    ])


if __name__ == "__main__":
    run()
