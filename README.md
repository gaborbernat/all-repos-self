# `all-repos` scripts for Bernat Gabor maintenance

[![check](https://github.com/gaborbernat/all-repos-self/actions/workflows/check.yml/badge.svg)](https://github.com/gaborbernat/all-repos-self/actions/workflows/check.yml)
[![OpenSSF Scorecard](https://api.scorecard.dev/projects/github.com/gaborbernat/all-repos-self/badge)](https://scorecard.dev/viewer/?uri=github.com/gaborbernat/all-repos-self)
[![OpenSSF Best Practices](https://www.bestpractices.dev/projects/16279/badge)](https://www.bestpractices.dev/projects/16279)

These scripts make one change across every repository I maintain, instead of repeating it by hand in each. The fleet is
the list of repositories in `repos.json`; [all-repos](https://github.com/asottile/all-repos) clones it and opens one
pull request per repository from the `bgabor8` fork.

```bash
export GITHUB_TOKEN="your API token"
tox r -e dev
.tox/dev/bin/python transformers/bump_deps_tools.py -C all-repos.json -j 10
```

## Transformers

A transformer is an `all-repos` autofixer: it picks the repositories that need the change, applies it in a fresh clone,
and pushes a pull request for each one that ends up with a diff. They share the `all-repos` fixer options, and two of
them are worth reaching for before a fleet-wide run:

- `--dry-run` prints each diff without pushing, so you can check the change before it reaches the whole fleet.
- `--repos <path> ...` limits the run to the named clones, for trying a change on a few repositories first.

Both run `pre-commit` with a throwaway hook cache, so every run installs the hooks from scratch.

**`bump_deps_tools`** refreshes dependencies and tooling in every repository that uses `pre-commit`. It raises the
dependency lower bounds with [bump-deps-index](https://github.com/gaborbernat/bump-deps-index), moves the hooks to their
latest releases, and reruns them so the formatters apply their new style. Use it for the periodic refresh, when bot
updates fall behind or a tool release changes the formatting everywhere. It opens the pull request even when the hooks
still fail, because CI on that pull request is where the remaining breakage gets fixed.

**`drop_prettier`** migrates repositories off the `prettier` hook to `yamlfmt` for YAML and `mdformat` for Markdown, and
deletes the `prettier` configuration files. Use it when a repository still carries `prettier`; the others are left
alone. The hooks run twice after the swap, because the first pass rewrites files and only the second shows whether the
tree settles.

## Tasks

**`helper`** works on the fleet through the GitHub API, run with `tox r -e helper -- <command>`:

- `pr` lists the open pull requests across all repositories. Add `--merge-green-bots` to approve and enable auto-merge
  on `dependabot` and `pre-commit-ci` pull requests whose checks pass, which clears the routine update queue in one go.
  Add `--open` to open each listed pull request in the browser; with `--merge-green-bots` it skips the approved ones.
- `open <suffix>` opens the same page for every repository, for example `open settings/branches` to review branch
  protection across the fleet.

Both open pages with the macOS `open` command.

**`install_uv_python`** installs the CPython and PyPy builds pinned in the script through
[uv](https://github.com/astral-sh/uv) and links each as `pythonX.Y` or `pypyX.Y` in `~/.local/bin`. Use it when setting
up a Mac that needs every interpreter on the `PATH` for `tox`. It assumes macOS on Apple Silicon.
