# OSS release migration plan

Last reviewed: 2026-10-18. Scope: the 39 distinct repositories on <https://bernat.tech/oss>. `pypa/build` is excluded by request. Of the remaining 38, 29 publish independently and nine do not need a separate release flow.

This file tracks the rollout. Check a repository only after its workflow, credentials, branch and tag rulesets, and release verification are complete. The audit records starting points, not proof that an untested release path works.

## Credential decision

The prepare job builds a changelog, commits it to protected `main`, and pushes a release tag that starts the publishing workflow. `GITHUB_TOKEN` cannot perform that unattended protected-branch push under the intended ruleset. The release actor needs a branch and tag bypass.

**Decision:** use one GitHub App per repository, installed only on that repository. Store its private key in the repository's protected release environment and back it up in Insync. A credential exposed to one repository must not authorize writes to another. A shared App would require a separately operated OIDC token broker, which is outside this rollout.

| Design | Boundary | Cost |
| --- | --- | --- |
| One App, with its private key stored in every repository | Does not meet the boundary: every key can mint tokens for all repositories in the App installation. | Few registrations |
| One App installed only on each repository | Meets the boundary. The App is a specific ruleset bypass actor. | One App and key per repository |
| One App with a central OIDC-verified token broker | Repository workflows receive scoped, short-lived tokens; the broker retains a key covering the installation. | One App plus a service and access policy to operate |
| One write deploy key per repository | Git write access is limited to that repository. | One nonexpiring key per repository; `DeployKey` ruleset bypass names the actor type, not an individual key |

Use the repository-only App pattern already established by `tox-dev/peryx`. Do not copy a shared App private key into every repository. Use common workflow credential names across repositories.

**PyPA access constraint:** we are not PyPA organization admins and cannot create a PyPA-owned App. The App route for `pypa/pipx` needs a PyPA owner to provision or approve it. `pypa/virtualenv` already uses a PyPA App, but changes to that App or its installation also need owner coordination. If PyPA does not provision an App, assess a repository-only write deploy key against the repository's permissions and rulesets before choosing it.

**pytest-dev access constraint:** we are not pytest-dev organization admins and cannot create pytest-dev-owned Apps. Leave `pytest-env` and `pytest-print` until the other migrations are complete, then coordinate App setup with a pytest-dev owner or assess repository-only deploy keys against their rulesets.

## Common release contract

- [ ] Preserve or backfill a versioned changelog through the latest release.
- [ ] Require a PR news fragment, with only explicit `skip news` exceptions. A skipped fragment job must be accepted by the aggregate only when the exception applies.
- [ ] Add one required aggregate check that runs with `always()` and collects all CI matrix jobs and the applicable fragment job. Keep external checks such as pre-commit.ci required separately where used.
- [ ] Protect the default branch with a ruleset requiring the aggregate and allowing admin and the chosen release actor to bypass.
- [ ] Protect release tags against creation, update, and deletion except for admin and the release actor.
- [ ] Limit the prepare job to the default branch and a protected release environment. Build the changelog, commit it to `main`, then push the tag using the release actor.
- [ ] Make the tag start the release workflow. Verify that the changelog contains the released version before publishing. Use PyPI Trusted Publishing where applicable; keep other registry credentials separate from GitHub write credentials.
- [ ] Prove a fragment-free PR is blocked, verify the aggregate and bypass, exercise a non-publishing release path, and retire the old credential only after the replacement works.

## Changelog location and documentation

A documentation site is not a prerequisite for the release model. Every independently released repository needs a tracked, readable changelog. The PR fragment check and release-time version check apply whether that file is under `docs/` or at the repository root.

- Repositories with a docs changelog already: `pypa/pipx`, `pypa/virtualenv`, `tox-dev/filelock`, `tox-dev/pipdeptree`, `tox-dev/platformdirs`, `tox-dev/python-discovery`, `tox-dev/sphinx-autodoc-typehints`, `tox-dev/tox`, and `tox-dev/turbohtml`. Keep the changelog in the docs navigation.
- Repositories with docs but no tracked changelog: `gaborbernat/bump-deps-index` and `tox-dev/pyproject-api`. Backfill a changelog in the existing docs tree and link it from the docs index.
- Repositories with a root `CHANGELOG.md`: `tox-dev/PyVenvManage`, `tox-dev/devpi-process`, `tox-dev/jetbrains-fish`, `tox-dev/peryx`, and `tox-dev/sphinx-argparse-cli`. Keep that location. Retain peryx's link from its site.
- Repositories with neither docs nor a tracked changelog: `gaborbernat/mdformat-hugo`, `gaborbernat/pypi-changes`, `pytest-dev/pytest-env`, `pytest-dev/pytest-print`, `quotaline/quotaline`, `tox-dev/action-pre-commit-uv`, `tox-dev/mdformat-zola`, `tox-dev/pre-commit-uv`, `tox-dev/toml-fmt`, `tox-dev/tox-gh`, `tox-dev/tox-ini-fmt`, `tox-dev/tox-uv`, and `tox-dev/xml-fmt`. Backfill a root `CHANGELOG.md`, link it from `README.md`, and keep incoming fragments in a tracked directory such as `changelog.d/` or the project's existing changeset directory. Do not create a docs site solely for the changelog.

The fragment tool may differ by project, but its PR check must enforce the same policy and its prepare job must fold fragments into the versioned changelog. For `toml-fmt`, make the two package histories identifiable in that root changelog.

## Code PRs

Prepare and verify the code PRs before changing App installations, secrets, or rulesets. These links track code work; the release checklist below remains open until the repository's complete release path is verified.

- [ ] `tox-dev/peryx`: [PR #2375](https://github.com/tox-dev/peryx/pull/2375) requires a change file and guards the published version.
- [ ] `tox-dev/filelock`: [PR #857](https://github.com/tox-dev/filelock/pull/857) collects tests and the news check in one CI gate.
- [ ] `tox-dev/platformdirs`: [PR #628](https://github.com/tox-dev/platformdirs/pull/628) collects tests and the news check in one CI gate.
- [ ] `tox-dev/pipdeptree`: [PR #735](https://github.com/tox-dev/pipdeptree/pull/735) requires news fragments, includes them in the aggregate, and guards publication.
- [ ] `tox-dev/tox`: [PR #4175](https://github.com/tox-dev/tox/pull/4175) requires news fragments, adds an aggregate, and guards publication.
- [ ] `tox-dev/turbohtml`: [PR #1538](https://github.com/tox-dev/turbohtml/pull/1538) requires news fragments, adds an aggregate, and guards publication.
- [ ] `pypa/pipx`: [PR #2161](https://github.com/pypa/pipx/pull/2161) requires news fragments, adds an aggregate, and guards publication.
- [ ] `pypa/virtualenv`: [PR #3445](https://github.com/pypa/virtualenv/pull/3445) requires news fragments in its aggregate and guards publication.
- [ ] `tox-dev/python-discovery`: [PR #151](https://github.com/tox-dev/python-discovery/pull/151) requires news fragments, adds an aggregate, guards publication, and replaces force pushes with fast-forward release refs.
- [ ] `tox-dev/mdformat-zola`: [PR #36](https://github.com/tox-dev/mdformat-zola/pull/36) backfills its first release and adds fragment, aggregate, and publish checks. Preparation remains to be added after the credential choice.
- [ ] `gaborbernat/mdformat-hugo`: [PR #35](https://github.com/gaborbernat/mdformat-hugo/pull/35) backfills three tags and adds fragment, aggregate, and publish checks. Preparation remains to be added after the credential choice.
- [ ] `tox-dev/devpi-process`: [PR #287](https://github.com/tox-dev/devpi-process/pull/287) backfills versions 0.3.1 through 1.3.0 and adds fragment, aggregate, and publish checks. Preparation remains to be added after the credential choice.
- [ ] `tox-dev/sphinx-argparse-cli`: [PR #372](https://github.com/tox-dev/sphinx-argparse-cli/pull/372) moves released changes out of `Unreleased` and adds fragment, aggregate, and publish checks. Preparation remains to be added after the credential choice.
- [ ] `tox-dev/xml-fmt`: [PR #123](https://github.com/tox-dev/xml-fmt/pull/123) backfills five releases and adds fragment, aggregate, and publish checks. Preparation remains to be added after the credential choice.
- [ ] `tox-dev/tox-ini-fmt`: [PR #380](https://github.com/tox-dev/tox-ini-fmt/pull/380) restores the early changelog, backfills all 26 tags, and adds fragment, aggregate, and publish checks. Preparation remains to be added after the credential choice.
- [ ] `tox-dev/tox-gh`: [PR #308](https://github.com/tox-dev/tox-gh/pull/308) backfills all 23 tags and adds fragment, aggregate, and publish checks. Preparation remains to be added after the credential choice.
- [ ] `gaborbernat/pypi-changes`: [PR #266](https://github.com/gaborbernat/pypi-changes/pull/266) backfills all 15 tags and adds fragment, aggregate, and publish checks. Preparation remains to be added after the credential choice.

`peryx` PR #2375 includes updates for the RustSec advisories that failed its `source` job. Confirm the new CI run before treating it as green.


## Released repositories

Each unchecked row represents the remaining work for that repository. Existing pieces noted after the dash should be retained and verified.

### Reference

- [x] `tox-dev/sphinx-autodoc-typehints`: require an aggregate covering the test matrix and PR changelog job; retain pre-commit.ci and admin/App bypass. Commit `1675a9c`; [run passed](https://github.com/tox-dev/sphinx-autodoc-typehints/actions/runs/39107100720).
- [x] Restrict its `tox-dev-release` App installation to `sphinx-autodoc-typehints` only.
- [ ] `tox-dev/sphinx-autodoc-typehints`: add a release-tag ruleset and verify the complete release contract.

### Existing changelog and preparation; persistent GitHub write credential

- [ ] `tox-dev/filelock`: replace the `RELEASE_TOKEN` PAT; retain the PR fragment and Towncrier preparation; add the aggregate and tag ruleset.
- [ ] `tox-dev/platformdirs`: replace the `RELEASE_TOKEN` PAT; retain the PR fragment and Towncrier preparation; add the aggregate and tag ruleset.
- [ ] `pypa/pipx`: replace `GH_RELEASE_TOKEN`; add required PR fragment and publish-time version checks, aggregate, and rulesets. A PyPA-owned App requires action by a PyPA organization admin; assess a repo-only deploy key if that route is unavailable.
- [ ] `tox-dev/pipdeptree`: replace `RELEASE_PAT`; verify the delegated preparation produces the changelog; add PR and publish gates, aggregate, and rulesets.
- [ ] `tox-dev/python-discovery`: replace `RELEASE_PAT`; add PR and publish gates, aggregate, and rulesets.
- [ ] `tox-dev/tox`: replace `RELEASE_PAT`; add PR and publish gates, aggregate, and rulesets.
- [ ] `tox-dev/turbohtml`: replace `RELEASE_PAT`; add PR and publish gates, aggregate, and rulesets.

### Already using an App

- [ ] `pypa/virtualenv`: coordinate with a PyPA organization admin to verify that its release App installation and stored key are limited to this repository; add missing PR and publish gates, aggregate, and tag protection as needed.
- [x] `tox-dev/peryx`: its `peryx-release` App is installed only on peryx. Keep it; the proposed migration to the shared App was cancelled without changing its secret or rulesets.
- [ ] `tox-dev/peryx`: require contributor changesets on PRs, remove the fallback that generates them from merged PRs, and add the missing publish gate. Retain its aggregate CI and branch/tag rulesets.

### Changelog exists; release chain differs

- [ ] `tox-dev/devpi-process`: add required PR check, preparation, publish guard, aggregate, and tag ruleset.
- [ ] `tox-dev/sphinx-argparse-cli`: add required PR check, preparation, publish guard, aggregate, and tag ruleset.
- [ ] `tox-dev/PyVenvManage`: replace the GitHub-write `RELEASE_TOKEN`; add required PR check, preparation, publish guard, aggregate, and tag ruleset.
- [ ] `tox-dev/jetbrains-fish`: create the changelog entry before publishing; replace only the GitHub-write `RELEASE_TOKEN`. Retain JetBrains Marketplace `PUBLISH_TOKEN` and signing credentials; add PR check, aggregate, and rulesets.

### Historical changelog absent

Backfill from existing tags and GitHub Releases before requiring new fragments. For each repository, also add preparation, a publish-time changelog guard, aggregate, and branch/tag rulesets.

- [ ] `gaborbernat/bump-deps-index`
- [ ] `gaborbernat/mdformat-hugo`
- [ ] `gaborbernat/pypi-changes`
- [ ] `pytest-dev/pytest-env`: migrate last; App setup needs a pytest-dev organization admin.
- [ ] `pytest-dev/pytest-print`: migrate last; App setup needs a pytest-dev organization admin.
- [ ] `tox-dev/action-pre-commit-uv`: preserve the GitHub Release event and floating Action tag updates, or adapt the trigger without losing them.
- [ ] `tox-dev/mdformat-zola`
- [ ] `tox-dev/pre-commit-uv`
- [ ] `tox-dev/pyproject-api`
- [ ] `tox-dev/tox-gh`
- [ ] `tox-dev/tox-ini-fmt`
- [ ] `tox-dev/tox-uv`
- [ ] `tox-dev/xml-fmt`
- [ ] `tox-dev/toml-fmt`: give its two packages separate versioned histories.
- [ ] `quotaline/quotaline`: preserve its desktop release channels and replace the current `GITHUB_TOKEN` tag-plus-dispatch chain with the chosen release actor.

## Repositories without an independent release

These remain in the maintenance inventory. Do not create release changelogs merely to make them match the package template.

- [x] `gaborbernat/all-repos-self`: maintenance scripts and inventory.
- [x] `gaborbernat/bernat-tech`: website deployment.
- [x] `gaborbernat/cv`: CV deployment.
- [x] `gaborbernat/dotfiles`: personal configuration.
- [x] `gaborbernat/gaborbernat`: profile repository.
- [x] `gaborbernat/ropi_jegyzet_latex`: Pages site.
- [x] `pypa/get-virtualenv`: generated by virtualenv.
- [x] `tox-dev/pyproject-fmt`: generated mirror of toml-fmt.
- [x] `tox-dev/tox-toml-fmt`: generated mirror of toml-fmt.

`pypa/build` is listed on the OSS page but excluded from this migration by request.

`repos.json` also contains `token-menu-bar-macos`, which is not on the OSS page. Its URL redirects to the archived `quotaline/token-menu-bar-macos` repository. Track that inventory drift separately; it is not counted among the 39 OSS listings or 29 release migrations.

## Rollout order

1. Prepare all code PRs for repository-only Apps and wait for their checks before changing GitHub settings. Prove the design on one tox-dev PAT-backed repository without publishing a real release. Plan PyPA App changes with an organization admin rather than assuming we can make them ourselves.
2. Migrate the six definite PAT users: filelock, platformdirs, pipdeptree, python-discovery, tox, and turbohtml. Audit `GH_RELEASE_TOKEN` in pipx and GitHub-write `RELEASE_TOKEN` in PyVenvManage, jetbrains-fish, and toml-fmt; GitHub does not reveal secret types.
3. Finish repositories with an existing changelog or App, preserving each publisher's special behavior.
4. Backfill and migrate the thirteen non-pytest-dev repositories without historical changelogs.
5. Migrate `pytest-dev/pytest-env` and `pytest-dev/pytest-print` last, with an organization admin involved if the App design is chosen.
6. Re-audit all 29 repositories against the common contract and update the checkboxes with links to the relevant commits, rulesets, and verification runs.
