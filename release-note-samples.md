# Release attribution samples

Bernát approved this format on 2026-10-18. No changelog or GitHub Release has been backfilled from this sheet. Each
linked PR was merged, and its author was checked against GitHub's PR API on 2026-10-18. The examples show the proposed
format. The backfill must retain each release’s facts, PR links, contributor credits, and category meaning while
changing its headings.

## Category and anchor proposal

Only user-visible changes get release notes. After format approval, apply these headings and stable anchors to every
existing tracked changelog release and GitHub Release description in all 29 repositories. Preserve release facts, tags,
assets, and ecosystem links. Each repository gets one PR with code, tracked changelog history, relevant contribution
guidance, and an exact before/after report for its GitHub Release bodies. Bernát reviews and merges each PR; no
auto-merge. Apply the reviewed GitHub Release body changes after merge. The tracked changelog and GitHub Release use
these headings:

| Tracked changelog | GitHub Release   | Use when                                         |
| ----------------- | ---------------- | ------------------------------------------------ |
| Added             | Features         | New capability                                   |
| Changes           | Changes          | Compatible behavior change                       |
| Fixed             | Bug fixes        | Behavior correction                              |
| Documentation     | Documentation    | Reader-facing docs change                        |
| Breaking changes  | Breaking changes | Incompatible behavior or dropped support         |
| Security          | Security         | Security fix or action users need to take        |
| Performance       | Performance      | Measurable performance change                    |
| Deprecated        | Deprecations     | Support slated for removal                       |
| Removed           | Removals         | Previously supported behavior removed            |
| Packaging         | Packaging        | Installation or downstream compatibility changes |

Omit empty sections. Internal maintenance, contributor workflow work, and packaging with no user impact use `skip news`.
Replace user-facing `misc` fragments with a specific category; remove the `misc` types still defined by python-discovery
and pipx. A distinct `change` fragment type keeps compatible changes separate from additions. Update contribution guides
and PR templates when these rules affect their instructions; the current issue templates do not mention release-note
rules.

Put an explicit anchor before each version and section heading, leaving the visible heading unchanged. Use a stable
release tag and category key in each anchor, such as `release-4-2-0-fixed`; do not derive it from the displayed title.
RST uses `.. _release-4-2-0-fixed:` and Markdown uses `<a name="release-4-2-0-fixed"></a>`. GitHub Release sections use
level-three headings. GitHub documents
[custom Markdown anchors](https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax#custom-anchors).

## Complete format examples

These are complete one-change release formats. `NEXT_VERSION`, `DATE`, and tag names are placeholders. The linked PRs
and authors are real; the historical backfill will retain every entry and fact from each tagged release. The
[review website](https://oss-release-review-2026.neonmoss6.chatgpt.site) has a paired example for every repository.

Markdown changelog, using a pre-commit-uv change:

```md
<a name="release-next-tag"></a>

## NEXT_VERSION (DATE)

<a name="release-next-tag-fixed"></a>

### Fixed

- Add Python 3.14 support ([#86](https://github.com/tox-dev/pre-commit-uv/pull/86)) by [@ssbarnea](https://github.com/ssbarnea).
```

Matching GitHub Release body:

```md
<a name="release-next-tag-fixed"></a>

### Bug fixes

- Add Python 3.14 support ([#86](https://github.com/tox-dev/pre-commit-uv/pull/86)) by @ssbarnea.

<a name="release-next-tag-new-contributors"></a>

### New Contributors

- @ssbarnea made their first contribution in https://github.com/tox-dev/pre-commit-uv/pull/86

[PyPI release](https://pypi.org/project/pre-commit-uv/NEXT_VERSION/)

**Full Changelog**: https://github.com/tox-dev/pre-commit-uv/compare/PREVIOUS_TAG...NEXT_TAG
```

RST changelog, using the existing `:user:` role in python-discovery:

```rst
.. _release-next-tag:

NEXT_VERSION (DATE)
===================

.. _release-next-tag-fixed:

Fixed
-----

- Discard unusable interpreter cache entries (:issue:`141`) - by :user:`darrenhuai`.
```

Matching GitHub Release body:

```md
<a name="release-next-tag-fixed"></a>

### Bug fixes

- Discard unusable interpreter cache entries ([#141](https://github.com/tox-dev/python-discovery/pull/141)) by @darrenhuai.

[PyPI release](https://pypi.org/project/python-discovery/NEXT_VERSION/)

**Full Changelog**: https://github.com/tox-dev/python-discovery/compare/PREVIOUS_TAG...NEXT_TAG
```

Pipx has no configured `:user:` role, so its RST changelog uses a standard RST link:

```rst
- Accept absolute ``file:///`` URLs as package specs (:issue:`2150`) - by `@srijan2607 <https://github.com/srijan2607>`_.
```

A combined pyproject-api entry keeps both verified PR authors:

```rst
- Validate in-tree backend paths and reject metadata directories containing the project root (:pull:`320`, :pull:`323`) - by :user:`blouirts123` and :user:`edsonsims`.
```

When one PR produces several user-visible changes, put each entry under its own heading with its verified PR and author.
Keep existing `by` credits in the changelog. For several verified human authors of one change, use `by @x, @y and @z`,
with each handle linked in the tracked changelog and mentioned on GitHub. Do not credit reviewers or bot accounts.
Mention a first-time human contributor only once in the GitHub Release. A bot PR needs no news entry unless it supplies
a user-facing fragment. Remove any automatic `skip news` label when it does; a bot-only entry has no `by` suffix.

## Per-repository attribution sample

The PR column is the source for the sample author, not a claim that every historical bullet already identifies its PR.
`:user:` is proposed only where that project's Sphinx setup supports it; pipx uses an explicit RST link. The GitHub
column is the suffix on the corresponding bullet. Existing contributor sections remain when they carry separate
information.

| Repository                           | Tracked changelog    | Verified example                                                                                                     | Changelog suffix                                         | GitHub suffix                    |
| ------------------------------------ | -------------------- | -------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------- | -------------------------------- |
| `gaborbernat/bump-deps-index`        | `docs/changelog.md`  | [#269](https://github.com/gaborbernat/bump-deps-index/pull/269)                                                      | `by [@gaborbernat](https://github.com/gaborbernat)`      | `by @gaborbernat`                |
| `gaborbernat/pypi-changes`           | `CHANGELOG.md`       | [#266](https://github.com/gaborbernat/pypi-changes/pull/266)                                                         | `by [@gaborbernat](https://github.com/gaborbernat)`      | `by @gaborbernat`                |
| `gaborbernat/mdformat-hugo`          | `CHANGELOG.md`       | [#35](https://github.com/gaborbernat/mdformat-hugo/pull/35)                                                          | `by [@gaborbernat](https://github.com/gaborbernat)`      | `by @gaborbernat`                |
| `tox-dev/mdformat-zola`              | `CHANGELOG.md`       | [#2](https://github.com/tox-dev/mdformat-zola/pull/2)                                                                | `by [@gaborbernat](https://github.com/gaborbernat)`      | `by @gaborbernat`                |
| `tox-dev/devpi-process`              | `CHANGELOG.md`       | [#290](https://github.com/tox-dev/devpi-process/pull/290)                                                            | `by [@gaborbernat](https://github.com/gaborbernat)`      | `by @gaborbernat`                |
| `tox-dev/xml-fmt`                    | `CHANGELOG.md`       | [#117](https://github.com/tox-dev/xml-fmt/pull/117)                                                                  | `by [@gaborbernat](https://github.com/gaborbernat)`      | `by @gaborbernat`                |
| `tox-dev/sphinx-argparse-cli`        | `CHANGELOG.md`       | [#95](https://github.com/tox-dev/sphinx-argparse-cli/pull/95)                                                        | `by [@webknjaz](https://github.com/webknjaz)`            | `by @webknjaz`                   |
| `tox-dev/pre-commit-uv`              | `CHANGELOG.md`       | [#86](https://github.com/tox-dev/pre-commit-uv/pull/86)                                                              | `by [@ssbarnea](https://github.com/ssbarnea)`            | `by @ssbarnea`                   |
| `tox-dev/tox-gh`                     | `CHANGELOG.md`       | [#305](https://github.com/tox-dev/tox-gh/pull/305)                                                                   | `by [@gaborbernat](https://github.com/gaborbernat)`      | `by @gaborbernat`                |
| `tox-dev/tox-ini-fmt`                | `CHANGELOG.md`       | [#119](https://github.com/tox-dev/tox-ini-fmt/pull/119)                                                              | `by [@pdecat](https://github.com/pdecat)`                | `by @pdecat`                     |
| `tox-dev/pyproject-api`              | `docs/changelog.rst` | [#320](https://github.com/tox-dev/pyproject-api/pull/320), [#323](https://github.com/tox-dev/pyproject-api/pull/323) | `` by :user:`blouirts123` and :user:`edsonsims`  ``      | `by @blouirts123 and @edsonsims` |
| `tox-dev/python-discovery`           | `docs/changelog.rst` | [#141](https://github.com/tox-dev/python-discovery/pull/141)                                                         | `` by :user:`darrenhuai`  ``                             | `by @darrenhuai`                 |
| `tox-dev/peryx`                      | `CHANGELOG.md`       | [#2357](https://github.com/tox-dev/peryx/pull/2357)                                                                  | `by [@gaborbernat](https://github.com/gaborbernat)`      | `by @gaborbernat`                |
| `tox-dev/action-pre-commit-uv`       | `CHANGELOG.md`       | [#38](https://github.com/tox-dev/action-pre-commit-uv/pull/38)                                                       | `by [@gaborbernat](https://github.com/gaborbernat)`      | `by @gaborbernat`                |
| `tox-dev/jetbrains-fish`             | `CHANGELOG.md`       | [#113](https://github.com/tox-dev/jetbrains-fish/pull/113)                                                           | `by [@gaborbernat](https://github.com/gaborbernat)`      | `by @gaborbernat`                |
| `tox-dev/PyVenvManage`               | `CHANGELOG.md`       | [#250](https://github.com/tox-dev/PyVenvManage/pull/250)                                                             | `by [@gaborbernat](https://github.com/gaborbernat)`      | `by @gaborbernat`                |
| `tox-dev/sphinx-autodoc-typehints`   | `docs/changelog.rst` | [#1090](https://github.com/tox-dev/sphinx-autodoc-typehints/pull/1090)                                               | `` by :user:`gaborbernat`  ``                            | `by @gaborbernat`                |
| `tox-dev/filelock`                   | `docs/changelog.rst` | [#831](https://github.com/tox-dev/filelock/pull/831)                                                                 | `` by :user:`gaborbernat`  ``                            | `by @gaborbernat`                |
| `tox-dev/platformdirs`               | `docs/changelog.rst` | [#619](https://github.com/tox-dev/platformdirs/pull/619)                                                             | `` by :user:`blouirts123`  ``                            | `by @blouirts123`                |
| `tox-dev/pipdeptree`                 | `docs/changelog.rst` | [#727](https://github.com/tox-dev/pipdeptree/pull/727)                                                               | `` by :user:`gaborbernat`  ``                            | `by @gaborbernat`                |
| `tox-dev/tox`                        | `docs/changelog.rst` | [#4173](https://github.com/tox-dev/tox/pull/4173)                                                                    | `` by :user:`pcbeingused333`  ``                         | `by @pcbeingused333`             |
| `tox-dev/turbohtml`                  | `docs/changelog.rst` | [#1395](https://github.com/tox-dev/turbohtml/pull/1395)                                                              | `` by :user:`gaborbernat`  ``                            | `by @gaborbernat`                |
| `pypa/pipx`                          | `docs/changelog.rst` | [#2150](https://github.com/pypa/pipx/pull/2150)                                                                      | `` by `@srijan2607 <https://github.com/srijan2607>`_  `` | `by @srijan2607`                 |
| `pypa/virtualenv`                    | `docs/changelog.rst` | [#3396](https://github.com/pypa/virtualenv/pull/3396)                                                                | `` by :user:`repzakske`  ``                              | `by @repzakske`                  |
| `tox-dev/tox-uv`                     | `CHANGELOG.md`       | [#332](https://github.com/tox-dev/tox-uv/pull/332)                                                                   | `by [@stephenfin](https://github.com/stephenfin)`        | `by @stephenfin`                 |
| `quotaline/quotaline`                | `CHANGELOG.md`       | [#7](https://github.com/quotaline/quotaline/pull/7)                                                                  | `by [@gaborbernat](https://github.com/gaborbernat)`      | `by @gaborbernat`                |
| `tox-dev/toml-fmt` (`pyproject-fmt`) | `CHANGELOG.md`       | [#480](https://github.com/tox-dev/toml-fmt/pull/480)                                                                 | `by [@gaborbernat](https://github.com/gaborbernat)`      | `by @gaborbernat`                |
| `tox-dev/toml-fmt` (`tox-toml-fmt`)  | `CHANGELOG.md`       | [#258](https://github.com/tox-dev/toml-fmt/pull/258)                                                                 | `by [@gaborbernat](https://github.com/gaborbernat)`      | `by @gaborbernat`                |
| `pytest-dev/pytest-env`              | `CHANGELOG.md`       | [#273](https://github.com/pytest-dev/pytest-env/pull/273)                                                            | `by [@edsonsims](https://github.com/edsonsims)`          | `by @edsonsims`                  |
| `pytest-dev/pytest-print`            | `CHANGELOG.md`       | [#268](https://github.com/pytest-dev/pytest-print/pull/268)                                                          | `by [@gaborbernat](https://github.com/gaborbernat)`      | `by @gaborbernat`                |

Quotaline has no GitHub Release in this repository yet; its row previews the first versioned release. The
`tox-dev/toml-fmt` rows cover both active distributions; `toml-fmt-common` has historical releases only. Tox-uv's GitHub
body must keep links to both PyPI distributions. The Action's floating `v1` Release remains a pointer to versioned
releases rather than a separate changelog.

## Validation before backfill

1. Capture the tagged changelog, current GitHub body, and release metadata for every tag. Keep a recovery copy outside
   the repositories.
1. Resolve PR authors from GitHub PR records. Parse PR references from fragments and release entries; require a human
   mapping for combined entries, issue-only references, direct commits, renamed accounts, or conflicting authors. Keep
   existing credited names when GitHub no longer resolves them.
1. Render both candidates without altering change descriptions. Preserve the category, contributor set, PR references,
   links, code spans, and any separate `New Contributors` section. Omit empty categories; use `Other changes` only when
   the source has no reliable category.
1. Check that each candidate has the same release facts and at least the original contributor credits. Require a no-wrap
   GitHub Markdown parse, the repository's Markdown or RST formatter, its documentation build when applicable, `prek`,
   and an idempotent second render. Reject a release if a credited author disappears or a newly introduced link fails.
   Keep an old unresolvable handle as text and record the exception.
1. Review all per-tag diffs and unresolved mappings before writing historical files or GitHub bodies. Edit only a
   Release's body through the API, then read it back and compare its metadata and asset digests. Verify the App-authored
   release commit with `prek` before tagging and verify the first new release in each repository.

After you approve the format, I will review the per-tag diffs before applying them. Entries with unresolved attribution
will stay unchanged and appear in the rollout report.
