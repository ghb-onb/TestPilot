"""Planner layer: parses natural language into test scenarios using rule engine."""
from __future__ import annotations
import re
from typing import Optional
from src.models.scenario import TestScenario, ScenarioType


class Planner:
    """Rule-based planner that converts natural language to test scenarios.

    Falls back to rule matching when no LLM API key is available.
    """

    KEYWORD_MAP = {
        ScenarioType.LOGIN: ["登录", "login", "登陆", "sign in", "登入"],
        ScenarioType.SEARCH: ["搜索", "search", "查找", "查询"],
        ScenarioType.FORM_SUBMIT: ["提交", "表单", "form", "submit", "注册", "填写"],
        ScenarioType.NAVIGATION: ["导航", "跳转", "navigate", "打开", "访问", "进入"],
    }

    def __init__(self, use_llm: bool = False):
        self.use_llm = use_llm

    def plan(self, nl_request: str) -> TestScenario:
        """Parse a natural language test request into a structured scenario."""
        nl_lower = nl_request.lower().strip()

        scenario_type = self._detect_type(nl_lower)
        target_url = self._extract_url(nl_request)
        name = self._extract_name(nl_request, scenario_type)

        return TestScenario(
            type=scenario_type,
            name=name,
            target_url=target_url,
            description=nl_request,
            parameters=self._extract_params(nl_request, scenario_type),
        )

    def _detect_type(self, nl: str) -> ScenarioType:
        for stype, keywords in self.KEYWORD_MAP.items():
            if any(kw in nl for kw in keywords):
                return stype
        return ScenarioType.GENERAL

    def _extract_url(self, nl: str) -> str:
        match = re.search(r'https?://[^\s，。]+', nl)
        if match:
            return match.group(0)
        return "http://localhost:8080"

    def _extract_name(self, nl: str, stype: ScenarioType) -> str:
        prefix_map = {
            ScenarioType.LOGIN: "登录测试",
            ScenarioType.SEARCH: "搜索测试",
            ScenarioType.FORM_SUBMIT: "表单提交测试",
            ScenarioType.NAVIGATION: "导航测试",
            ScenarioType.GENERAL: "功能测试",
        }
        return prefix_map.get(stype, "功能测试")

    def _extract_params(self, nl: str, stype: ScenarioType) -> dict:
        params = {}
        if stype == ScenarioType.LOGIN:
            user_match = re.search(r'(用户名|账号|username|user)[是为:：\s]*([^\s，。]+)', nl, re.IGNORECASE)
            pass_match = re.search(r'(密码|password)[是为:：\s]*([^\s，。]+)', nl, re.IGNORECASE)
            if user_match:
                params["username"] = user_match.group(2)
            if pass_match:
                params["password"] = pass_match.group(2)
        elif stype == ScenarioType.SEARCH:
            kw_match = re.search(r'(搜索|search|查找)[了过]?[^\s，。]*[「『"](.+?)[」』"]', nl, re.IGNORECASE)
            if kw_match:
                params["keyword"] = kw_match.group(2)
            else:
                # Try to find the object after search keyword
                after = re.split(r'(搜索|search|查找|查询)', nl, flags=re.IGNORECASE)
                if len(after) >= 3:
                    params["keyword"] = after[-1].strip().strip("，。 ")
        return params
