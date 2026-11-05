# Contributing

Open a pull request against `main`. Run `tox run -e fix` before pushing; it applies the formatters and linters the CI
checks. Never try a change by running a script against the real fleet: use the tests, or `--dry-run` once the tests
pass.

## Tests

Add a test for every new script, feature and bug fix: a fix needs a test that fails without it. A change without a test
needs a reason in the pull request description. Run the suite with `tox run -e test`, which fails below 100% coverage of
the scripts and the tests. Pass pytest arguments after `--` to run a subset, for example
`tox run -e test -- tests/transformers -k prettier`; that run skips the coverage check.

The tests never reach GitHub or PyPI. A transformer test builds a small fleet of local bare repositories, runs the
transformer through [all-repos](https://github.com/asottile/all-repos) against it, and checks what landed on each
default branch. The tools that need the network, `pre-commit` and `bump-deps-index`, are replaced by a stand-in that
logs each call into the repository, so the log shows which repositories ran which commands. Tests of the GitHub commands
mock the API client.

For example, a test for a transformer that should only touch repositories using `prettier` seeds one repository with a
`prettier` hook and one without, then asserts that only the first one's default branch changed.
