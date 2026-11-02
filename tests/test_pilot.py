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


