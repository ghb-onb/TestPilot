"""Scenario models for TestPilot."""
from __future__ import annotations
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class ScenarioType(str, Enum):
    LOGIN = "login"
    SEARCH = "search"
    FORM_SUBMIT = "form_submit"
    NAVIGATION = "navigation"
    NAV = "navigation"
    GENERAL = "general"


class TestScenario(BaseModel):
    """A parsed test scenario from natural language."""
    type: ScenarioType = ScenarioType.GENERAL
    name: str
    target_url: str = "http://localhost:8080"
    description: str = ""
    parameters: dict = Field(default_factory=dict)
    priority: int = 3  # 1(highest) - 5(lowest)
