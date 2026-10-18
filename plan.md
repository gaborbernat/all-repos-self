# OSS release migration plan

Last reviewed: 2026-10-18. Scope: the 39 distinct repositories on <https://bernat.tech/oss>. `pypa/build` is excluded by request. Of the remaining 38, 29 publish independently and nine do not need a separate release flow.

This file tracks the rollout. Check a repository only after its workflow, credentials, branch and tag rulesets, and a new published release are verified. The audit records starting points, not proof that an untested release path works.

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

Grant Contents write to each release App. `tox-dev/PyVenvManage`, `tox-dev/jetbrains-fish`, `tox-dev/toml-fmt`, and `quotaline/quotaline` also need Pull requests and Issues write for maintenance or cask PRs. Install each App on its named repository only, disable webhooks, and store the `RELEASE_APP_CLIENT_ID` variable and `RELEASE_APP_PRIVATE_KEY` secret in that repository's `release-auth` environment. Restrict that environment to `main` and, where a tag-triggered App job needs it, the repository's release tag pattern. Keep the existing `release` environment for `tox-dev/sphinx-autodoc-typehints`.

At token creation, set `repositories` to the current repository and request only the job's `permission-*` values. A release commit and tag needs Contents write; a maintenance PR job additionally needs Pull requests and Issues write for creating and labeling PRs. Give the tag workflow's GitHub Release job only `contents: write`; keep PyPI OIDC in a separate job.

**PyPA access constraint:** we are not PyPA organization admins and cannot create a PyPA-owned App. The App route for `pypa/pipx` needs a PyPA owner to provision or approve it. `pypa/virtualenv` already uses a PyPA App, but changes to that App or its installation also need owner coordination. If PyPA does not provision an App, assess a repository-only write deploy key against the repository's permissions and rulesets before choosing it.

**pytest-dev access constraint:** we are not pytest-dev organization admins and cannot create pytest-dev-owned Apps. Leave `pytest-env` and `pytest-print` until the other migrations are complete, then coordinate App setup with a pytest-dev owner or assess repository-only deploy keys against their rulesets.

## Common release contract

- [ ] Preserve or backfill a versioned changelog through the latest release.
- [ ] Require a user-facing PR news fragment, with only explicit `skip news` exceptions. Do not offer a `misc` category for internal changes. The `skip news` label may be added after a PR opens; the fragment job must rerun on label changes, and the aggregate must accept a skipped job only for that exception.
- [ ] Apply `skip news` automatically when Dependabot or our own CI automation opens a PR without user-facing news. Preserve existing dependency labels, and add the label in each PR-creating workflow where applicable.
- [ ] Add one required aggregate check that runs with `always()` and collects all CI matrix jobs and the applicable fragment job. Keep external checks such as pre-commit.ci required separately where used.
- [ ] Protect the default branch with a ruleset requiring the aggregate and allowing admin and the chosen release actor to bypass. Keep the required review count at zero and disable extra approval for unattributed changes; these repositories have one maintainer.
- [ ] Protect release tags against creation, update, and deletion except for admin and the release actor.
- [ ] Apply the relevant Actions safeguards from [the Secure Open Source Fund notes](https://gist.github.com/gaborbernat/bc6795c27533d9d8dcc3cc2dd1ffeaa4): pin third-party actions to commit SHAs, give PR jobs read-only permissions and no release secrets, avoid shared caches in privileged release jobs, keep GitHub write permissions narrow, and avoid direct untrusted expressions in scripts.
- [ ] Limit the prepare job to the default branch and a protected release environment. Build the changelog, commit it to `main`, then push the tag using the release actor.
- [ ] Refresh `main` before applying a release patch or building notes, so an unrelated merge during preparation does not make the protected push stale. Reject a concurrent change to release inputs rather than overwrite it.
- [ ] Make the tag start the release workflow. Verify that the changelog contains the released version before publishing. Use PyPI Trusted Publishing where applicable; keep other registry credentials separate from GitHub write credentials.
- [ ] Publish a GitHub Release for every released tag after the ecosystem publication succeeds. Use that tag's changelog section for notes, link the ecosystem release and the diff from the previous version tag, avoid GitHub's generated-notes comment, and verify both destinations for each rollout release. Backfill existing GitHub Releases to the same style and create any missing GitHub Releases for published tags.
- [ ] Resolve newly added action pins against upstream releases immediately before pushing a rollout PR. On 2026-10-18, the current pins are `actions/create-github-app-token` v3.3.0 (`64ab729a6294000f5aa4a4bc0b73d1f32bc45510`) and `astral-sh/setup-uv` v10.3.0 (`1c37ad07a6a961277cf70c0d37d6f313000f5884`).
- [ ] Prove a fragment-free PR is blocked, verify the aggregate and bypass, cut and verify a new published release, and retire the old credential only after the replacement works.

## Changelog location and documentation

A documentation site is not a prerequisite for the release model. Every independently released repository needs a tracked, readable changelog. The PR fragment check and release-time version check apply whether that file is under `docs/` or at the repository root.

- Repositories with a docs changelog already: `pypa/pipx`, `pypa/virtualenv`, `tox-dev/filelock`, `tox-dev/pipdeptree`, `tox-dev/platformdirs`, `tox-dev/python-discovery`, `tox-dev/sphinx-autodoc-typehints`, `tox-dev/tox`, and `tox-dev/turbohtml`. Keep the changelog in the docs navigation.
- Repositories with docs but no tracked changelog: `gaborbernat/bump-deps-index` and `tox-dev/pyproject-api`. Backfill a changelog in the existing docs tree and link it from the docs index.
- Repositories with a root `CHANGELOG.md`: `tox-dev/PyVenvManage`, `tox-dev/devpi-process`, `tox-dev/jetbrains-fish`, `tox-dev/peryx`, and `tox-dev/sphinx-argparse-cli`. Keep that location. Retain peryx's link from its site.
- Repositories with neither docs nor a tracked changelog: `gaborbernat/mdformat-hugo`, `gaborbernat/pypi-changes`, `pytest-dev/pytest-env`, `pytest-dev/pytest-print`, `quotaline/quotaline`, `tox-dev/action-pre-commit-uv`, `tox-dev/mdformat-zola`, `tox-dev/pre-commit-uv`, `tox-dev/toml-fmt`, `tox-dev/tox-gh`, `tox-dev/tox-ini-fmt`, `tox-dev/tox-uv`, and `tox-dev/xml-fmt`. Backfill a root `CHANGELOG.md`, link it from `README.md`, and keep incoming fragments in a tracked directory such as `changelog.d/` or the project's existing changeset directory. Do not create a docs site solely for the changelog.

The fragment tool may differ by project, but its PR check must enforce the same policy and its prepare job must fold fragments into the versioned changelog. For `toml-fmt`, make the two package histories identifiable in that root changelog.

## Code PRs

Complete one repository at a time: verify its code PR, configure its repository-only App and GitHub settings, then hand the PR to Bernát to merge. These links track code work; the release checklist below remains open until the repository's complete release path is verified.

- [ ] `tox-dev/sphinx-autodoc-typehints`: [PR #1091](https://github.com/tox-dev/sphinx-autodoc-typehints/pull/1091) separates Towncrier from the credentialed release push and checks the patch before minting the App token.
- [x] `tox-dev/peryx`: [PR #2375](https://github.com/tox-dev/peryx/pull/2375) requires a change file and guards the published version.
- [ ] `tox-dev/filelock`: [PR #857](https://github.com/tox-dev/filelock/pull/857) collects tests and the news check in one CI gate and replaces the release PAT with a repository App token.
- [ ] `tox-dev/platformdirs`: [PR #628](https://github.com/tox-dev/platformdirs/pull/628) collects tests and the news check in one CI gate and replaces the release PAT with a repository App token.
- [ ] `tox-dev/pipdeptree`: [PR #735](https://github.com/tox-dev/pipdeptree/pull/735) requires news fragments, includes them in the aggregate, guards publication, and replaces the release PAT with a repository App token.
- [ ] `tox-dev/tox`: [PR #4175](https://github.com/tox-dev/tox/pull/4175) requires news fragments, adds an aggregate, guards publication, replaces the release PAT, and removes force pushes from preparation.
- [ ] `tox-dev/turbohtml`: [PR #1538](https://github.com/tox-dev/turbohtml/pull/1538) requires news fragments, adds an aggregate, guards publication, replaces the release PAT, and removes force pushes from preparation.
- [x] `pypa/pipx`: [PR #2161](https://github.com/pypa/pipx/pull/2161) requires news fragments, adds an aggregate, guards publication, and replaces the GitHub write token with a repository App token. PyPA admin setup remains.
- [x] `pypa/virtualenv`: [PR #3445](https://github.com/pypa/virtualenv/pull/3445) requires news fragments in its aggregate, guards publication, and pushes the release commit and tag atomically.
- [ ] `tox-dev/python-discovery`: [PR #151](https://github.com/tox-dev/python-discovery/pull/151) requires news fragments, adds an aggregate, guards publication, replaces force pushes with fast-forward release refs, and replaces the release PAT with a repository App token.
- [ ] `tox-dev/mdformat-zola`: [PR #36](https://github.com/tox-dev/mdformat-zola/pull/36) backfills its first release, includes a `1.0.1` fragment, and adds fragment, aggregate, publish, and App-backed preparation workflows. Its final CI run is pending.
- [x] `gaborbernat/mdformat-hugo`: [PR #35](https://github.com/gaborbernat/mdformat-hugo/pull/35) backfills three tags and adds fragment, aggregate, publish, and App-backed preparation workflows.
- [ ] `tox-dev/devpi-process`: [PR #287](https://github.com/tox-dev/devpi-process/pull/287) backfills versions 0.3.1 through 1.3.0 and adds fragment, aggregate, publish, and App-backed preparation workflows.
- [ ] `tox-dev/sphinx-argparse-cli`: [PR #372](https://github.com/tox-dev/sphinx-argparse-cli/pull/372) moves released changes out of `Unreleased` and adds fragment, aggregate, publish, and App-backed preparation workflows.
- [ ] `tox-dev/xml-fmt`: [PR #123](https://github.com/tox-dev/xml-fmt/pull/123) backfills five releases and adds fragment, aggregate, publish, and App-backed preparation workflows.
- [ ] `tox-dev/tox-ini-fmt`: [PR #380](https://github.com/tox-dev/tox-ini-fmt/pull/380) restores the early changelog, backfills all 26 tags, and adds fragment, aggregate, publish, and App-backed preparation workflows.
- [ ] `tox-dev/tox-gh`: [PR #308](https://github.com/tox-dev/tox-gh/pull/308) backfills all 23 tags and adds fragment, aggregate, publish, and App-backed preparation workflows.
- [x] `gaborbernat/pypi-changes`: [PR #266](https://github.com/gaborbernat/pypi-changes/pull/266) backfills all 15 tags, includes a `1.7.1` fragment, and adds fragment, aggregate, publish, and App-backed preparation workflows. Its final PR check passed.
- [ ] `tox-dev/pyproject-api`: [PR #324](https://github.com/tox-dev/pyproject-api/pull/324) restores all 34 tagged versions, adds fragment and aggregate checks, and prepares releases with a repository-only App.
- [x] `gaborbernat/bump-deps-index`: [PR #269](https://github.com/gaborbernat/bump-deps-index/pull/269) imports the notes for all 30 releases into the docs and adds fragment, aggregate, preparation, and publish checks.
- [ ] `tox-dev/pre-commit-uv`: [PR #186](https://github.com/tox-dev/pre-commit-uv/pull/186) backfills all 15 tags and adds fragment, aggregate, preparation, and publish checks.
- [ ] `tox-dev/tox-uv`: [PR #386](https://github.com/tox-dev/tox-uv/pull/386) backfills all 75 tags and adds fragment, aggregate, preparation, and publish checks for its two distributions.
- [ ] `tox-dev/action-pre-commit-uv`: [PR #39](https://github.com/tox-dev/action-pre-commit-uv/pull/39) backfills seven versioned releases and adds fragment, aggregate, App-backed preparation, and GitHub Release checks while retaining floating action tags.
- [ ] `tox-dev/jetbrains-fish`: [PR #144](https://github.com/tox-dev/jetbrains-fish/pull/144) backfills missing and placeholder changelog sections, adds fragment and aggregate checks, prepares releases with a repository App, and separates the post-release PR from Marketplace secrets.
- [ ] `tox-dev/PyVenvManage`: [PR #268](https://github.com/tox-dev/PyVenvManage/pull/268) backfills missing and placeholder changelog sections, adds fragment and aggregate checks, prepares releases with a repository App, and migrates post-release and mise-update PRs away from the PAT.
- [x] `quotaline/quotaline`: [PR #9](https://github.com/quotaline/quotaline/pull/9) backfills the archived macOS releases, requires fragments in the existing aggregate, waits for full CI on the changelog commit before tagging, and uses a repository App for protected Git writes and cask PRs. The existing GNOME, Direct, Homebrew, and App Store channels remain.
- [ ] `tox-dev/toml-fmt`: [PR #484](https://github.com/tox-dev/toml-fmt/pull/484) backfills all 86 tags across both active packages and the older `toml-fmt-common` releases, collects eight PR workflows and news in one gate, separates preparation from tag-triggered publishing, and replaces the PAT in maintenance PR jobs with the repository App. Mirror sync falls back to its daily schedule.
- [x] `pytest-dev/pytest-env`: [PR #276](https://github.com/pytest-dev/pytest-env/pull/276) backfills 25 tags, adds fragments and an aggregate, prepares tags with a repository App, and checks versioned notes and distributions before PyPI. App provisioning needs a pytest-dev organization admin.
- [x] `pytest-dev/pytest-print`: [PR #271](https://github.com/pytest-dev/pytest-print/pull/271) backfills 19 tags, adds fragments and an aggregate, prepares tags with a repository App, and checks versioned notes and distributions before PyPI. App provisioning needs a pytest-dev organization admin.

`peryx` PR #2375 includes updates for the RustSec advisories that failed its `source` job. Confirm the new CI run before treating it as green.

The checked code PRs have passing aggregate checks on their latest heads. The remaining new CI runs must finish before the settings phase.

### Adversarial review

Review the full diff, release path, permissions, changelog policy, and CI for every rollout PR. Keep fixes in that repository's PR. The first pass replaced GitHub write PATs in filelock, platformdirs, pipdeptree, tox, turbohtml, pipx, and python-discovery. Tox and turbohtml also stopped force pushing release refs. Those seven PRs use `skip news` for their internal changes. Twelve new workflows resolve the bot identity from the App token.

A later pass separated Towncrier from the App token in 14 code PRs and reference PR #1091. It made the same split for Knope in peryx and release tooling in pipx, pipdeptree, python-discovery, tox, and turbohtml. Reference PR #1091 now reruns its changelog check when `skip news` changes. Recheck CI before marking any PR ready.

A final release review replaced separate commit and tag pushes with an atomic push in 25 prepare workflows. Virtualenv PR #3445 now stages the generated changelog and pushes both refs atomically too; its App-authored commit loses the previous API signature. This prevents a rejected tag from leaving a release commit on `main` without a tag. Quotaline intentionally pushes the commit before running full CI, then tags it; a rerun can recover if its tag push fails. Pipx and peryx already used atomic release pushes. Rerun CI on all 26 updated PR heads.

Pipx PR #2161 and turbohtml PR #1538 now reject `misc` fragments in their naming hooks, PR checks, and release preparation. Both repositories' Towncrier configs omit that category, so allowing its filename would silently discard the entry. Commits `57f9c9a` and `f7c1ffe1`; rerun CI after these pushes.

The 28 remaining open release PRs now handle the release-base race and automation labels where applicable. The patch-based prepare jobs fetch and reset to current `main` before applying their validated patch. Single-job prepare flows refresh before reading fragments. Quotaline refreshes before version selection and refuses to tag if `main` moves after its full CI run. Virtualenv replays its generated changelog on current `main` only when the changelog, fragments, and release tooling have not changed since generation. All Dependabot ecosystems in these repositories request `skip news` while preserving existing dependency labels. Peryx's browser-update PR now requests it too; the other in-repository PR creators already label their non-news PRs or generate a fragment. Created the missing `skip news` labels in peryx and virtualenv. `prek` passed on the touched files; quotaline's system `jactionlint` hook required `mise exec` and was run that way after the remaining `prek` hooks passed. Review the new CI runs before treating these PRs as green.

The ruleset audit found that `pypa/virtualenv` currently requires one approving review and approval of the last push. Set the review count to zero and disable `require_last_push_approval`. Every active review ruleset sets `require_extra_approval_for_unattributed_changes=true`; disable it while retaining the admin bypass and replacing matrix check lists with the aggregate. Make these changes as each repository reaches its rollout turn.

Peryx already requires `ci-gate`, `conformance-gate`, and `codspeed-gate`; remove its separate `coverage` requirement because `ci-gate` collects it. Pipx and quotaline still use classic branch protection. Create the replacement branch ruleset with the aggregate and admin/App bypass before removing classic protection. Preserve pipx's linear-history rule and block its currently allowed force pushes; retain quotaline's required external checks.


## Released repositories

Each unchecked row represents the remaining work for that repository. Existing pieces noted after the dash should be retained and verified.

### Reference

- [x] `tox-dev/sphinx-autodoc-typehints`: require an aggregate covering the test matrix and PR changelog job; retain pre-commit.ci and admin/App bypass. Commit `1675a9c`; [run passed](https://github.com/tox-dev/sphinx-autodoc-typehints/actions/runs/39107100720).
- [x] Restrict its `tox-dev-release` App installation to `sphinx-autodoc-typehints` only.
- [ ] `tox-dev/sphinx-autodoc-typehints`: disable its current `require_extra_approval_for_unattributed_changes` rule. Its review count is already zero and its admin bypass is already configured.
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
- [ ] `tox-dev/peryx`: rotate the existing App key into `release-auth` and save a separate backup in Insync; the current secret cannot be read back and no peryx key backup was found.
- [ ] `tox-dev/peryx`: require contributor changesets on PRs, remove the fallback that generates them from merged PRs, and add the missing publish gate. Retain its aggregate CI and branch/tag rulesets.

### Changelog exists; release chain differs

- [ ] `tox-dev/devpi-process`: add required PR check, preparation, publish guard, aggregate, and tag ruleset.
- [ ] `tox-dev/sphinx-argparse-cli`: add required PR check, preparation, publish guard, aggregate, and tag ruleset.
- [ ] `tox-dev/PyVenvManage`: replace the GitHub-write `RELEASE_TOKEN`; add required PR check, preparation, publish guard, aggregate, and tag ruleset.
- [ ] `tox-dev/jetbrains-fish`: create the changelog entry before publishing; replace only the GitHub-write `RELEASE_TOKEN`. Retain JetBrains Marketplace `PUBLISH_TOKEN` and signing credentials; add PR check, aggregate, and rulesets.

### Historical changelog absent

Backfill from existing tags and GitHub Releases before requiring new fragments. For each repository, also add preparation, a publish-time changelog guard, aggregate, and branch/tag rulesets.

- [x] `gaborbernat/bump-deps-index`: [1.17.1 on PyPI](https://pypi.org/project/bump-deps-index/1.17.1/) and [GitHub](https://github.com/gaborbernat/bump-deps-index/releases/tag/1.17.1/) published after [prepare](https://github.com/gaborbernat/bump-deps-index/actions/runs/39148845245) and [publish](https://github.com/gaborbernat/bump-deps-index/actions/runs/39148880418) passed.
- [x] `gaborbernat/mdformat-hugo`: [0.3.1](https://pypi.org/project/mdformat-hugo/0.3.1/) published from the protected App-authored tag after [prepare](https://github.com/gaborbernat/mdformat-hugo/actions/runs/39144321245) and [publish](https://github.com/gaborbernat/mdformat-hugo/actions/runs/39144353734) passed.
- [x] `gaborbernat/pypi-changes`: [1.7.1](https://pypi.org/project/pypi-changes/1.7.1/) published from the protected App-authored tag after [prepare](https://github.com/gaborbernat/pypi-changes/actions/runs/39146089361) and [publish](https://github.com/gaborbernat/pypi-changes/actions/runs/39146118208) passed.
- [x] Backfilled [pypi-changes 1.7.1](https://github.com/gaborbernat/pypi-changes/releases/tag/1.7.1) and [mdformat-hugo 0.3.1](https://github.com/gaborbernat/mdformat-hugo/releases/tag/0.3.1) GitHub Releases from their tagged changelogs. GitHub Release automation merged in [pypi-changes PR #268](https://github.com/gaborbernat/pypi-changes/pull/268), [mdformat-hugo PR #39](https://github.com/gaborbernat/mdformat-hugo/pull/39), and [bump-deps-index PR #271](https://github.com/gaborbernat/bump-deps-index/pull/271). The bump-deps-index `1.17.1` release validated that automation.
- [ ] [mdformat-zola PR #36](https://github.com/tox-dev/mdformat-zola/pull/36) and [tox-gh PR #308](https://github.com/tox-dev/tox-gh/pull/308) now create a GitHub Release after PyPI. [toml-fmt PR #484](https://github.com/tox-dev/toml-fmt/pull/484) already creates GitHub Releases for both active packages. Those three open PRs now pin `create-github-app-token` v3.3.0 and `setup-uv` v10.3.0 where used. Check their new CI runs.
- [ ] [filelock PR #857](https://github.com/tox-dev/filelock/pull/857), [platformdirs PR #628](https://github.com/tox-dev/platformdirs/pull/628), [tox PR #4175](https://github.com/tox-dev/tox/pull/4175), [turbohtml PR #1538](https://github.com/tox-dev/turbohtml/pull/1538), and [pyproject-api PR #324](https://github.com/tox-dev/pyproject-api/pull/324) now create GitHub Releases from tagged changelog sections after PyPI succeeds. GitHub write access is confined to the new release job; the PyPI job keeps OIDC only. Their open PRs and [peryx PR #2375](https://github.com/tox-dev/peryx/pull/2375) now pin the current App-token and uv actions where used. Check the new CI runs.
- [ ] Merged rollout PRs needed GitHub Release follow-ups: [devpi-process #289](https://github.com/tox-dev/devpi-process/pull/289), [pre-commit-uv #188](https://github.com/tox-dev/pre-commit-uv/pull/188), [sphinx-argparse-cli #374](https://github.com/tox-dev/sphinx-argparse-cli/pull/374), [tox-ini-fmt #382](https://github.com/tox-dev/tox-ini-fmt/pull/382), [tox-uv #388](https://github.com/tox-dev/tox-uv/pull/388), and [xml-fmt #125](https://github.com/tox-dev/xml-fmt/pull/125). Each creates the GitHub Release after PyPI; tox-uv links both published distributions. They pin current actions and carry `skip news`. Check CI before merge.
- [ ] [pipdeptree #738](https://github.com/tox-dev/pipdeptree/pull/738) and [python-discovery #153](https://github.com/tox-dev/python-discovery/pull/153) move GitHub Release creation from preparation to after PyPI. [sphinx-autodoc-typehints #1092](https://github.com/tox-dev/sphinx-autodoc-typehints/pull/1092) separates GitHub write permission from the PyPI job. All three use the tagged changelog section instead of generated notes, pin the current App-token action, and carry `skip news`.
- [ ] [jetbrains-fish #146](https://github.com/tox-dev/jetbrains-fish/pull/146) and [PyVenvManage #270](https://github.com/tox-dev/PyVenvManage/pull/270) remove GitHub Contents write from the Marketplace publishing job. A separate job attaches the built artifact to the GitHub Release after Marketplace publication, and the post-release PR waits for that upload. Both pin the current App-token action and carry `skip news`.
- [ ] [pipx #2163](https://github.com/pypa/pipx/pull/2163) and [virtualenv #3448](https://github.com/pypa/virtualenv/pull/3448) replace GitHub generated release notes with the tagged changelog section and pin current release action versions. Virtualenv keeps its immutable release assets in the creation call. Both carry `skip news`. PyPA App provisioning for pipx still needs a PyPA owner.
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

## Historical GitHub Release notes

Use the tracked versioned changelog as the source, link the published ecosystem version, and link the comparison with the previous version tag. For the first tag, link its commit history. Preserve release assets, draft/prerelease state, and the Latest designation. Create a missing GitHub Release only when the matching published tag and changelog section are verified. A completed row covers the existing tagged versions; future releases still depend on the open workflow PRs.

- [x] `gaborbernat/bump-deps-index`: 31 release bodies updated; [PR #272](https://github.com/gaborbernat/bump-deps-index/pull/272) adds future comparison links.
- [x] `gaborbernat/pypi-changes`: 16 versions covered, including the missing `1.6.0` GitHub Release; [PR #269](https://github.com/gaborbernat/pypi-changes/pull/269) adds future comparison links.
- [x] `gaborbernat/mdformat-hugo`: four versions covered, including the missing `0.2.0` GitHub Release; [PR #40](https://github.com/gaborbernat/mdformat-hugo/pull/40) adds future comparison links.
- [x] `tox-dev/mdformat-zola`: its `1.0.0` GitHub Release updated; [PR #36](https://github.com/tox-dev/mdformat-zola/pull/36) adds future comparison links.
- [x] `tox-dev/devpi-process`: 11 release bodies updated; [PR #289](https://github.com/tox-dev/devpi-process/pull/289) adds future comparison links.
- [x] `tox-dev/xml-fmt`: five versions covered, including the missing `1.1.0` GitHub Release; [PR #125](https://github.com/tox-dev/xml-fmt/pull/125) adds future comparison links.
- [x] `tox-dev/sphinx-argparse-cli`: 40 versions covered, including the missing `1.22.0` GitHub Release; [PR #374](https://github.com/tox-dev/sphinx-argparse-cli/pull/374) restores three omitted changelog sections and adds future comparison links.
- [x] `tox-dev/pre-commit-uv`: 15 tagged versions covered, including the missing `4.3.0` GitHub Release; [PR #188](https://github.com/tox-dev/pre-commit-uv/pull/188) adds future comparison links. Four older PyPI versions predate this repository's `4.0.0` fork and have no tags in this repository.
- [ ] `tox-dev/sphinx-autodoc-typehints`
- [ ] `tox-dev/peryx`
- [ ] `tox-dev/filelock`
- [ ] `tox-dev/platformdirs`
- [ ] `tox-dev/pipdeptree`
- [ ] `tox-dev/tox`
- [ ] `tox-dev/turbohtml`
- [ ] `pypa/pipx`
- [ ] `pypa/virtualenv`
- [ ] `tox-dev/python-discovery`
- [ ] `tox-dev/tox-ini-fmt`
- [ ] `tox-dev/tox-gh`
- [ ] `tox-dev/pyproject-api`
- [ ] `tox-dev/tox-uv`
- [ ] `tox-dev/action-pre-commit-uv`
- [ ] `tox-dev/jetbrains-fish`
- [ ] `tox-dev/PyVenvManage`
- [ ] `quotaline/quotaline`
- [ ] `tox-dev/toml-fmt`
- [ ] `pytest-dev/pytest-env`
- [ ] `pytest-dev/pytest-print`

## Rollout order

Pilot status on 2026-10-18: [PR #35](https://github.com/gaborbernat/mdformat-hugo/pull/35) was merged; the [main check run](https://github.com/gaborbernat/mdformat-hugo/actions/runs/39142427294) passed. `release-auth` (environment 24639454821) accepts `main` only and holds the App client ID and private key. [gaborbernat-mdformat-hugo-release](https://github.com/settings/installations/172746597) (App 5370155) has Contents write and Metadata read, is installed only on `gaborbernat/mdformat-hugo`, and has no webhook. Its private key is backed up in Insync; a signed App request minted a token scoped to that repository with the expected permissions. The [branch ruleset](https://github.com/gaborbernat/mdformat-hugo/rules/13275985) requires `Required checks pass`, keeps zero reviews, and allows admin and App bypass. The [tag ruleset](https://github.com/gaborbernat/mdformat-hugo/rules/25348004) blocks tag creation, updates, and deletion except by admins and the App. [PR #37](https://github.com/gaborbernat/mdformat-hugo/pull/37) merged the `0.3.1` fragment. The [first prepare run](https://github.com/gaborbernat/mdformat-hugo/actions/runs/39143333836) failed because Dependabot PR #36 moved `main` before the protected push; it created no tag. [PR #38](https://github.com/gaborbernat/mdformat-hugo/pull/38) merged the race fix and Dependabot labels. The [retry](https://github.com/gaborbernat/mdformat-hugo/actions/runs/39144321245) pushed tag `0.3.1`; the [tag workflow](https://github.com/gaborbernat/mdformat-hugo/actions/runs/39144353734) published the wheel and source archive to [PyPI](https://pypi.org/project/mdformat-hugo/0.3.1/). The tag's changelog contains the versioned notes.

Personal repositories take priority while tox-dev CI is backlogged. [PR #266](https://github.com/gaborbernat/pypi-changes/pull/266) merged after its final CI passed with the changelog job active. [gaborbernat-pypi-changes-release](https://github.com/settings/installations/172757421) (App 5370497) has Contents write and Metadata read with webhooks off, and is installed only on `gaborbernat/pypi-changes`; a signed request minted a token limited to that repository. Its private key matches GitHub's fingerprint and is backed up in Insync. `release-auth` (environment 24642262571) accepts `main` only and holds the App client ID and private key. The [branch ruleset](https://github.com/gaborbernat/pypi-changes/rules/1973534) requires `Required checks pass` and pre-commit.ci, keeps zero reviews, and allows admin/App bypass. The [tag ruleset](https://github.com/gaborbernat/pypi-changes/rules/25349542) protects release tags with admin/App bypass. The [merged main run](https://github.com/gaborbernat/pypi-changes/actions/runs/39146011303) passed. `prek` passed before the [prepare run](https://github.com/gaborbernat/pypi-changes/actions/runs/39146089361) pushed the `1.7.1` changelog commit and tag; the [tag workflow](https://github.com/gaborbernat/pypi-changes/actions/runs/39146118208) published the wheel and source archive to [PyPI](https://pypi.org/project/pypi-changes/1.7.1/).

Next: [bump-deps-index PR #269](https://github.com/gaborbernat/bump-deps-index/pull/269) merged after its final fragment and aggregate checks passed. Its [main run](https://github.com/gaborbernat/bump-deps-index/actions/runs/39146384150) passed. [gaborbernat-bump-deps-release](https://github.com/settings/apps/gaborbernat-bump-deps-release) (App 5370573) has Contents write, Metadata read, and webhooks off, and is installed only on `gaborbernat/bump-deps-index`; its private key is backed up in Insync and stored in `release-auth` (environment 24642601887) alongside the App client ID. A signed request minted a token scoped to that repository. The [branch ruleset](https://github.com/gaborbernat/bump-deps-index/rules/1973527) requires the aggregate, pre-commit.ci, and Read the Docs, with zero reviews and admin/App bypass. The [tag ruleset](https://github.com/gaborbernat/bump-deps-index/rules/25349807) protects releases. `prek` passed before [prepare](https://github.com/gaborbernat/bump-deps-index/actions/runs/39148845245) pushed tag `1.17.1`; [publish](https://github.com/gaborbernat/bump-deps-index/actions/runs/39148880418) created the [PyPI distribution](https://pypi.org/project/bump-deps-index/1.17.1/) and [GitHub Release](https://github.com/gaborbernat/bump-deps-index/releases/tag/1.17.1/) from the tagged changelog.

[PR #36](https://github.com/tox-dev/mdformat-zola/pull/36) waits for its updated CI run. [tox-dev-mdformat-zola-release](https://github.com/organizations/tox-dev/settings/installations/172755006) (App 5370430) is owned by tox-dev, has Contents write and Metadata read with webhooks off, and is installed only on `tox-dev/mdformat-zola`. Its private key matches GitHub's fingerprint and is backed up in Insync; a signed request minted a token limited to that repository. `release-auth` (environment 24641758714) accepts `main` only and holds the App client ID and private key. The [branch ruleset](https://github.com/tox-dev/mdformat-zola/rules/25349359) requires `Required checks pass`, zero reviews, and admin/App bypass. The [tag ruleset](https://github.com/tox-dev/mdformat-zola/rules/25349362) protects release tags with admin/App bypass. PR #36 includes a `1.0.1` documentation fragment; Towncrier draft rendered it. After CI passes and Bernát merges it, dispatch `1.0.1` and verify PyPI and GitHub publication.

1. Pilot `gaborbernat/mdformat-hugo` with [PR #35](https://github.com/gaborbernat/mdformat-hugo/pull/35): code, App, key, environment, rulesets, and the published `0.3.1` release are verified.
2. Finish the personal repositories first. The Apps, rulesets, and first releases are verified for `mdformat-hugo`, `pypi-changes`, and `bump-deps-index`. Validate the newly merged GitHub Release automation in `mdformat-hugo` and `pypi-changes` with another release before moving to the next repository.

3. Migrate the six definite PAT users: filelock, platformdirs, pipdeptree, python-discovery, tox, and turbohtml. Audit `GH_RELEASE_TOKEN` in pipx and GitHub-write `RELEASE_TOKEN` in PyVenvManage, jetbrains-fish, and toml-fmt; GitHub does not reveal secret types.
4. Preserve each publisher's special behavior. Backfill changelogs in repositories that lack them.
5. Migrate PyPA and pytest-dev repositories last with their organization admins; we cannot create Apps in those organizations ourselves.

[pypi-changes PR #269](https://github.com/gaborbernat/pypi-changes/pull/269) links GitHub Releases from the README and supplies the documentation fragment for `1.7.2`. Merge after the replacement CI run passes, then dispatch `1.7.2` and verify its PyPI and GitHub releases.

Historical GitHub Releases now use tagged changelog notes, a PyPI link, and a version comparison: all [31 bump-deps-index releases](https://github.com/gaborbernat/bump-deps-index/releases), all [16 pypi-changes releases](https://github.com/gaborbernat/pypi-changes/releases), and all [four mdformat-hugo releases](https://github.com/gaborbernat/mdformat-hugo/releases). The missing pypi-changes `1.6.0` and mdformat-hugo `0.2.0` GitHub Releases were created with `latest=false`; the newest versions remain marked Latest. [bump-deps-index PR #272](https://github.com/gaborbernat/bump-deps-index/pull/272), [pypi-changes PR #269](https://github.com/gaborbernat/pypi-changes/pull/269), and [mdformat-hugo PR #40](https://github.com/gaborbernat/mdformat-hugo/pull/40) add comparison links to future release jobs.
6. Re-audit all 29 repositories against the common contract and update the checkboxes with links to the relevant commits, rulesets, and verification runs.
