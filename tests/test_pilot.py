"""TestPilot test suite - 23 tests covering all layers."""
import os
import sys
import pytest
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models.test_case import TestCase, TestStep, StepStatus, StepResult, TestResult, TestReport
from src.models.scenario import TestScenario, ScenarioType
from src.planner import Planner
from src.generator import TestGenerator
from src.executor import MockExecutor
from src.collector import ResultCollector
from src.analyzer import FailureAnalyzer
from src.reporter import ReportGenerator
from src.pilot import TestPilot


# ===== Planner tests (5) =====
class TestPlanner:
    def test_login_detection(self):
        p = Planner()
        s = p.plan("测试登录功能")
        assert s.type == ScenarioType.LOGIN

    def test_search_detection(self):
        p = Planner()
        s = p.plan("测试搜索功能")
        assert s.type == ScenarioType.SEARCH

    def test_form_detection(self):
        p = Planner()
        s = p.plan("测试表单提交功能")
        assert s.type == ScenarioType.FORM_SUBMIT

    def test_url_extraction(self):
        p = Planner()
        s = p.plan("访问 http://example.com 测试")
        assert s.target_url == "http://example.com"

    def test_general_fallback(self):
        p = Planner()
        s = p.plan("随便做点什么")
        assert s.type == ScenarioType.GENERAL


# ===== Generator tests (4) =====
# NOTE: the class must not be named `TestGenerator`, otherwise it shadows the
# imported `TestGenerator` from src.generator inside this module's namespace.
class TestGeneratorLayer:
    def test_login_generation(self):
        g = TestGenerator()
        scenario = TestScenario(type=ScenarioType.LOGIN, name="登录测试")
        tc = g.generate(scenario)
        assert tc.id == "tc_login"
        assert len(tc.steps) == 5
        assert any("username" in s.selector for s in tc.steps)

    def test_search_generation(self):
        g = TestGenerator()
        scenario = TestScenario(type=ScenarioType.SEARCH, name="搜索测试")
        tc = g.generate(scenario)
        assert len(tc.steps) == 4

    def test_form_generation(self):
        g = TestGenerator()
        scenario = TestScenario(type=ScenarioType.FORM_SUBMIT, name="表单测试")
        tc = g.generate(scenario)
        assert len(tc.steps) == 5

    def test_nav_generation(self):
        g = TestGenerator()
        scenario = TestScenario(type=ScenarioType.NAVIGATION, name="导航测试")
        tc = g.generate(scenario)
        assert len(tc.steps) == 3


# ===== Executor tests (3) =====
class TestExecutor:
    def test_all_steps_pass(self):
        e = MockExecutor()
        tc = TestCase(id="tc1", name="测试", steps=[
            TestStep(id="s1", action="click", selector="#valid-btn"),
            TestStep(id="s2", action="fill", selector="#valid-input"),
        ])
        result = e.execute(tc)
        assert result.status == StepStatus.PASSED
        assert all(s.status == StepStatus.PASSED for s in result.step_results)

    def test_step_failure(self):
        e = MockExecutor()
        tc = TestCase(id="tc2", name="测试", steps=[
            TestStep(id="s1", action="click", selector="#broken-element"),
        ])
        result = e.execute(tc)
        assert result.status == StepStatus.FAILED
        assert result.step_results[0].error == "Element not found"

    def test_duration_recorded(self):
        e = MockExecutor()
        tc = TestCase(id="tc3", name="测试", steps=[
            TestStep(id="s1", action="click", selector="#valid"),
        ])
        result = e.execute(tc)
        assert result.total_duration_ms >= 0


