"""Reporter layer: generates test reports."""
from __future__ import annotations
from typing import List
from src.models.test_case import TestResult, TestReport, StepStatus


class ReportGenerator:
    """Generates aggregated test reports."""

    def generate(self, results: List[TestResult]) -> TestReport:
        """Build a TestReport from individual results."""
        report = TestReport()
        report.results = results
        report.total = len(results)

        for r in results:
            if r.status == StepStatus.PASSED:
                report.passed += 1
            elif r.status == StepStatus.FAILED:
                report.failed += 1
            else:
                report.skipped += 1
        return report

    def to_dict(self, report: TestReport) -> dict:
        """Convert report to a serializable dict."""
        return {
            "total": report.total,
            "passed": report.passed,
            "failed": report.failed,
            "skipped": report.skipped,
            "pass_rate": report.pass_rate,
            "generated_at": report.generated_at.isoformat(),
            "results": [
                {
                    "case_id": r.case_id,
                    "case_name": r.case_name,
                    "status": r.status.value,
                    "duration_ms": r.total_duration_ms,
                    "failure_reason": r.failure_reason,
                }
                for r in report.results
            ],
        }
