# repo-health-check Design

Date: 2026-06-01
Status: Approved for planning

## Purpose

`repo-health-check` is a local-first Python CLI for open-source maintainers. It audits whether a repository has the basic signals of a healthy OSS project and produces an actionable report that maintainers can use before publishing, requesting reviews, or applying to maintainer-support programs.

The first version does not call the OpenAI API and does not require credentials. This keeps the tool easy to trust, test, and run in private or public repositories. API-backed features can be added later as optional enhancements for intelligent remediation suggestions, PR review summaries, issue triage, and release checklist generation.

## Scope

The first release will provide:

- A CLI command that scans a local repository path.
- Modular checks for common OSS health signals.
- Markdown and JSON report output.
- A clear pass/warn/fail result model with practical remediation guidance.
- Tests using fixture repositories that represent healthy and incomplete projects.
- Project documentation suitable for a public GitHub repository.

The first release will not provide:

- GitHub API integration.
- Automatic file modification.
- OpenAI API integration.
- Hosted service behavior.
- Claims about stars, downloads, or adoption that do not yet exist.

## CLI

Primary commands:

```bash
repo-health-check /path/to/repo
repo-health-check --format markdown /path/to/repo
repo-health-check --format json /path/to/repo
```

Default output format is Markdown. JSON output is intended for automation and future GitHub Action integration.

The CLI should return:

- Exit code `0` when no failing checks are present.
- Exit code `1` when one or more failing checks are present.
- Exit code `2` for CLI usage errors, unreadable paths, or unsupported output formats.

## Architecture

The project will use a small modular package layout:

- `repo_health_check.cli`: argument parsing, command execution, and process exit behavior.
- `repo_health_check.scanner`: repository path validation and file discovery helpers.
- `repo_health_check.checks`: independent check modules for each OSS health signal.
- `repo_health_check.models`: shared result types such as status, check result, and report.
- `repo_health_check.report`: Markdown and JSON rendering.

Each check should expose a simple function that accepts repository metadata and returns one or more structured results. Checks should not print directly, parse CLI arguments, or perform network calls.

## Initial Checks

The first version will include these checks:

- README: verify that a README exists and contains basic usage-oriented sections such as installation, usage, contributing, or maintenance.
- License: verify that a license file exists.
- CI: detect common CI configuration, starting with GitHub Actions under `.github/workflows`.
- Contributing: detect `CONTRIBUTING.md` or equivalent contributor guidance.
- Security: detect `SECURITY.md` or a security disclosure section.
- Templates: detect issue and pull request templates under `.github`.
- Changelog: detect `CHANGELOG.md`, `RELEASES.md`, or equivalent release notes.
- Package metadata: detect common metadata files such as `pyproject.toml`, `package.json`, or equivalent ecosystem manifests.

Each check result should include:

- Stable check ID.
- Human-readable title.
- Status: `pass`, `warn`, or `fail`.
- Short explanation.
- Suggested fix.

## Report Model

Reports should include:

- Repository path.
- Overall score.
- Summary counts by status.
- Detailed check results grouped by category.
- Next actions ordered by severity.

The score is advisory, not a guarantee of project quality. Failing checks should represent missing core OSS hygiene. Warnings should represent helpful improvements that may not apply to every project.

## Error Handling

The CLI should fail clearly when:

- The target path does not exist.
- The target path is not a directory.
- The process cannot read the target path.
- The requested output format is unsupported.

Individual checks should handle missing files gracefully and return structured results instead of raising exceptions for expected absence.

## Testing

Tests should cover:

- CLI argument handling and exit codes.
- Scanner behavior for missing and valid paths.
- Each individual check.
- Markdown rendering.
- JSON rendering.
- Fixture repositories representing healthy, partial, and minimal repositories.

The first implementation should prefer Python standard library functionality where practical. If a third-party dependency is introduced, it must provide clear value.

## Public Repository Materials

The repository should include:

- `README.md` with project purpose, installation, examples, report output, roadmap, and maintainer-support context.
- `LICENSE`.
- `CONTRIBUTING.md`.
- `SECURITY.md`.
- `.github/ISSUE_TEMPLATE` and `.github/pull_request_template.md`.
- GitHub Actions CI for tests.

## Codex for Open Source Application Positioning

The application should be truthful about project maturity. It should describe the repository as a new OSS project intended to reduce maintenance burden by standardizing repository health checks.

For the eligibility explanation, the project should emphasize ecosystem importance rather than invented usage metrics: many OSS projects lack consistent health signals, and this tool helps maintainers identify gaps before onboarding contributors, reviewing pull requests, or preparing releases.

For API credit usage, the application should describe future optional workflows:

- Generate context-aware remediation suggestions from scan results.
- Summarize maintainer action items for PRs and issues.
- Draft release checklists from repository state.
- Assist with issue triage and documentation improvements.

The application must not claim stars, downloads, users, or adoption that the project does not have.

