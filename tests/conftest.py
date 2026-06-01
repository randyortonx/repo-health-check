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
