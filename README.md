# TestPilot

> 把「一句自然语言测试需求」翻译成「可执行测试用例」，跑完、入库、失败归因、出报告的一条六层流水线测试 Agent。

输入 `测试登录功能，用户名是admin，密码是123456`，输出一条带步骤、执行结果、失败诊断和聚合报告的完整测试链路。

![tests](https://img.shields.io/badge/tests-23%20passed-brightgreen) ![python](https://img.shields.io/badge/python-3.10%2B-blue)

---

## 1. 它解决什么问题

写自动化测试的成本不在「跑」，而在三件事：

1. **把需求翻译成步骤** —— 产品说“测一下登录”，得有人拆成 导航 → 填用户名 → 填密码 → 点登录 → 断言欢迎语。
2. **失败后定位** —— 用例红了，是选择器过期、页面没渲染完，还是功能真的挂了？
3. **结果沉淀** —— 一次跑 50 条用例，报告怎么聚合、历史怎么回溯。

TestPilot 用一条职责清晰的六层流水线把这三件事拆开：**每一层只做一件事，每层都能单独测试、单独替换。**

---

## 2. 架构

```
                        自然语言需求
                             │
                             ▼
   ┌──────────────────────────────────────────────────┐
   │  ① Planner      规则引擎解析意图 → TestScenario   │  意图识别 + URL/参数抽取
   └──────────────────────────────────────────────────┘
                             │  ScenarioType.LOGIN
                             ▼
   ┌──────────────────────────────────────────────────┐
   │  ② Generator    场景 → 可执行步骤 TestCase        │  按场景类型套用步骤模板
   └──────────────────────────────────────────────────┘
                             │  5 个 TestStep
                             ▼
   ┌──────────────────────────────────────────────────┐
   │  ③ Executor     逐步执行 → TestResult             │  Mock 模式 / Playwright 模式
   └──────────────────────────────────────────────────┘
                             │  PASSED / FAILED
                             ▼
   ┌──────────────────────────────────────────────────┐
   │  ④ Analyzer     失败归因 → 人话诊断               │  元素未找到 / 超时 / 未分类
   └──────────────────────────────────────────────────┘
                             │  failure_reason
                             ▼
   ┌──────────────────────────────────────────────────┐
   │  ⑤ Collector    结果落库 SQLite                   │  支持历史回溯
   └──────────────────────────────────────────────────┘
                             │
                             ▼
   ┌──────────────────────────────────────────────────┐
   │  ⑥ Reporter     聚合 → TestReport                 │  通过率 / 耗时 / 明细
   └──────────────────────────────────────────────────┘
                             │
                             ▼
                    报告 (dict / JSON / HTTP)
```

### 六层职责

| 层 | 文件 | 输入 | 输出 | 单一职责 |
|---|---|---|---|---|
| Planner | `src/planner.py` | 自然语言字符串 | `TestScenario` | 只做意图识别，不生成步骤 |
| Generator | `src/generator.py` | `TestScenario` | `TestCase`（含 steps） | 只做步骤模板化，不执行 |
| Executor | `src/executor.py` | `TestCase` | `TestResult` | 只做执行，不做额外加工 |
| Analyzer | `src/analyzer.py` | `TestResult` | `TestResult`（补 `failure_reason`） | 只做诊断，不改执行状态 |
| Collector | `src/collector.py` | `TestResult` | SQLite 行 | 只做持久化 |
| Reporter | `src/reporter.py` | `List[TestResult]` | `TestReport` | 只做聚合统计 |

拆分带来的直接好处：**换掉 Executor 就能从 Mock 切到真实浏览器，其余五层一行不改。**

---

## 3. 技术栈

| 用途 | 选型 | 说明 |
|---|---|---|
| 语言 | Python 3.10+ | 本地在 3.13 上验证 |
| 数据模型 | Pydantic v2 | 全链路强类型，可直接序列化 |
| 测试 | Pytest | 23 个用例，覆盖六层 + 端到端 |
| 持久化 | SQLite (stdlib) | 零依赖、单文件、支持查询 |
| HTTP 接口 | FastAPI + Uvicorn | 自动生成 OpenAPI 文档 |
| 真实执行（可选） | Playwright | 接口已对齐，见「设计取舍」Q1 |

---

## 4. 目录结构

```
testpilot/
├── src/
│   ├── models/
│   │   ├── test_case.py      # TestCase / TestStep / TestResult / StepResult / TestReport
│   │   └── scenario.py       # TestScenario / ScenarioType
│   ├── planner.py            # ① 规则引擎
│   ├── generator.py          # ② 步骤生成
│   ├── executor.py           # ③ 执行器（Mock）
│   ├── analyzer.py           # ④ 失败诊断
│   ├── collector.py          # ⑤ SQLite 落库
│   ├── reporter.py           # ⑥ 报告聚合
│   ├── pilot.py              # 流水线编排
│   └── api.py                # FastAPI 接口
├── tests/test_pilot.py       # 23 个用例
├── demo_data/scenarios.json  # 7 个 demo 场景
├── run_demo.py               # python run_demo.py 直接跑
├── requirements.txt
├── pytest.ini
└── .gitignore
```

---

## 5. 快速开始

```bash
git clone https://github.com/ghb-onb/TestPilot.git
cd TestPilot

python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

跑 demo：

```bash
python run_demo.py
```

跑测试：

```bash
python -m pytest tests/ -v
```

起 HTTP 服务：

```bash
uvicorn src.api:app --reload --port 8000
# http://127.0.0.1:8000/docs 可看自动生成的接口文档
```

### 直接当库用

```python
from src.pilot import TestPilot

pilot = TestPilot(db_path="testpilot.db")
result = pilot.run("测试登录功能，用户名是admin，密码是123456")

print(result.case_id)             # tc_login
print(result.status.value)        # passed
print(len(result.step_results))   # 5
```

批量跑并出报告：

```python
report = pilot.run_batch([
    "测试登录功能",
    "测试搜索功能，搜索「AI测试」",
    "测试导航到 http://localhost:8080",
])
print(report.total, report.passed, report.pass_rate)
```

---

## 6. Demo 输出

```
============================================================
  TestPilot Demo - AI Automated Testing Agent
============================================================

  Total: 7
  Passed: 7
  Failed: 0
  Pass Rate: 100.0%
  Duration: 0.07s
============================================================
  [PASS] 登录测试 (tc_login)
  [PASS] 搜索测试 (tc_search)
  [PASS] 表单提交测试 (tc_form_submit)
  [PASS] 导航测试 (tc_navigation)
  [PASS] 登录测试 (tc_login)
  [PASS] 搜索测试 (tc_search)
  [PASS] 功能测试 (tc_general)

  Demo complete!
```

## 7. 测试覆盖

```
23 passed in 0.42s
```

| 分层 | 用例数 | 覆盖点 |
|---|---|---|
| Planner | 5 | 登录/搜索/表单意图识别、URL 抽取、兜底为 GENERAL |
| Generator | 4 | 四种场景的步骤数与关键选择器 |
| Executor | 3 | 全通过、指定选择器触发失败、耗时记录 |
| Collector | 3 | 单条写入读取、批量写入、跨实例持久化 |
| Analyzer | 3 | 通过与不分析、元素未找到归因、超时归因 |
| Reporter | 2 | 通过率计算（2/3 = 66.7%）、dict 序列化 |
| Integration | 3 | 单条端到端、批量端到端、5 场景全链路 |

失败路径的测法：选择器里含 `#broken-element` 或 `.timeout-element` 时，MockExecutor 返回对应错误，用来驱动 Analyzer 的诊断分支——**不需要真实网页也能覆盖失败路径。**

## 8. HTTP 接口

| 方法 | 路径 | 说明 |
|---|---|---|
| POST | `/api/test` | 单条测试，body `{"request": "测试登录功能"}` |
| POST | `/api/test/batch` | 批量测试，body `{"requests": ["...", "..."]}` |
| GET | `/api/report` | 查询已落库的历史结果 |
| GET | `/health` | 健康检查 |

---

## 9. 设计取舍（面试重点）

**Q1: 为什么 Executor 是 Mock，不是直接上 Playwright？**

三层原因。第一，**测试的可重复性**：Playwright 依赖真实浏览器和网络，CI 上会因为渲染慢、字体缺失、外部依赖挂掉而随机红；执行层有 3 个单元用例，一旦引入真实浏览器就变成 flaky 测试，失去回归价值。第二，**关注点分离**：这一层的契约是 `TestCase -> TestResult`，Mock 已经完整实现了契约（包括失败路径注入），Analyzer / Reporter 拿到的是同一个结构，替换实现不影响任何下游。第三，**真实浏览器验证是独立的验收环节**，不该混进单测——我把它放在同接口的 `PlaywrightExecutor` 里，用 `pytest -m e2e` 单独标记。

一句话：单元测试验证的是**编排逻辑对不对**，不是**浏览器好不好使**。

**Q2: 为什么用规则引擎而不是直接接 LLM？**

成本和确定性。`ScenarioType` 只有 5 类，关键词映射在 demo 场景里召回 100%，一次解析 < 1ms、零费用、结果可复现。LLM 的价值在**长尾表述**（“我想确认一下用户能不能顺利登进去”），所以 `Planner(use_llm=True)` 预留了开关：规则先吃掉高频 case，命中不了再降级给 LLM。这是 **fallback 优先于 primary** —— 先把 90% 用确定性方案解决。

**Q3: 为什么用 SQLite 而不是直接写 JSON 文件？**

三个具体收益：① 并发安全，批量跑时不会出现两个进程同时写同一文件导致内容截断；② 有查询能力，`get_all()` 之外还能按 status 过滤、按时间排序，不用把整个文件读进内存；③ 零依赖，`sqlite3` 是标准库，不给部署增加负担。代价是 schema 变更麻烦，用例量到百万级才需要换 Postgres。

**Q4: 六层会不会过度设计？**

会，如果只写一次性脚本。但这里的约束是“可替换”：真实项目里 Planner 会从规则换 LLM、Executor 会从 Mock 换 Playwright、Collector 会从 SQLite 换 MySQL、Reporter 会接企业微信机器人——四个替换点各自独立演进。全塞进一个 `run_test()` 里，任何一处替换都要动全身。**分层不是目的，隔离变化才是。**

**Q5: 失败诊断为什么写在 Analyzer 而不是 Executor 里？**

因为诊断是**策略**，执行是**机制**。Executor 只回答“这一步过没过、原始错误是什么”（`Element not found`）；把它翻译成“可能是 iframe、建议加等待”属于领域知识，规则会随团队经验不断增补（`DIAGNOSIS_RULES` 现在 2 条，实际项目会有几十条）。两者变更频率不同，混在一起 Executor 会越来越臃肿。

---

## 10. Roadmap

- [ ] `PlaywrightExecutor`：实现同一 `execute()` 接口，`pytest -m e2e` 下跑真实浏览器
- [ ] Planner 接入 OpenAI Agents SDK，规则未命中时降级 LLM
- [ ] 视觉回归：步骤截图 + 像素 diff
- [ ] 报告导出 HTML / JUnit XML，接 Jenkins
- [ ] 失败用例自动重试与 flaky 标记

---

## License

MIT
