# repo-health-check Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a public-ready Python CLI that scans local open-source repositories for common health signals and outputs Markdown or JSON reports.

**Architecture:** Use a small `src/` package with explicit boundaries: dataclass models, repository scanning helpers, independent check modules, report renderers, and a thin CLI. Checks return structured results and never print, parse CLI arguments, perform network calls, or mutate the target repository.

**Tech Stack:** Python 3.11+, standard library runtime, `pytest` for tests, `pyproject.toml` packaging with a `repo-health-check` console script.

---

## File Structure

- Create `pyproject.toml`: project metadata, package discovery, pytest config, and console script.
- Create `src/repo_health_check/__init__.py`: package version export.
- Create `src/repo_health_check/models.py`: `Status`, `CheckResult`, `Report`, and score/count helpers.
- Create `src/repo_health_check/scanner.py`: path validation and repository file discovery.
- Create `src/repo_health_check/checks/__init__.py`: ordered registry of all checks.
- Create `src/repo_health_check/checks/readme.py`: README presence and content checks.
- Create `src/repo_health_check/checks/license.py`: license file detection.
- Create `src/repo_health_check/checks/ci.py`: GitHub Actions workflow detection.
- Create `src/repo_health_check/checks/contributing.py`: contributor guide detection.
- Create `src/repo_health_check/checks/security.py`: security policy detection.
- Create `src/repo_health_check/checks/templates.py`: issue and pull request template detection.
- Create `src/repo_health_check/checks/changelog.py`: changelog or release notes detection.
- Create `src/repo_health_check/checks/metadata.py`: ecosystem package metadata detection.
- Create `src/repo_health_check/report.py`: Markdown and JSON rendering.
- Create `src/repo_health_check/cli.py`: CLI argument parsing, scan orchestration, output, and exit codes.
- Create `tests/conftest.py`: fixture repository builders.
- Create `tests/test_models.py`: model behavior.
- Create `tests/test_scanner.py`: scanner behavior.
- Create `tests/test_checks.py`: all check modules.
- Create `tests/test_report.py`: Markdown and JSON rendering.
- Create `tests/test_cli.py`: CLI behavior and exit codes.
- Create `README.md`: public project documentation and examples.
- Create `LICENSE`: MIT license.
- Create `CONTRIBUTING.md`: local development and contribution workflow.
- Create `SECURITY.md`: vulnerability reporting guidance.
- Create `.github/workflows/tests.yml`: CI test workflow.
- Create `.github/ISSUE_TEMPLATE/bug_report.md`: issue template.
- Create `.github/ISSUE_TEMPLATE/feature_request.md`: feature template.
- Create `.github/pull_request_template.md`: PR checklist.
- Create `docs/codex-for-oss-application.md`: truthful application draft for Codex for Open Source.

## Task 1: Package Scaffold

**Files:**
- Create: `pyproject.toml`
- Create: `src/repo_health_check/__init__.py`

- [ ] **Step 1: Create package metadata**

Create `pyproject.toml`:

```toml
[build-system]
requires = ["setuptools>=69"]
build-backend = "setuptools.build_meta"

[project]
name = "repo-health-check"
version = "0.1.0"
description = "Local-first OSS repository health checks for maintainers."
readme = "README.md"
requires-python = ">=3.11"
license = { text = "MIT" }
authors = [{ name = "repo-health-check maintainers" }]
keywords = ["open-source", "maintenance", "repository", "health-check", "cli"]
classifiers = [
  "Development Status :: 3 - Alpha",
  "Environment :: Console",
  "Intended Audience :: Developers",
  "License :: OSI Approved :: MIT License",
  "Programming Language :: Python :: 3",
  "Programming Language :: Python :: 3.11",
  "Programming Language :: Python :: 3.12",
  "Topic :: Software Development :: Quality Assurance",
]

[project.optional-dependencies]
dev = ["pytest>=8"]

[project.scripts]
repo-health-check = "repo_health_check.cli:main"

[tool.setuptools.packages.find]
where = ["src"]

[tool.pytest.ini_options]
pythonpath = ["src"]
testpaths = ["tests"]
```

Create `src/repo_health_check/__init__.py`:

```python
"""Local-first OSS repository health checks."""

__version__ = "0.1.0"
```

- [ ] **Step 2: Verify package imports**

Run: `python -m pytest --version`

Expected: pytest prints its version. If pytest is missing, install local dev dependencies with `python -m pip install -e ".[dev]"`.

- [ ] **Step 3: Commit**

```bash
git add pyproject.toml src/repo_health_check/__init__.py
git commit -m "chore: scaffold python package"
```

## Task 2: Core Result Models

**Files:**
- Create: `tests/test_models.py`
- Create: `src/repo_health_check/models.py`

- [ ] **Step 1: Write failing model tests**

Create `tests/test_models.py`:

```python
from repo_health_check.models import CheckResult, Report, Status


def test_report_counts_results_by_status():
    report = Report(
        repo_path="/tmp/example",
        results=[
            CheckResult("readme", "README", Status.PASS, "Found", "No action needed."),
            CheckResult("license", "License", Status.FAIL, "Missing", "Add a LICENSE file."),
            CheckResult("security", "Security", Status.WARN, "Missing", "Add SECURITY.md."),
        ],
    )

    assert report.counts == {"pass": 1, "warn": 1, "fail": 1}


def test_report_score_treats_pass_as_full_and_warn_as_half_credit():
    report = Report(
        repo_path="/tmp/example",
        results=[
            CheckResult("readme", "README", Status.PASS, "Found", "No action needed."),
            CheckResult("license", "License", Status.WARN, "Partial", "Clarify license."),
            CheckResult("security", "Security", Status.FAIL, "Missing", "Add SECURITY.md."),
        ],
    )

    assert report.score == 50


def test_report_next_actions_prioritizes_failures_before_warnings():
    report = Report(
        repo_path="/tmp/example",
        results=[
            CheckResult("security", "Security", Status.WARN, "Missing", "Add SECURITY.md."),
            CheckResult("license", "License", Status.FAIL, "Missing", "Add a LICENSE file."),
            CheckResult("readme", "README", Status.PASS, "Found", "No action needed."),
        ],
    )

    assert [result.check_id for result in report.next_actions] == ["license", "security"]
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_models.py -v`

Expected: FAIL because `repo_health_check.models` does not exist.

- [ ] **Step 3: Implement minimal models**

Create `src/repo_health_check/models.py`:

```python
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class Status(StrEnum):
    PASS = "pass"
    WARN = "warn"
    FAIL = "fail"


@dataclass(frozen=True)
class CheckResult:
    check_id: str
    title: str
    status: Status
    summary: str
    suggestion: str


@dataclass(frozen=True)
class Report:
    repo_path: str
    results: list[CheckResult]

    @property
    def counts(self) -> dict[str, int]:
        return {
            Status.PASS.value: sum(1 for result in self.results if result.status == Status.PASS),
            Status.WARN.value: sum(1 for result in self.results if result.status == Status.WARN),
            Status.FAIL.value: sum(1 for result in self.results if result.status == Status.FAIL),
        }

    @property
    def score(self) -> int:
        if not self.results:
            return 0
        earned = 0.0
        for result in self.results:
            if result.status == Status.PASS:
                earned += 1.0
            elif result.status == Status.WARN:
                earned += 0.5
        return round((earned / len(self.results)) * 100)

    @property
    def next_actions(self) -> list[CheckResult]:
        failures = [result for result in self.results if result.status == Status.FAIL]
        warnings = [result for result in self.results if result.status == Status.WARN]
        return failures + warnings
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_models.py -v`

Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
git add tests/test_models.py src/repo_health_check/models.py
git commit -m "feat: add report result models"
```

## Task 3: Repository Scanner

**Files:**
- Create: `tests/conftest.py`
- Create: `tests/test_scanner.py`
- Create: `src/repo_health_check/scanner.py`

- [ ] **Step 1: Write failing scanner tests**

Create `tests/conftest.py`:

```python
from pathlib import Path

import pytest


@pytest.fixture
def repo_factory(tmp_path: Path):
    def create_repo(files: dict[str, str]) -> Path:
        repo = tmp_path / "repo"
        repo.mkdir()
        for relative_path, content in files.items():
            target = repo / relative_path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
        return repo

    return create_repo
```

Create `tests/test_scanner.py`:

```python
from pathlib import Path

import pytest

from repo_health_check.scanner import RepositorySnapshot, scan_repository


def test_scan_repository_records_relative_file_paths(repo_factory):
    repo = repo_factory({
        "README.md": "# Example\n",
        ".github/workflows/tests.yml": "name: tests\n",
    })

    snapshot = scan_repository(repo)

    assert isinstance(snapshot, RepositorySnapshot)
    assert snapshot.root == repo
    assert snapshot.has_file("README.md")
    assert snapshot.has_file(".github/workflows/tests.yml")
    assert snapshot.read_text("README.md") == "# Example\n"


def test_scan_repository_rejects_missing_path(tmp_path: Path):
    with pytest.raises(FileNotFoundError, match="Repository path does not exist"):
        scan_repository(tmp_path / "missing")


def test_scan_repository_rejects_file_path(tmp_path: Path):
    target = tmp_path / "README.md"
    target.write_text("# Not a directory\n", encoding="utf-8")

    with pytest.raises(NotADirectoryError, match="Repository path is not a directory"):
        scan_repository(target)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_scanner.py -v`

Expected: FAIL because `repo_health_check.scanner` does not exist.

- [ ] **Step 3: Implement scanner**

Create `src/repo_health_check/scanner.py`:

```python
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


IGNORED_DIRS = {".git", ".hg", ".svn", "__pycache__", ".mypy_cache", ".pytest_cache", "node_modules"}


@dataclass(frozen=True)
class RepositorySnapshot:
    root: Path
    files: frozenset[str]

    def has_file(self, relative_path: str) -> bool:
        return relative_path.replace("\\", "/") in self.files

    def matching_files(self, *names: str) -> list[str]:
        wanted = {name.lower() for name in names}
        return sorted(path for path in self.files if Path(path).name.lower() in wanted)

    def files_under(self, prefix: str) -> list[str]:
        normalized = prefix.strip("/").replace("\\", "/")
        return sorted(path for path in self.files if path.startswith(f"{normalized}/"))

    def read_text(self, relative_path: str) -> str:
        return (self.root / relative_path).read_text(encoding="utf-8")


def scan_repository(path: str | Path) -> RepositorySnapshot:
    root = Path(path).expanduser().resolve()
    if not root.exists():
        raise FileNotFoundError(f"Repository path does not exist: {root}")
    if not root.is_dir():
        raise NotADirectoryError(f"Repository path is not a directory: {root}")

    files: set[str] = set()
    for item in root.rglob("*"):
        if any(part in IGNORED_DIRS for part in item.relative_to(root).parts):
            continue
        if item.is_file():
            files.add(item.relative_to(root).as_posix())
    return RepositorySnapshot(root=root, files=frozenset(files))
```

- [ ] **Step 4: Run scanner and model tests**

Run: `python -m pytest tests/test_scanner.py tests/test_models.py -v`

Expected: 6 passed.

- [ ] **Step 5: Commit**

```bash
git add tests/conftest.py tests/test_scanner.py src/repo_health_check/scanner.py
git commit -m "feat: add repository scanner"
```

## Task 4: Health Checks

**Files:**
- Create: `tests/test_checks.py`
- Create: `src/repo_health_check/checks/__init__.py`
- Create: `src/repo_health_check/checks/readme.py`
- Create: `src/repo_health_check/checks/license.py`
- Create: `src/repo_health_check/checks/ci.py`
- Create: `src/repo_health_check/checks/contributing.py`
- Create: `src/repo_health_check/checks/security.py`
- Create: `src/repo_health_check/checks/templates.py`
- Create: `src/repo_health_check/checks/changelog.py`
- Create: `src/repo_health_check/checks/metadata.py`

- [ ] **Step 1: Write failing check tests**

Create `tests/test_checks.py`:

```python
from repo_health_check.checks import run_checks
from repo_health_check.models import Status
from repo_health_check.scanner import scan_repository


def status_by_id(repo):
    results = run_checks(scan_repository(repo))
    return {result.check_id: result.status for result in results}


def test_healthy_repository_passes_core_checks(repo_factory):
    repo = repo_factory({
        "README.md": "# Example\n\n## Installation\n\n## Usage\n\n## Contributing\n",
        "LICENSE": "MIT License\n",
        ".github/workflows/tests.yml": "name: tests\n",
        "CONTRIBUTING.md": "# Contributing\n",
        "SECURITY.md": "# Security\n",
        ".github/ISSUE_TEMPLATE/bug_report.md": "---\nname: Bug report\n---\n",
        ".github/pull_request_template.md": "## Checklist\n",
        "CHANGELOG.md": "# Changelog\n",
        "pyproject.toml": "[project]\nname = 'example'\n",
    })

    statuses = status_by_id(repo)

    assert statuses == {
        "readme": Status.PASS,
        "license": Status.PASS,
        "ci": Status.PASS,
        "contributing": Status.PASS,
        "security": Status.PASS,
        "templates": Status.PASS,
        "changelog": Status.PASS,
        "metadata": Status.PASS,
    }


def test_minimal_repository_fails_required_checks_and_warns_for_templates(repo_factory):
    repo = repo_factory({"README.md": "# Example\n"})

    statuses = status_by_id(repo)

    assert statuses["readme"] == Status.WARN
    assert statuses["license"] == Status.FAIL
    assert statuses["ci"] == Status.FAIL
    assert statuses["contributing"] == Status.WARN
    assert statuses["security"] == Status.WARN
    assert statuses["templates"] == Status.WARN
    assert statuses["changelog"] == Status.WARN
    assert statuses["metadata"] == Status.WARN


def test_missing_readme_fails_readme_check(repo_factory):
    repo = repo_factory({"LICENSE": "MIT License\n"})

    statuses = status_by_id(repo)

    assert statuses["readme"] == Status.FAIL
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_checks.py -v`

Expected: FAIL because `repo_health_check.checks` does not exist.

- [ ] **Step 3: Implement check registry**

Create `src/repo_health_check/checks/__init__.py`:

```python
from __future__ import annotations

from collections.abc import Callable

from repo_health_check.checks.changelog import check_changelog
from repo_health_check.checks.ci import check_ci
from repo_health_check.checks.contributing import check_contributing
from repo_health_check.checks.license import check_license
from repo_health_check.checks.metadata import check_metadata
from repo_health_check.checks.readme import check_readme
from repo_health_check.checks.security import check_security
from repo_health_check.checks.templates import check_templates
from repo_health_check.models import CheckResult
from repo_health_check.scanner import RepositorySnapshot

Check = Callable[[RepositorySnapshot], CheckResult]

CHECKS: tuple[Check, ...] = (
    check_readme,
    check_license,
    check_ci,
    check_contributing,
    check_security,
    check_templates,
    check_changelog,
    check_metadata,
)


def run_checks(snapshot: RepositorySnapshot) -> list[CheckResult]:
    return [check(snapshot) for check in CHECKS]
```

- [ ] **Step 4: Implement individual checks**

Create `src/repo_health_check/checks/readme.py`:

```python
from __future__ import annotations

from repo_health_check.models import CheckResult, Status
from repo_health_check.scanner import RepositorySnapshot

README_NAMES = ("README.md", "README.rst", "README.txt", "README")
HELPFUL_TERMS = ("install", "installation", "usage", "quickstart", "contributing", "maintain")


def check_readme(snapshot: RepositorySnapshot) -> CheckResult:
    matches = snapshot.matching_files(*README_NAMES)
    if not matches:
        return CheckResult("readme", "README", Status.FAIL, "No README file was found.", "Add a README with installation, usage, and contribution guidance.")
    content = snapshot.read_text(matches[0]).lower()
    if any(term in content for term in HELPFUL_TERMS):
        return CheckResult("readme", "README", Status.PASS, f"Found {matches[0]} with usage-oriented content.", "No action needed.")
    return CheckResult("readme", "README", Status.WARN, f"Found {matches[0]}, but it has limited usage guidance.", "Add installation, usage, or contribution sections.")
```

Create `src/repo_health_check/checks/license.py`:

```python
from __future__ import annotations

from repo_health_check.models import CheckResult, Status
from repo_health_check.scanner import RepositorySnapshot

LICENSE_NAMES = ("LICENSE", "LICENSE.md", "LICENSE.txt", "COPYING")


def check_license(snapshot: RepositorySnapshot) -> CheckResult:
    matches = snapshot.matching_files(*LICENSE_NAMES)
    if matches:
        return CheckResult("license", "License", Status.PASS, f"Found {matches[0]}.", "No action needed.")
    return CheckResult("license", "License", Status.FAIL, "No license file was found.", "Add an OSI-approved license file such as MIT, Apache-2.0, or BSD-3-Clause.")
```

Create `src/repo_health_check/checks/ci.py`:

```python
from __future__ import annotations

from repo_health_check.models import CheckResult, Status
from repo_health_check.scanner import RepositorySnapshot


def check_ci(snapshot: RepositorySnapshot) -> CheckResult:
    workflow_files = [path for path in snapshot.files_under(".github/workflows") if path.endswith((".yml", ".yaml"))]
    if workflow_files:
        return CheckResult("ci", "Continuous integration", Status.PASS, f"Found {len(workflow_files)} GitHub Actions workflow file(s).", "No action needed.")
    return CheckResult("ci", "Continuous integration", Status.FAIL, "No GitHub Actions workflow was found.", "Add a workflow under .github/workflows to run tests on pull requests.")
```

Create `src/repo_health_check/checks/contributing.py`:

```python
from __future__ import annotations

from repo_health_check.models import CheckResult, Status
from repo_health_check.scanner import RepositorySnapshot

CONTRIBUTING_NAMES = ("CONTRIBUTING.md", "CONTRIBUTING.rst", "CONTRIBUTING.txt")


def check_contributing(snapshot: RepositorySnapshot) -> CheckResult:
    matches = snapshot.matching_files(*CONTRIBUTING_NAMES)
    if matches:
        return CheckResult("contributing", "Contributing guide", Status.PASS, f"Found {matches[0]}.", "No action needed.")
    return CheckResult("contributing", "Contributing guide", Status.WARN, "No contributing guide was found.", "Add CONTRIBUTING.md with setup, testing, and pull request expectations.")
```

Create `src/repo_health_check/checks/security.py`:

```python
from __future__ import annotations

from repo_health_check.models import CheckResult, Status
from repo_health_check.scanner import RepositorySnapshot

SECURITY_NAMES = ("SECURITY.md", "SECURITY.rst", "SECURITY.txt")


def check_security(snapshot: RepositorySnapshot) -> CheckResult:
    matches = snapshot.matching_files(*SECURITY_NAMES)
    if matches:
        return CheckResult("security", "Security policy", Status.PASS, f"Found {matches[0]}.", "No action needed.")
    return CheckResult("security", "Security policy", Status.WARN, "No security policy was found.", "Add SECURITY.md with vulnerability reporting guidance.")
```

Create `src/repo_health_check/checks/templates.py`:

```python
from __future__ import annotations

from repo_health_check.models import CheckResult, Status
from repo_health_check.scanner import RepositorySnapshot


def check_templates(snapshot: RepositorySnapshot) -> CheckResult:
    issue_templates = snapshot.files_under(".github/ISSUE_TEMPLATE")
    pr_templates = [path for path in (".github/pull_request_template.md", ".github/PULL_REQUEST_TEMPLATE.md") if snapshot.has_file(path)]
    if issue_templates and pr_templates:
        return CheckResult("templates", "Issue and PR templates", Status.PASS, "Found issue and pull request templates.", "No action needed.")
    return CheckResult("templates", "Issue and PR templates", Status.WARN, "Issue or pull request templates are missing.", "Add issue templates and .github/pull_request_template.md.")
```

Create `src/repo_health_check/checks/changelog.py`:

```python
from __future__ import annotations

from repo_health_check.models import CheckResult, Status
from repo_health_check.scanner import RepositorySnapshot

CHANGELOG_NAMES = ("CHANGELOG.md", "CHANGELOG.rst", "HISTORY.md", "RELEASES.md")


def check_changelog(snapshot: RepositorySnapshot) -> CheckResult:
    matches = snapshot.matching_files(*CHANGELOG_NAMES)
    if matches:
        return CheckResult("changelog", "Changelog", Status.PASS, f"Found {matches[0]}.", "No action needed.")
    return CheckResult("changelog", "Changelog", Status.WARN, "No changelog or release notes file was found.", "Add CHANGELOG.md to document user-visible changes.")
```

Create `src/repo_health_check/checks/metadata.py`:

```python
from __future__ import annotations

from repo_health_check.models import CheckResult, Status
from repo_health_check.scanner import RepositorySnapshot

METADATA_NAMES = ("pyproject.toml", "package.json", "Cargo.toml", "go.mod", "pom.xml", "build.gradle")


def check_metadata(snapshot: RepositorySnapshot) -> CheckResult:
    matches = snapshot.matching_files(*METADATA_NAMES)
    if matches:
        return CheckResult("metadata", "Package metadata", Status.PASS, f"Found {matches[0]}.", "No action needed.")
    return CheckResult("metadata", "Package metadata", Status.WARN, "No common package metadata file was found.", "Add ecosystem metadata such as pyproject.toml, package.json, Cargo.toml, or go.mod when applicable.")
```

- [ ] **Step 5: Run check tests**

Run: `python -m pytest tests/test_checks.py -v`

Expected: 3 passed.

- [ ] **Step 6: Run all existing tests**

Run: `python -m pytest tests/test_models.py tests/test_scanner.py tests/test_checks.py -v`

Expected: 9 passed.

- [ ] **Step 7: Commit**

```bash
git add tests/test_checks.py src/repo_health_check/checks
git commit -m "feat: add repository health checks"
```

## Task 5: Report Rendering

**Files:**
- Create: `tests/test_report.py`
- Create: `src/repo_health_check/report.py`

- [ ] **Step 1: Write failing report tests**

Create `tests/test_report.py`:

```python
import json

from repo_health_check.models import CheckResult, Report, Status
from repo_health_check.report import render_json, render_markdown


def sample_report():
    return Report(
        repo_path="/tmp/example",
        results=[
            CheckResult("readme", "README", Status.PASS, "Found README.md.", "No action needed."),
            CheckResult("license", "License", Status.FAIL, "No license file was found.", "Add a LICENSE file."),
            CheckResult("security", "Security policy", Status.WARN, "No security policy was found.", "Add SECURITY.md."),
        ],
    )


def test_render_markdown_includes_summary_and_next_actions():
    output = render_markdown(sample_report())

    assert "# Repository Health Report" in output
    assert "Score: 50/100" in output
    assert "- Pass: 1" in output
    assert "- Warn: 1" in output
    assert "- Fail: 1" in output
    assert "## Next Actions" in output
    assert "Add a LICENSE file." in output


def test_render_json_outputs_machine_readable_report():
    data = json.loads(render_json(sample_report()))

    assert data["repo_path"] == "/tmp/example"
    assert data["score"] == 50
    assert data["counts"] == {"pass": 1, "warn": 1, "fail": 1}
    assert data["results"][1]["check_id"] == "license"
    assert data["results"][1]["status"] == "fail"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_report.py -v`

Expected: FAIL because `repo_health_check.report` does not exist.

- [ ] **Step 3: Implement renderers**

Create `src/repo_health_check/report.py`:

```python
from __future__ import annotations

import json

from repo_health_check.models import CheckResult, Report


STATUS_LABELS = {
    "pass": "PASS",
    "warn": "WARN",
    "fail": "FAIL",
}


def render_markdown(report: Report) -> str:
    lines = [
        "# Repository Health Report",
        "",
        f"Repository: `{report.repo_path}`",
        f"Score: {report.score}/100",
        "",
        "## Summary",
        "",
        f"- Pass: {report.counts['pass']}",
        f"- Warn: {report.counts['warn']}",
        f"- Fail: {report.counts['fail']}",
        "",
        "## Results",
        "",
    ]
    for result in report.results:
        lines.extend(_render_result(result))

    lines.extend(["## Next Actions", ""])
    if not report.next_actions:
        lines.append("No required actions.")
    else:
        for result in report.next_actions:
            lines.append(f"- **{result.title}**: {result.suggestion}")
    lines.append("")
    return "\n".join(lines)


def _render_result(result: CheckResult) -> list[str]:
    label = STATUS_LABELS[result.status.value]
    return [
        f"### {label}: {result.title}",
        "",
        result.summary,
        "",
        f"Suggested fix: {result.suggestion}",
        "",
    ]


def render_json(report: Report) -> str:
    payload = {
        "repo_path": report.repo_path,
        "score": report.score,
        "counts": report.counts,
        "results": [
            {
                "check_id": result.check_id,
                "title": result.title,
                "status": result.status.value,
                "summary": result.summary,
                "suggestion": result.suggestion,
            }
            for result in report.results
        ],
        "next_actions": [result.check_id for result in report.next_actions],
    }
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"
```

- [ ] **Step 4: Run report tests**

Run: `python -m pytest tests/test_report.py -v`

Expected: 2 passed.

- [ ] **Step 5: Run all tests**

Run: `python -m pytest -v`

Expected: 11 passed.

- [ ] **Step 6: Commit**

```bash
git add tests/test_report.py src/repo_health_check/report.py
git commit -m "feat: add report renderers"
```

## Task 6: CLI

**Files:**
- Create: `tests/test_cli.py`
- Create: `src/repo_health_check/cli.py`

- [ ] **Step 1: Write failing CLI tests**

Create `tests/test_cli.py`:

```python
import json

from repo_health_check.cli import main


def test_cli_outputs_markdown_and_returns_one_when_failures_exist(repo_factory, capsys):
    repo = repo_factory({"README.md": "# Example\n"})

    exit_code = main([str(repo)])
    output = capsys.readouterr().out

    assert exit_code == 1
    assert "# Repository Health Report" in output
    assert "No license file was found." in output


def test_cli_outputs_json_when_requested(repo_factory, capsys):
    repo = repo_factory({
        "README.md": "# Example\n\n## Usage\n",
        "LICENSE": "MIT License\n",
        ".github/workflows/tests.yml": "name: tests\n",
    })

    exit_code = main(["--format", "json", str(repo)])
    output = capsys.readouterr().out
    data = json.loads(output)

    assert exit_code == 0
    assert data["repo_path"] == str(repo.resolve())
    assert "results" in data


def test_cli_returns_two_for_missing_path(tmp_path, capsys):
    exit_code = main([str(tmp_path / "missing")])
    captured = capsys.readouterr()

    assert exit_code == 2
    assert "Repository path does not exist" in captured.err
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_cli.py -v`

Expected: FAIL because `repo_health_check.cli` does not exist.

- [ ] **Step 3: Implement CLI**

Create `src/repo_health_check/cli.py`:

```python
from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence

from repo_health_check.checks import run_checks
from repo_health_check.models import Report, Status
from repo_health_check.report import render_json, render_markdown
from repo_health_check.scanner import scan_repository


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Audit OSS repository health signals.")
    parser.add_argument("path", help="Path to the repository to scan.")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown", help="Report output format.")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        snapshot = scan_repository(args.path)
    except (FileNotFoundError, NotADirectoryError, PermissionError) as exc:
        print(str(exc), file=sys.stderr)
        return 2

    report = Report(repo_path=str(snapshot.root), results=run_checks(snapshot))
    if args.format == "json":
        print(render_json(report), end="")
    else:
        print(render_markdown(report), end="")

    return 1 if any(result.status == Status.FAIL for result in report.results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run CLI tests**

Run: `python -m pytest tests/test_cli.py -v`

Expected: 3 passed.

- [ ] **Step 5: Run all tests**

Run: `python -m pytest -v`

Expected: 14 passed.

- [ ] **Step 6: Commit**

```bash
git add tests/test_cli.py src/repo_health_check/cli.py
git commit -m "feat: add command line interface"
```

## Task 7: Public Repository Materials

**Files:**
- Create: `README.md`
- Create: `LICENSE`
- Create: `CONTRIBUTING.md`
- Create: `SECURITY.md`
- Create: `.github/workflows/tests.yml`
- Create: `.github/ISSUE_TEMPLATE/bug_report.md`
- Create: `.github/ISSUE_TEMPLATE/feature_request.md`
- Create: `.github/pull_request_template.md`

- [ ] **Step 1: Create public docs and GitHub metadata**

Create `README.md`:

````markdown
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
````

Create `LICENSE`:

```text
MIT License

Copyright (c) 2026 repo-health-check contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

Create `CONTRIBUTING.md`:

````markdown
# Contributing

Thanks for helping improve `repo-health-check`.

## Development Setup

```bash
python -m pip install -e ".[dev]"
python -m pytest -v
```

## Pull Requests

- Keep checks small and deterministic.
- Add or update tests before changing behavior.
- Avoid network calls in core checks.
- Update README examples when CLI behavior changes.
````

Create `SECURITY.md`:

```markdown
# Security Policy

`repo-health-check` reads local repository files and should not send repository content to external services.

Please report security issues privately to the maintainers. Do not include secrets, private tokens, or confidential repository contents in public issues.
```

Create `.github/workflows/tests.yml`:

```yaml
name: tests

on:
  pull_request:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.11", "3.12"]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - run: python -m pip install -e ".[dev]"
      - run: python -m pytest -v
```

Create `.github/ISSUE_TEMPLATE/bug_report.md`:

```markdown
---
name: Bug report
about: Report incorrect scan behavior or CLI failures
title: ""
labels: bug
assignees: ""
---

## What happened?

## Expected behavior

## Repository shape

## Command output
```

Create `.github/ISSUE_TEMPLATE/feature_request.md`:

```markdown
---
name: Feature request
about: Suggest a check, renderer, or maintainer workflow
title: ""
labels: enhancement
assignees: ""
---

## Use case

## Proposed behavior

## Alternatives considered
```

Create `.github/pull_request_template.md`:

```markdown
## Summary

## Testing

- [ ] `python -m pytest -v`

## Checklist

- [ ] Tests cover the behavior change
- [ ] Documentation is updated when user-facing behavior changes
```

- [ ] **Step 2: Run the tool against its own repository**

Run: `python -m pytest -v && python -m repo_health_check.cli .`

Expected: tests pass and the repository health report shows no failing checks.

- [ ] **Step 3: Commit**

```bash
git add README.md LICENSE CONTRIBUTING.md SECURITY.md .github
git commit -m "docs: add public repository materials"
```

## Task 8: Codex for OSS Application Draft

**Files:**
- Create: `docs/codex-for-oss-application.md`

- [ ] **Step 1: Create truthful application draft**

Create `docs/codex-for-oss-application.md`:

```markdown
# Codex for Open Source Application Draft

## Project

repo-health-check

## Repository

Public GitHub repository URL: Not yet available while the repository is local. Replace this line with the public GitHub URL after publishing.

## Short Description

`repo-health-check` is a local-first Python CLI that audits open-source repository readiness and produces actionable maintainer-focused reports. It checks common OSS health signals such as README quality, license presence, CI, contribution guidance, security policy, issue and PR templates, changelog, and package metadata.

## Why This Matters

Many open-source repositories miss basic maintenance signals that help contributors understand how to install, test, report issues, disclose vulnerabilities, and submit changes. `repo-health-check` gives maintainers a repeatable way to find these gaps before onboarding contributors, reviewing pull requests, preparing releases, or applying to maintainer-support programs.

This is a new project. It should not be represented as having stars, downloads, or adoption until those metrics exist. Its current importance is the maintenance problem it targets: reducing repetitive repository hygiene work for OSS maintainers.

## How Codex Credits Would Be Used

The first release is local-only and does not require an API key. Codex credits would support optional future maintainer workflows:

- Generate context-aware remediation suggestions from scan results.
- Summarize maintainer action items for pull requests and issues.
- Draft release checklists from repository state.
- Assist with issue triage and documentation improvements.

## Current State

- Local Python CLI planned and implemented in this repository.
- Markdown and JSON report output.
- Deterministic checks with tests and CI.
- Public repository materials included: README, license, contribution guide, security policy, issue templates, PR template, and test workflow.

## Accuracy Notes

Do not claim usage metrics that do not exist. Add stars, downloads, package links, or notable users only after they are real and verifiable.
```

- [ ] **Step 2: Verify no fake metrics appear**

Run: `rg -n "star|download|user|adoption|popular|widely used" docs/codex-for-oss-application.md README.md`

Expected: matches only in cautionary or future-context language, not claims of current adoption.

- [ ] **Step 3: Commit**

```bash
git add docs/codex-for-oss-application.md
git commit -m "docs: add codex for oss application draft"
```

## Task 9: Final Verification

**Files:**
- Verify all source, tests, docs, and git state.

- [ ] **Step 1: Run full test suite**

Run: `python -m pytest -v`

Expected: all tests pass.

- [ ] **Step 2: Run installed CLI in Markdown mode**

Run: `python -m repo_health_check.cli .`

Expected: Markdown report prints and exits with code `0`.

- [ ] **Step 3: Run installed CLI in JSON mode**

Run: `python -m repo_health_check.cli --format json .`

Expected: valid JSON report prints and exits with code `0`.

- [ ] **Step 4: Inspect git status**

Run: `git status --short`

Expected: no output.

- [ ] **Step 5: Report completion evidence**

Report exact verification commands and outcomes to the user, including any deviations.
