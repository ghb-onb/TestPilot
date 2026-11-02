"""TestPilot main orchestrator: chains all six layers together."""
from __future__ import annotations
from typing import List, Optional
from src.planner import Planner
from src.generator import TestGenerator
from src.executor import MockExecutor
from src.collector import ResultCollector
from src.analyzer import FailureAnalyzer
from src.reporter import ReportGenerator
from src.models.test_case import TestCase, TestResult, TestReport
from src.models.scenario import TestScenario


class TestPilot:
    """Six-layer pipeline: Planner -> Generator -> Executor -> Collector -> Analyzer -> Reporter."""

    def __init__(self, db_path: str = "testpilot.db", use_llm: bool = False):
        self.planner = Planner(use_llm=use_llm)
        self.generator = TestGenerator()
        self.executor = MockExecutor()
        self.collector = ResultCollector(db_path=db_path)
        self.analyzer = FailureAnalyzer()
        self.reporter = ReportGenerator()

    def run(self, nl_request: str) -> TestResult:
        """Run a single test request through the full pipeline."""
        # 1. Plan: parse natural language
        scenario = self.planner.plan(nl_request)

        # 2. Generate: build test case
        test_case = self.generator.generate(scenario)

        # 3. Execute: run steps
        result = self.executor.execute(test_case)

        # 4. Analyze: diagnose failures
        result = self.analyzer.analyze(result)

        # 5. Collect: persist
        self.collector.collect(result)

        return result

    def run_batch(self, requests: List[str]) -> TestReport:
        """Run multiple test requests and return an aggregate report."""
        results = []
        for req in requests:
            result = self.run(req)
            results.append(result)
        return self.reporter.generate(results)
