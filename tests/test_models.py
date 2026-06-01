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
