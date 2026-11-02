"""Pydantic data models for TestPilot."""
from __future__ import annotations
from enum import Enum
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class StepStatus(str, Enum):
    PENDING = "pending"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"


class TestStep(BaseModel):
    """A single executable step in a test case."""
    id: str
    action: str  # navigate, click, fill, press, expect, screenshot
    selector: Optional[str] = None
    value: Optional[str] = None
    description: str = ""
    timeout_ms: int = 5000


class StepResult(BaseModel):
    """Result of executing a single step."""
    step_id: str
    status: StepStatus = StepStatus.PENDING
    message: str = ""
    duration_ms: float = 0.0
    screenshot_path: Optional[str] = None
    error: Optional[str] = None


class TestCase(BaseModel):
    """A test case composed of multiple steps."""
    id: str
    name: str
    description: str = ""
    scenario_type: str = "general"
    steps: List[TestStep] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)


class TestResult(BaseModel):
    """Result of a single test case execution."""
    case_id: str
    case_name: str
    status: StepStatus = StepStatus.PENDING
    step_results: List[StepResult] = Field(default_factory=list)
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    total_duration_ms: float = 0.0
    failure_reason: Optional[str] = None


class TestReport(BaseModel):
    """Aggregated test execution report."""
    total: int = 0
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    results: List[TestResult] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=datetime.now)

    @property
    def pass_rate(self) -> float:
        return round(self.passed / self.total * 100, 1) if self.total > 0 else 0.0
