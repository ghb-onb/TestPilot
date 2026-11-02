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


# ===== Collector tests (3) =====
class TestCollector:
    def test_collect_and_retrieve(self):
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        try:
            c = ResultCollector(db_path=db_path)
            r = TestResult(case_id="tc_x", case_name="测试", status=StepStatus.PASSED)
            c.collect(r)
            all_results = c.get_all()
            assert len(all_results) == 1
            assert all_results[0]["case_id"] == "tc_x"
        finally:
            os.unlink(db_path)

    def test_batch_collect(self):
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        try:
            c = ResultCollector(db_path=db_path)
            results = [
                TestResult(case_id=f"tc_{i}", case_name=f"测试{i}", status=StepStatus.PASSED)
                for i in range(3)
            ]
            c.collect_batch(results)
            assert len(c.get_all()) == 3
        finally:
            os.unlink(db_path)

    def test_persistence(self):
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        try:
            c = ResultCollector(db_path=db_path)
            c.collect(TestResult(case_id="tc_p", case_name="持久化", status=StepStatus.PASSED))
            c2 = ResultCollector(db_path=db_path)
            assert len(c2.get_all()) == 1
        finally:
            os.unlink(db_path)


# ===== Analyzer tests (3) =====
class TestAnalyzer:
    def test_passed_no_analysis(self):
        a = FailureAnalyzer()
        r = TestResult(case_id="tc1", case_name="测试", status=StepStatus.PASSED)
        result = a.analyze(r)
        assert result.failure_reason is None

    def test_element_not_found_diagnosis(self):
        a = FailureAnalyzer()
        r = TestResult(
            case_id="tc2", case_name="测试", status=StepStatus.FAILED,
            step_results=[StepResult(step_id="s1", status=StepStatus.FAILED, error="Element not found")],
        )
        result = a.analyze(r)
        assert "元素未找到" in result.failure_reason

    def test_timeout_diagnosis(self):
        a = FailureAnalyzer()
        r = TestResult(
            case_id="tc3", case_name="测试", status=StepStatus.FAILED,
            step_results=[StepResult(step_id="s1", status=StepStatus.FAILED, error="Timeout waiting for element")],
        )
        result = a.analyze(r)
        assert "超时" in result.failure_reason


# ===== Reporter tests (2) =====
class TestReporter:
    def test_report_generation(self):
        r = ReportGenerator()
        results = [
            TestResult(case_id="1", case_name="A", status=StepStatus.PASSED),
            TestResult(case_id="2", case_name="B", status=StepStatus.PASSED),
            TestResult(case_id="3", case_name="C", status=StepStatus.FAILED),
        ]
        report = r.generate(results)
        assert report.total == 3
        assert report.passed == 2
        assert report.failed == 1
        assert report.pass_rate == 66.7

    def test_report_dict(self):
        r = ReportGenerator()
        results = [TestResult(case_id="1", case_name="A", status=StepStatus.PASSED)]
        report = r.generate(results)
        d = r.to_dict(report)
        assert d["total"] == 1
        assert d["passed"] == 1


