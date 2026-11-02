"""Generator layer: builds test cases (steps) from scenarios."""
from __future__ import annotations
from typing import List
from src.models.scenario import TestScenario, ScenarioType
from src.models.test_case import TestCase, TestStep


class TestGenerator:
    """Converts a TestScenario into an executable TestCase with steps."""

    def generate(self, scenario: TestScenario) -> TestCase:
        """Generate a test case based on scenario type."""
        generators = {
            ScenarioType.LOGIN: self._gen_login,
            ScenarioType.SEARCH: self._gen_search,
            ScenarioType.FORM_SUBMIT: self._gen_form,
            ScenarioType.NAVIGATION: self._gen_nav,
        }
        gen_func = generators.get(scenario.type, self._gen_general)
        return gen_func(scenario)

    def _gen_login(self, s: TestScenario) -> TestCase:
        username = s.parameters.get("username", "testuser")
        password = s.parameters.get("password", "testpass123")
        steps = [
            TestStep(id="s1", action="navigate", description=f"打开登录页", selector=s.target_url),
            TestStep(id="s2", action="fill", description="输入用户名", selector="#username", value=username),
            TestStep(id="s3", action="fill", description="输入密码", selector="#password", value=password),
            TestStep(id="s4", action="click", description="点击登录按钮", selector="#login-btn"),
            TestStep(id="s5", action="expect", description="验证登录成功", selector=".welcome-message", value="欢迎"),
        ]
        return TestCase(
            id=f"tc_{s.type.value}",
            name=s.name,
            description=s.description,
            scenario_type=s.type.value,
            steps=steps,
            tags=["login", "auth"],
        )

    def _gen_search(self, s: TestScenario) -> TestCase:
        keyword = s.parameters.get("keyword", "测试")
        steps = [
            TestStep(id="s1", action="navigate", description="打开首页", selector=s.target_url),
            TestStep(id="s2", action="fill", description="输入搜索关键词", selector="#search-input", value=keyword),
            TestStep(id="s3", action="press", description="按回车搜索", selector="#search-input", value="Enter"),
            TestStep(id="s4", action="expect", description="验证搜索结果", selector=".search-results"),
        ]
        return TestCase(
            id=f"tc_{s.type.value}",
            name=s.name,
            description=s.description,
            scenario_type=s.type.value,
            steps=steps,
            tags=["search"],
        )

    def _gen_form(self, s: TestScenario) -> TestCase:
        steps = [
            TestStep(id="s1", action="navigate", description="打开表单页", selector=s.target_url),
            TestStep(id="s2", action="fill", description="填写姓名", selector="#name", value="测试用户"),
            TestStep(id="s3", action="fill", description="填写邮箱", selector="#email", value="test@example.com"),
            TestStep(id="s4", action="click", description="点击提交", selector="#submit-btn"),
            TestStep(id="s5", action="expect", description="验证提交成功", selector=".success-message"),
        ]
        return TestCase(
            id=f"tc_{s.type.value}",
            name=s.name,
            description=s.description,
            scenario_type=s.type.value,
            steps=steps,
            tags=["form", "submit"],
        )

    def _gen_nav(self, s: TestScenario) -> TestCase:
        steps = [
            TestStep(id="s1", action="navigate", description="打开目标页面", selector=s.target_url),
            TestStep(id="s2", action="expect", description="验证页面加载", selector="body"),
            TestStep(id="s3", action="screenshot", description="截图记录", selector="body"),
        ]
        return TestCase(
            id=f"tc_{s.type.value}",
            name=s.name,
            description=s.description,
            scenario_type=s.type.value,
            steps=steps,
            tags=["navigation"],
        )

    def _gen_general(self, s: TestScenario) -> TestCase:
        steps = [
            TestStep(id="s1", action="navigate", description="打开页面", selector=s.target_url),
            TestStep(id="s2", action="expect", description="验证页面加载", selector="body"),
        ]
        return TestCase(
            id=f"tc_{s.type.value}",
            name=s.name,
            description=s.description,
            scenario_type=s.type.value,
            steps=steps,
            tags=["general"],
        )
