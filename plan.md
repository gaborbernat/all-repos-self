# OSS release migration plan

Last reviewed: 2026-10-18. Scope: the 39 distinct repositories on <https://bernat.tech/oss>. `pypa/build` is excluded by request. Of the remaining 38, 29 publish independently and nine do not need a separate release flow.

This file tracks the rollout. Check a repository only after its workflow, credentials, branch and tag rulesets, and release verification are complete. The audit records starting points, not proof that an untested release path works.

## Credential decision

The prepare job builds a changelog, commits it to protected `main`, and pushes a release tag that starts the publishing workflow. `GITHUB_TOKEN` cannot perform that unattended protected-branch push under the intended ruleset. The release actor needs a branch and tag bypass.

**Decision pending:** choose the credential design before migrating more repositories. A credential exposed to one repository should not authorize writes to another. Avoid one App registration per repository if that boundary can be preserved without operating a large service.

| Design | Boundary | Cost |
| --- | --- | --- |
| One App, with its private key stored in every repository | Does not meet the boundary: every key can mint tokens for all repositories in the App installation. | Few registrations |
| One App installed only on each repository | Meets the boundary. The App is a specific ruleset bypass actor. | One App and key per repository |
| One App with a central OIDC-verified token broker | Repository workflows receive scoped, short-lived tokens; the broker retains a key covering the installation. | One App plus a service and access policy to operate |
| One write deploy key per repository | Git write access is limited to that repository. | One nonexpiring key per repository; `DeployKey` ruleset bypass names the actor type, not an individual key |

The security-first baseline is a repository-only App, as used by `tox-dev/peryx`. A write deploy key is the simpler no-App fallback when its broader repository authority and rotation burden are acceptable. A broker is the way to keep one shared App without putting its broad private key in repository workflows. Do not copy a shared App private key into every repository. Use a common workflow shape and credential names whichever design is selected.

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

1. Settle the credential design and prove it on one of the tox-dev PAT-backed repositories without publishing a real release. Plan PyPA App changes with an organization admin rather than assuming we can make them ourselves.
2. Migrate the six definite PAT users: filelock, platformdirs, pipdeptree, python-discovery, tox, and turbohtml. Audit `GH_RELEASE_TOKEN` in pipx and GitHub-write `RELEASE_TOKEN` in PyVenvManage, jetbrains-fish, and toml-fmt; GitHub does not reveal secret types.
3. Finish repositories with an existing changelog or App, preserving each publisher's special behavior.
4. Backfill and migrate the thirteen non-pytest-dev repositories without historical changelogs.
5. Migrate `pytest-dev/pytest-env` and `pytest-dev/pytest-print` last, with an organization admin involved if the App design is chosen.
6. Re-audit all 29 repositories against the common contract and update the checkboxes with links to the relevant commits, rulesets, and verification runs.
