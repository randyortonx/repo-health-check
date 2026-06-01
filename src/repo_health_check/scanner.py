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
