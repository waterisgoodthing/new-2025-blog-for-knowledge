# 建议汇总（2026-08-29 全天对话）

> 来源：三轮评估（全量扫描 → 暑期路线复盘 → 再扫描定路线）加一轮安全修复执行。每条标注**当前状态**，可当作跟踪清单使用。执行细节见 `docs/workflows/security-findings-remediation/` 与 `docs/roadmap-2026-09.md`。

## 一、全量扫描的 15 条建议（2026-08-29 上午）

### P0 — 部署阻断 / 数据安全

| # | 建议 | 状态 |
|---|------|------|
| 1 | `EXPECTED_ALEMBIC_REVISION=025` 与迁移 026 脱节，升级后后端拒绝启动；CI 的 import check 不触发 lifespan 发现不了 | ✅ 已修复（`backend/main.py` 钉 026，同提交落地迁移） |
| 2 | 迁移 026 无 `downgrade()`，且含集群级操作（CREATE ROLE / CREATE EXTENSION / REVOKE FROM PUBLIC） | ✅ 已加受保护 downgrade（明确报错+指引）；生产执行仍需 DBA 评估（决策点 D1） |

### P1 — CI 与工程化

| # | 建议 | 状态 |
|---|------|------|
| 3 | CI 从不运行前端 374 个测试与 `test:typecheck` | ⏳ 未做（路线 W1：CI 补 `npm test`） |
| 4 | 全仓库零 lint（无 ESLint / ruff，Prettier 未强制） | ⏳ 未做（W1） |
| 5 | 后端无 conftest/pytest 配置，测试导入依赖 CI 运行目录；`pip install pytest` 重复且未锁版本 | ⏳ 未做（W1 顺带） |
| 6 | CI 起了 Postgres 但测试不用它，模型↔迁移漂移发现不了 | 🔶 当天已验证其价值：真库 CI 抓出了 026 列缺陷（见二）；补集成测试仍列 W6+ |

### P1 — 安全与后端质量

| # | 建议 | 状态 |
|---|------|------|
| 7 | 默认 JWT secret / AUTH_BYPASS 仅 production 拦截；注册密钥 `!=` 比较；孤儿 passkey reg-options 端点 | ✅ 全部修复（非 dev 环境 fail-closed、`secrets.compare_digest`、端点移除） |
| 8 | 14 处 `detail=str(e)` 向客户端泄漏内部错误 | ✅ 全部脱敏 + 服务端 `logger.exception` |
| 9 | 管理端列表 N+1（questions 4N+1 / mistakes 3N+1）；notes 搜索不用已有 GIN 索引 | ⏳ 未做（W6+ 候选） |

### P1 — 前端质量

| # | 建议 | 状态 |
|---|------|------|
| 10 | 5,782 行死路由树（`/write*`、`/mistakes/review` 已被重定向） | ⏳ 未做（**W1 第一件事**） |
| 11 | 双轨认证 + 网络错误即登出（`use-admin-auth` 忽略 error） | ⏳ 未做 |
| 12 | manage 页签绕过统一 API 客户端（相对路径 `fetch('/api/...')`） | ⏳ 未做 |
| 13 | 数据层缺陷：原地改 SWR 缓存、hidden 帖子元数据下发客户端、`size:100` 截断、54 处吞异常 catch | ⏳ 未做 |
| 14 | 0/49 页有 metadata/OG；GA ID 硬编码 | ⏳ 未做（W5） |

### P1/P2 — 仓库治理

| # | 建议 | 状态 |
|---|------|------|
| 15 | `agents/` 治理文档未入库；`.gitignore` 缺 7 个工具目录；24MB 版权 MP3；历史文档宣称 JWT；docs/ 55MB/104 文件夹堆积；无 dependabot/pre-commit | 🔶 部分完成（agents/ 已入库、.gitignore 已补、dependabot 在 W1）；音乐外迁（D3）、docs 归档待做 |

## 二、执行阶段的新发现（当天，全部已修复）

1. **026 迁移角色操作需要超级用户**：`blog_user` 无 CREATEROLE，迁移在本地失败且事务干净回滚——角色/授权配置应移出 Alembic，作为 DBA 步骤。
2. **026 的生产级缺陷**：026 给 `review_items` 加了 `mistake_id NOT NULL`（外键+唯一索引+回填），但 ORM 模型没有该列——**任何升到 026 的数据库上复习项 INSERT 全部失败**。静态审查两轮都没发现，是真库 CI 抓出来的。已按迁移契约修模型并补创建点。
3. **LSR03 运行时契约**：守护脚本要求 `backend/.venv` 解释器，CI 已改为 venv 运行。
4. **教训**：「测试跑在迁移出来的库上」是有效的防回归护栏——建议按此扩展（W1 的 ruff/eslint/dependabot、W6+ 的覆盖率与集成测试）。

## 三、暑期重构路线复盘（6 条建议）

1. **先收割再开新线**：route-ownership R1–R5 的 "deferred cutover" 是已付费未兑付的最大回报——删除死树、收敛 manage、合并列表页（= W1）。
2. **撤销执行摘要的 jose/JWT 推荐**：其前提与现行会话契约矛盾，采纳会制造审计警告的"第二套认证"；PSS 的 session-state 方案才是正路。✅ 已在新路线冻结清单中作废。
3. **"完成的定义包含拆除"**：任何切换类工作项，验收必须含旧路径删除/归档。
4. **扩展今天的真实验证护栏**：CI 真库已证明有效，补 lint/dependabot/覆盖率（合计 <1 天）。
5. **LSR-03 要有明确结局**：排期生产窗口或正式归档，不要停在 "FAIL+未授权" 半挂起态（决策点 D1）。
6. **计划源收敛**：一份滚动活文档取代四份重叠报告与 104 个过程文件夹；小任务不建 workflow 五件套。✅ 已建立 `docs/roadmap-2026-09.md`。

## 四、UI 重构路线（5 条建议）

1. **视觉 token 从 PNG 落成代码**：VSC 停在"待批准"，editorial 语言只存在于 9 张参考图；先做 VSC-02/03（导航统一 + 浮层 a11y 合同），token 落 `theme.css`（W2）。
2. **UI 最大杠杆也是删除**：5 个列表页 ~1,000 行重复 + 760 行 manage/page.tsx vs (workspace) 双 UI 并行（W1）。
3. **编辑器收敛批准 Option A 但砍范围**：只做 capture/notes/mistakes 三编辑器的共享原语，不建 UnifiedEditor（W3）。
4. **渲染管线二选一**：生产旧渲染器 + 隔离 PoC 双轨是最差状态；执行 M7 提升，前置补 rehype-sanitize 白名单（D-05 缺口）（W4）。
5. **补上路线缺失的三块**：SEO（0/49 页 metadata）、a11y（291 按钮/114 aria-label、45 处 index key）、LCP 实测（RISK-PRA-001 挂了三周）→ Lighthouse 进 CI（W5）。

## 五、元建议（工作方法）

暑期路线验证了"门禁+独立审查"能防伪实现，但没防住"无限推迟收尾"。下一阶段改为**每周一条可部署的垂直薄片**，每片过 CI；不要再写 10–16 天的 Phase 1–4 大计划。

## 六、待你拍板的决策点

| # | 决策 | 建议 |
|---|------|------|
| D1 | 生产迁移 026 窗口 | 排期执行（需 CREATEROLE + 共享实例评估）或正式归档 LSR-03 |
| D2 | cmdk 统一创作面板 | 缓议（新功能非技术债；jose 条款已作废） |
| D3 | 24MB 音乐外迁 | 迁 CDN/R2，顺带解决版权暴露 |
| D4 | `reactStrictMode: false` | W2 后试点开启一轮，无副作用则常开 |
