# Week 4 — RELEASE GATE 执行计划摘要

> 完整文档：[README.md](README.md) · 任务详情：[tasks/](tasks/) · 进度跟踪：[TRACKING.md](TRACKING.md)

## 目标

Week 4 建立发布门禁，完成 30 天收敛工程（M1→M2→M3→M4）：

1. **OCR 诊断** — 失败分类、可见性、重试流程
2. **认证加固** — WebAuthn challenge 生命周期、登录限流
3. **AI 治理收尾** — 目标 ID 纪律、分类决策
4. **CI 完整性** — 四 Job 流水线 + E2E 覆盖
5. **遗留清理** — 带证据删除死代码

## 串行执行顺序

```
W4-00 预检 → PR-14 OCR → PR-15 WebAuthn → PR-19 AI (可并行) → PR-16 限流 → PR-17 CI → PR-18 清理 → Gate
```

## 工作包

| PR | 需求 | 风险 | 关键验收 |
|---|---|---|---|
| W4-00 | 预检与范围锁定 | MEDIUM | 基线快照、迁移 032 确认、OCR/WebAuthn/清理候选盘点 |
| PR-14 | OCR 诊断与 UI | MEDIUM | 10 样本 ≥8 成功或入口标记/禁用；失败分类；重试可用 |
| PR-15 | WebAuthn challenges 表 | HIGH | migration 033；三类 ceremony 保持；并发/过期/已消费/跨目的隔离 |
| PR-19 | AI 治理收尾 | MEDIUM | polish 分类决策；持久化调用写 target_id；创建流回填 |
| PR-16 | 登录限流 | HIGH | 双维度（账户+IP）；递增延迟 0→0→0→2s→5s→15s；成功重置 |
| PR-17 | CI 四 Job | MEDIUM | Job 1 前端、Job 2 后端、Job 3 runtime smoke、Job 4 E2E(workers=1) |
| PR-18 | 遗留清理 | MEDIUM | 三证据删除（grep+测试+运行时）；SM-2/旧客户端/死端点/WIP 组件 |

## 关键决策

- **W4-D02**: OCR 诊断优先，不重写管线
- **W4-D03**: WebAuthn 表模式：purpose + binding keys + TTL
- **W4-D04**: 限流无永久锁定，渐进式延迟，可配置
- **W4-D05**: Polish 是瞬态预览（豁免）；持久化 AI 必须链接 target_id
- **W4-D06**: CI 四 Job 契约（前端、后端、smoke、E2E）
- **W4-D07**: 遗留清理三证据要求

## Week 4 Gate 矩阵

| 验收项 | 目标 | 状态 |
|---|---|---|
| OCR 基线 | ≥8/10 或入口标记 | NOT_STARTED |
| WebAuthn 迁移 033 | fresh + 增量回放 PASS | NOT_STARTED |
| AI 治理分类 | polish 决策已记录 | NOT_STARTED |
| 登录限流 | 延迟时序测试 PASS | NOT_STARTED |
| CI 四 Job | 全绿 | NOT_STARTED |
| 遗留清理 | 三证据完整 | NOT_STARTED |
| 基线健康 | 前端 516+、后端 821+/≤4/≤9 | NOT_STARTED |
| 迁移 head | 单 head 033 | NOT_STARTED |

## 授权边界

**已授权**：Week 4 计划编写（2026-09-26 完成）

**未授权**：
- Week 4 实施（需单独明确批准）
- 生产迁移执行
- Commit/stage/push/merge
- 部署到任何环境
- Week 5+ 或 30 天计划外工作

## 风险与缓解

| 风险 | 缓解 |
|---|---|
| OCR 基线 <80% | 标记实验性或禁用；Gate 通过需诚实披露 |
| WebAuthn ceremony 破坏 | 保留确切调用签名；测试三类 ceremony |
| 限流 UX 降级 | 渐进式延迟；可配置阈值 |
| CI 不稳定 | workers=1；记录 flake；重试策略 |
| 遗留清理删错代码 | 三证据；增量删除；每步全量测试 |

## 明确不做

- OCR 管线重写或模型替换
- 候选确认 UI (PR-22)
- 后台状态跟踪 (PR-26)
- 认证 UI 重设计 (PR-20)
- 撤销 API/UI (PR-24)
- 每日 AI 推荐 (PR-25)
- FSRS、向量搜索、Redis、Elasticsearch
- 数据库列/表清理（仅应用代码）

## 证据位置

所有证据文件存储在：
```
docs/workflows/personal-learning-system-convergence/week4/evidence/
```

## 估算时长

5 个工作日（W4-00: 1-2d, PR-14: 2-3d, PR-15: 3-4d, PR-19: 1-2d, PR-16: 2-3d, PR-17: 2-3d, PR-18: 2-3d, Gate: 1-2d）

实际执行可能并行 PR-19 与 PR-15/16，缩短总时长。

---

**下一步**：等待用户批准 Week 4 实施授权，然后启动 W4-00 预检。
