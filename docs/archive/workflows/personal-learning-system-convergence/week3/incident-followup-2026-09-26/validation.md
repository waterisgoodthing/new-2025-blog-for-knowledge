# 证据与结果

## Week 3 只读复核：PARTIAL

独立 agent `/root/verify_week3`：公共 active+public allowlist、migration032 复合 PK/双 CASCADE、KP 排序/practice 窗口/Dashboard canonical 数据链与声明相符。多数 SQL/API/测试/截图保存材料支持完成。历史结果是保存证据复核，本轮未复跑全量产品环境。

发现：
- Gate 实际路径 `../evidence/root-week3-relocated/gate/`，报告原索引失效。
- Gate 原测试摘要日期 2026-09-25；INC-02 数据日期 09-23/24；清理 09-26。报告统一 09-22 裁决/完成与时间线冲突；真实裁决日期无法从现文件确认，不虚构更正日期。
- 目标后端 147、前端 516、全量 821 passed/4 failed/9 skipped、smoke 20/20 有保存材料。三个污染失败有隔离 PASS；psycopg2 环境失败为 n/a。三个失败属于 Week3 新测试，缺少 Week2 基线，不能统称预存。
- migration/build/preview/backend 摘要引用的 .log 原件未找到，只有摘要/schema/HTTP辅证；Gate最终独立评审/G2/G3落盘原报告未找到，只有 TRACKING记述。
- browser摘要 KP 7/8 与 SQL 139/140 不一致；reduced-motion emulation 原记录未生效，截图不能证明该行为。

历史 Gate PASS 不撤销；本次对证据完整性的独立核实为 PARTIAL，待原始材料补齐。没有重写原证据或伪造日志。

## 本轮无数据库验证

- `backend/.venv/bin/python scripts/incident-db-safety.test.py`：6 tests PASS。真实 engine 事件+mock DBAPI，含目标/hostaddr覆盖；子进程 socket 禁止连接，四个脚本、Alembic及collection-time拒绝，network sentinel不存在。
- `backend/.venv/bin/python scripts/week3-scratch-guard.test.py`：36 tests PASS。
- backend `PYTHONPATH=. .venv/bin/python -m pytest tests/test_week3_contracts.py -q`：60 passed。
- `git diff --check`：exit 0。
- 独立评审初次 CHANGES_REQUIRED（hostaddr）；返工后 `/root/verify_week3` 最终 PASS，独立复跑 6 tests PASS。主 agent 对本轮防复发范围验收 PASS；不构成完整产品环境重验或生产放行。

未连接数据库，未创建/删除 scratch，未触及任何常驻进程或实际迁移。mock 放行不宣称完整 DB 套件成功。旧测试依赖默认 blog_v2 将被明确拒绝，须另行准备隔离 scratch；本轮没有全量重跑。
