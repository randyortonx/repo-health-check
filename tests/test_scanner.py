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


def test_scan_repository_records_files_as_sorted_sequence(repo_factory):
    repo = repo_factory({
        "b.txt": "B\n",
        "a.txt": "A\n",
        "nested/c.txt": "C\n",
    })

    snapshot = scan_repository(repo)

    assert snapshot.files == ("a.txt", "b.txt", "nested/c.txt")


def test_snapshot_read_text_rejects_paths_outside_repository(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "README.md").write_text("# Example\n", encoding="utf-8")
    (tmp_path / "outside.txt").write_text("outside\n", encoding="utf-8")

    snapshot = scan_repository(repo)

    with pytest.raises(ValueError, match="outside repository"):
        snapshot.read_text("../outside.txt")


def test_snapshot_read_text_rejects_ignored_files(repo_factory):
    repo = repo_factory({
        "README.md": "# Example\n",
        ".git/config": "[core]\n",
    })

    snapshot = scan_repository(repo)

    with pytest.raises(ValueError, match="not part of repository snapshot"):
        snapshot.read_text(".git/config")


def test_scan_repository_excludes_symlinked_files_outside_repository(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    outside = tmp_path / "outside.txt"
    outside.write_text("outside\n", encoding="utf-8")
    (repo / "linked-outside.txt").symlink_to(outside)

    snapshot = scan_repository(repo)

    assert not snapshot.has_file("linked-outside.txt")


def test_scan_repository_excludes_files_under_ignored_dirs(repo_factory):
    repo = repo_factory({
        "README.md": "# Example\n",
        "node_modules/package/index.js": "module.exports = {}\n",
        ".git/config": "[core]\n",
    })

    snapshot = scan_repository(repo)

    assert snapshot.has_file("README.md")
    assert not snapshot.has_file("node_modules/package/index.js")
    assert not snapshot.has_file(".git/config")


def test_scan_repository_raises_os_walk_errors(repo_factory, monkeypatch):
    repo = repo_factory({"README.md": "# Example\n"})

    def walk_with_error(_root, *, onerror=None):
        if onerror is not None:
            onerror(PermissionError("cannot read nested"))
        return iter(())

    monkeypatch.setattr("repo_health_check.scanner.os.walk", walk_with_error)

    with pytest.raises(PermissionError, match="cannot read nested"):
        scan_repository(repo)


def test_scan_repository_excludes_symlinked_files_into_ignored_dirs(repo_factory):
    repo = repo_factory({
        ".git/config": "[core]\n",
    })
    (repo / "README.md").symlink_to(".git/config")

    snapshot = scan_repository(repo)

    assert not snapshot.has_file("README.md")


def test_scan_repository_rejects_missing_path(tmp_path: Path):
    with pytest.raises(FileNotFoundError, match="Repository path does not exist"):
        scan_repository(tmp_path / "missing")


def test_scan_repository_rejects_file_path(tmp_path: Path):
    target = tmp_path / "README.md"
    target.write_text("# Not a directory\n", encoding="utf-8")

    with pytest.raises(NotADirectoryError, match="Repository path is not a directory"):
        scan_repository(target)
