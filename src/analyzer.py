"""Analyzer layer: diagnoses failed test steps."""
from __future__ import annotations
from src.models.test_case import TestResult, StepResult, StepStatus


class FailureAnalyzer:
    """Analyzes failed steps and produces human-readable diagnoses."""

    DIAGNOSIS_RULES = {
        "Element not found": (
            "元素未找到：可能是选择器过时或页面结构变化。建议：1)检查元素是否在iframe内；"
            "2)增加等待时间；3)确认CSS选择器是否与当前DOM匹配。"
        ),
        "Timeout waiting for element": (
            "元素超时：页面加载慢或元素未渲染。建议：1)增加timeout；"
            "2)检查网络请求；3)确认元素是否需要前置操作才出现。"
        ),
    }

    def analyze(self, result: TestResult) -> TestResult:
        """Analyze a test result and attach failure reasons to failed steps."""
        if result.status == StepStatus.PASSED:
            return result

        failed_steps = [s for s in result.step_results if s.status == StepStatus.FAILED]
        if not failed_steps:
            return result

        reasons = []
        for step in failed_steps:
            error = step.error or "未知错误"
            diagnosis = self.DIAGNOSIS_RULES.get(error, f"未分类错误：{error}")
            reasons.append(f"步骤{step.step_id}: {diagnosis}")

        result.failure_reason = " | ".join(reasons)
        return result
