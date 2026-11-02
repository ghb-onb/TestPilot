"""Executor layer: executes test steps. Supports mock mode for CI/testing."""
from __future__ import annotations
import time
import uuid
from typing import List
from src.models.test_case import TestCase, StepResult, StepStatus, TestResult


class MockExecutor:
    """Simulates test execution without a real browser.

    In production, this wraps Playwright. In mock mode, steps pass by default
    unless they match known failure patterns (used by the analyzer tests).
    """

    # Steps whose selectors contain these substrings will "fail" in mock mode
    FAILURE_PATTERNS = {
        "#broken-element": "Element not found",
        ".timeout-element": "Timeout waiting for element",
    }

    def execute(self, test_case: TestCase) -> TestResult:
        """Execute all steps of a test case and return results."""
        result = TestResult(
            case_id=test_case.id,
            case_name=test_case.name,
            started_at=__import__("datetime").datetime.now(),
        )

        all_passed = True
        for step in test_case.steps:
            step_result = StepResult(step_id=step.id)
            start = time.time()

            failure = self._check_failure(step.selector)
            if failure:
                step_result.status = StepStatus.FAILED
                step_result.error = failure
                step_result.message = f"Step failed: {failure}"
                all_passed = False
            else:
                step_result.status = StepStatus.PASSED
                step_result.message = f"Step '{step.description}' executed successfully"

            step_result.duration_ms = round((time.time() - start) * 1000, 2)
            result.step_results.append(step_result)

        result.status = StepStatus.PASSED if all_passed else StepStatus.FAILED
        result.finished_at = __import__("datetime").datetime.now()
        if result.started_at and result.finished_at:
            result.total_duration_ms = (
                result.finished_at - result.started_at
            ).total_seconds() * 1000
        return result

    def _check_failure(self, selector: str | None) -> str | None:
        if not selector:
            return None
        for pattern, reason in self.FAILURE_PATTERNS.items():
            if pattern in selector:
                return reason
        return None
