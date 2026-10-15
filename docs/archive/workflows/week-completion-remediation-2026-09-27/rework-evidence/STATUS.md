# 本次返工执行状态（2026-09-27）

结论：**本地返工实现并部分验证（本地证据 PASS，含 945 后端 / 530 前端 / 同源 smoke 23/23）；
但"所有 EV 关闭"的产品级验收仍为 PARTIAL —— Playwright 真浏览器 E2E、独立实现复核、远端 CI、
生产迁移/发布在本轮 NOT_VERIFIED / NOT_AUTHORIZED。**

上一轮核验（R00–R07）的 FAIL 是对 *旧候选* 的裁定；本轮按 [rework-plan](../rework-plan.md)
B00–B07 重新执行并对每个 EV 给出本地证据。B07 的独立复核与真实浏览器 E2E 未在本地完成，
[rework-plan](../rework-plan.md) 的最终 accept 条件留待后续。

## 本轮实测结果

| 验证 | 命令/环境 | 结果 |
| --- | --- | --- |
| 前端单测 | `npm test` | **530 passed**（70 files；较之前 +5 为本轮新增回归） |
| 前端 TS | `npx tsc --noEmit` | 退出 0 |
| Next 构建 | `NEXT_PUBLIC_API_URL=http://ci-check.invalid:8000 npm run build` | 退出 0 |
| OpenNext/CF 构建 | `NEXT_PUBLIC_API_URL=http://ci-check.invalid:8001 npm run build:cf` | 退出 0（OpenNext build complete） |
| 后端全测（fresh 库） | `scripts/week4-scratch-guard.py run --db-name astra_week4_rework_full_v -- env -C backend PYTHONPATH=. .venv/bin/python -m pytest tests/ -q` | **945 passed, 9 skipped, 2 warnings, 47 subtests** |
| 迁移 fresh upgrade | 同上库 `alembic upgrade head`（026…034） | 成功至 034 |
| OpenNext 同源 smoke | `npm run build:cf` → `opennextjs-cloudflare preview --port 8787` + FastAPI :8001；`npm run smoke` | **23/23 checks 通过**（壳/资源/后端健康探针；workerd 工件 + 本地 FastAPI 隔离库） |
| ORM 门禁 | `alembic check` | "No new upgrade operations detected" |
| 受治理 catalog 门禁 | `python -m app.models.schema_catalog_gate` | "catalog gate passed: governed definitions match the manifest" |
| B02 只读候选报告 | `b02-legacy-kp-candidate-report.sql` 于隔离库执行 | 纯 SELECT，成功；未触碰生产/真实库 |
| 真实 provider / OCR 样本 | — | **NOT_EXECUTED（未授权）** |
| 真实浏览器 E2E（workerd+FastAPI 同源） | — | **未在本轮运行** |
| 远端 CI、生产迁移、backfill、deploy | — | **NOT_AUTHORIZED** |

## 测试覆盖到的反例闭环

- EV01 → `review-queue.test.tsx` 3 例（迟到响应、迟到失败、乱序题目 load）。
- EV02 → `test_b03_kp_delete_freeze.py`（真 HTTP 410 + 无副作用 + 并发 link 串行化）。
- EV03 → `test_b04_catalog_gate.py`（原三例 + 4 类新定义漂移反例；clean 复查通过）。
- EV04 → `test_b05_ai_canonical.py`（context 落库 / 绑定 / 重放幂等 / 异 payload / 错 actor / 题面版本 / 双会话竞态）。
- EV05 → `capture-workspace.test.tsx` 2 例（uploaded→人工题面→保存→ready→转换表单；recognized-only 引导）。
- B02 → `test_b02_kp_preservation.py`（跨事务矩阵）。

## 遗留与风险

1. Playwright E2E（workerd+FastAPI 同源完整用例）未在本轮执行，运行时 smoke（23/23）与 jsdom/服务级测试只等价于"壳/健康/产品逻辑"，不能替代原 5 个 E2E 与本轮新增竞争/OCR/AI 确认场景的真浏览器证据 — 本地运行仍未证明该；缺失独立的同源 E2E。
2. `astra_week4_rework_full_v` 是本轮新建的隔离 PG16 本地库；生产及远端 CI 状态不在本轮范围。
3. B05b 的 UI 是"可选 AI 候选"路径的人工接线，本轮未在本轮启动的完整 E2E 流程中点按验证。
4. B04 catalog manifest 是新代码初版提取并绑定revision 034；后续迁移必须随迁移一起做显式 manifest diff。
5. 上轮 9 项 skip（6 LSR03 专用库缺失 + 3 Week2 旧 scratch 前缀）未消除，仍单列。
6. 本轮曾出现一次性全套运行挂起，根因是 `link()`/`unlink()` 中先加入的行锁与既有并发重叠连接
   冲突；已回退为仅删除侧 `FOR UPDATE`（并保留语义注释），复跑全套 945 passed 通过。
