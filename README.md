# repo-health-check

`repo-health-check` is a local-first CLI that audits open-source repository readiness and produces actionable maintainer-focused health reports.

The first release runs entirely on local files. It does not call external APIs, modify your repository, or require credentials.

## Install

```bash
python -m pip install -e ".[dev]"
```

## Usage

```bash
repo-health-check /path/to/repo
repo-health-check --format json /path/to/repo
```

By default, reports are printed as Markdown. JSON output is available for automation and future GitHub Action integration.

## Checks

- README presence and usage-oriented content
- License file
- GitHub Actions CI workflow
- Contributing guide
- Security policy
- Issue and pull request templates
- Changelog or release notes
- Common package metadata

## Exit Codes

- `0`: no failing checks
- `1`: one or more failing checks
- `2`: invalid CLI usage or unreadable repository path

## Roadmap

- GitHub Action wrapper
- Configurable check severity
- Optional AI-assisted remediation suggestions
- Maintainer-focused PR and issue summaries

## Maintainer Support Context

This project is intended to reduce repetitive OSS maintenance work by making repository health gaps visible early. Future optional AI-backed features may help maintainers draft fixes, summarize review work, and triage issues from scan results.
