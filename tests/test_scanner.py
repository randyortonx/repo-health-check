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
