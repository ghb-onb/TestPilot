"""FastAPI interface for TestPilot."""
from __future__ import annotations
from typing import Optional, List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.pilot import TestPilot

app = FastAPI(title="TestPilot API", version="1.0.0")
_pilot: Optional[TestPilot] = None


class TestRequest(BaseModel):
    request: str


class BatchTestRequest(BaseModel):
    requests: List[str]


def get_pilot() -> TestPilot:
    global _pilot
    if _pilot is None:
        _pilot = TestPilot()
    return _pilot


@app.post("/api/test")
def run_test(req: TestRequest):
    """Run a single test request."""
    pilot = get_pilot()
    result = pilot.run(req.request)
    return {
        "case_id": result.case_id,
        "case_name": result.case_name,
        "status": result.status.value,
        "duration_ms": result.total_duration_ms,
        "failure_reason": result.failure_reason,
    }


@app.post("/api/test/batch")
def run_batch(req: BatchTestRequest):
    """Run a batch of test requests."""
    pilot = get_pilot()
    report = pilot.run_batch(req.requests)
    return pilot.reporter.to_dict(report)


@app.get("/api/report")
def get_report():
    """Get all stored test results."""
    pilot = get_pilot()
    return {"results": pilot.collector.get_all()}


@app.get("/health")
def health():
    return {"status": "ok"}
