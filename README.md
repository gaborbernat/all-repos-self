# `all-repos` scripts for Bernat Gabor maintenance

[![check](https://github.com/gaborbernat/all-repos-self/actions/workflows/check.yml/badge.svg)](https://github.com/gaborbernat/all-repos-self/actions/workflows/check.yml)
[![OpenSSF Scorecard](https://api.scorecard.dev/projects/github.com/gaborbernat/all-repos-self/badge)](https://scorecard.dev/viewer/?uri=github.com/gaborbernat/all-repos-self)
[![OpenSSF Best Practices](https://www.bestpractices.dev/projects/16279/badge)](https://www.bestpractices.dev/projects/16279)

```bash
export GITHUB_TOKEN="your API token"
tox r -e dev
.tox/dev/bin/python transformers/bump_deps_tools.py -C all-repos.json -j 10
```
