"""TestPilot Demo: runs 7 test scenarios and prints a report."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.pilot import TestPilot

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCENARIO_FILE = os.path.join(BASE_DIR, "demo_data", "scenarios.json")

# Fallback if demo_data/scenarios.json is missing
DEFAULT_SCENARIOS = [
    "测试登录功能，用户名是admin，密码是123456",
    "测试搜索功能，搜索关键词「AI测试」",
    "测试表单提交功能",
    "测试导航到首页 http://localhost:8080",
    "测试登录功能，用户名是testuser",
    "测试搜索功能，搜索「自动化测试工具」",
    "测试一般功能",
]


def load_scenarios():
    """Load demo scenarios from demo_data/scenarios.json, fallback to built-in list.

    Returns (scenarios, source_label).
    """
    try:
        with open(SCENARIO_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        scenarios = data["scenarios"] if isinstance(data, dict) else data
        if scenarios:
            return scenarios, "demo_data/scenarios.json"
    except (OSError, ValueError, KeyError):
        pass
    return DEFAULT_SCENARIOS, "built-in list"


def main():
    print("=" * 60)
    print("  TestPilot Demo - AI Automated Testing Agent")
    print("=" * 60)

    scenarios, source = load_scenarios()
    print(f"  Loaded {len(scenarios)} scenarios from {source}")

    pilot = TestPilot(db_path="demo_testpilot.db")

    import time
    start = time.time()
    report = pilot.run_batch(scenarios)
    elapsed = time.time() - start

    print(f"\n  Total: {report.total}")
    print(f"  Passed: {report.passed}")
    print(f"  Failed: {report.failed}")
    print(f"  Pass Rate: {report.pass_rate}%")
    print(f"  Duration: {elapsed:.2f}s")
    print("=" * 60)

    for r in report.results:
        status = "PASS" if r.status.value == "passed" else "FAIL"
        print(f"  [{status}] {r.case_name} ({r.case_id})")

    # Cleanup demo db
    if os.path.exists("demo_testpilot.db"):
        os.remove("demo_testpilot.db")

    print("\n  Demo complete!")


if __name__ == "__main__":
    main()
