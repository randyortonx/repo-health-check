from repo_health_check.checks import run_checks
from repo_health_check.checks.readme import check_readme
from repo_health_check.models import Status
from repo_health_check.scanner import RepositorySnapshot, scan_repository


def status_by_id(repo):
    results = run_checks(scan_repository(repo))
    return {result.check_id: result.status for result in results}


def result_by_id(repo):
    results = run_checks(scan_repository(repo))
    return {result.check_id: result for result in results}


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


def test_invalid_utf8_readme_returns_warning(repo_factory):
    repo = repo_factory({"LICENSE": "MIT License\n"})
    (repo / "README.md").write_bytes(b"\xff\xfe\x00")

    results = result_by_id(repo)

    assert results["readme"].status == Status.WARN
    assert "decode" in results["readme"].summary.lower() or "unreadable" in results["readme"].summary.lower()


def test_readme_read_os_error_returns_warning(repo_factory, monkeypatch):
    repo = repo_factory({"README.md": "# Example\n"})
    snapshot = scan_repository(repo)

    def raise_os_error(self, relative_path):
        raise OSError("read failed")

    monkeypatch.setattr(RepositorySnapshot, "read_text", raise_os_error)

    result = check_readme(snapshot)

    assert result.status == Status.WARN
    assert "read" in result.summary.lower()
    assert "safely" in result.summary.lower()


def test_readme_symlink_to_ignored_internal_file_does_not_raise(repo_factory):
    repo = repo_factory({
        ".git/config": "[core]\n",
    })
    (repo / "README.md").symlink_to(".git/config")

    results = result_by_id(repo)

    assert results["readme"].status in {Status.FAIL, Status.WARN}


def test_nested_files_do_not_satisfy_root_level_checks(repo_factory):
    repo = repo_factory({
        "docs/LICENSE": "MIT License\n",
        "examples/README.md": "# Example\n\n## Usage\n",
        "docs/CONTRIBUTING.md": "# Contributing\n",
        "docs/SECURITY.md": "# Security\n",
        "docs/CHANGELOG.md": "# Changelog\n",
        "packages/pkg/pyproject.toml": "[project]\nname = 'example'\n",
    })

    statuses = status_by_id(repo)

    assert statuses["readme"] == Status.FAIL
    assert statuses["license"] == Status.FAIL
    assert statuses["contributing"] == Status.WARN
    assert statuses["security"] == Status.WARN
    assert statuses["changelog"] == Status.WARN
    assert statuses["metadata"] == Status.WARN
