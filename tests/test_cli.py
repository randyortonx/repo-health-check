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
