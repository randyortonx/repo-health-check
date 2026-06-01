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
