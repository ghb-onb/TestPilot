"""Collector layer: collects and persists test results."""
from __future__ import annotations
import json
import sqlite3
from pathlib import Path
from typing import List, Optional
from src.models.test_case import TestResult, TestReport


class ResultCollector:
    """Collects test results and persists them to SQLite."""

    def __init__(self, db_path: str = "testpilot.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS test_results (
                id TEXT PRIMARY KEY,
                case_id TEXT,
                case_name TEXT,
                status TEXT,
                duration_ms REAL,
                failure_reason TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()

    def collect(self, result: TestResult) -> None:
        """Store a single test result."""
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            "INSERT OR REPLACE INTO test_results (id, case_id, case_name, status, duration_ms, failure_reason) VALUES (?, ?, ?, ?, ?, ?)",
            (result.case_id, result.case_id, result.case_name, result.status.value,
             result.total_duration_ms, result.failure_reason),
        )
        conn.commit()
        conn.close()

    def collect_batch(self, results: List[TestResult]) -> None:
        for r in results:
            self.collect(r)

    def get_all(self) -> List[dict]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        rows = conn.execute("SELECT * FROM test_results ORDER BY created_at DESC").fetchall()
        conn.close()
        return [dict(r) for r in rows]
