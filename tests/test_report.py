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
