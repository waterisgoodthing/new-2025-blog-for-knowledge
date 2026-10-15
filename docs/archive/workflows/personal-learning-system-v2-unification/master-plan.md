# Personal Learning System V2 统一大方案

版本：Draft 1.0（融合稿）
日期：2026-07-20
状态：`I0 APPROVED BASELINE / IMPLEMENTATION NOT AUTHORIZED`

## 1. 一句话愿景

将现有博客、笔记、题目、错题、复习、附件、项目和发布能力收敛为一个以个人学习闭环为主线的工作台：

```text
采集 → 整理 → 建立知识关系 → 学习/练习 → 发现错误 → 复习 → 总结 → 选择性发布
```

## 2. 成功边界

本方案分为四个层次，禁止混为一个完成状态：

1. **核心 MVP**：人工维护的题目、错题、复习和附件闭环。
2. **产品化 v1**：统一导航、今日工作台、动态资料、稳定的公开/管理体验。
3. **长期工作区**：文件系统、Markdown、WikiLink、反向链接、搜索、版本和治理。
4. **迁移与生产收口**：旧系统盘点、dry-run、切换、观察期和 Legacy 归档。

## 3. 产品信息架构

```text
Personal Learning Space
├── 今日
├── 采集
├── 学习
│   ├── 题目
│   └── 错题
├── 复习
├── 知识库
│   ├── 收件箱
│   ├── 笔记
│   ├── 文件
│   ├── 知识点
│   └── 搜索
├── 项目
├── 发布
│   └── 博客
├── 管理工作区
│   ├── 草稿审核
│   ├── OCR 与 AI
│   ├── 任务队列
│   ├── 附件中心
│   ├── 数据分析
│   ├── 迁移台账
│   └── 系统健康
└── 设置
```

管理工作区是管理员专用；公开博客、笔记和已发布错题继续保持公开读取边界，不因产品化而整体加 AuthGate。

## 4. 首页工作台

首页以今日行动为中心，默认展示：

1. 今日目标和快速捕获
2. 到期复习和最近错题
3. 待处理草稿/采集
4. 最近笔记和文件
5. 最新文章和项目
6. 最小学习摘要

模块可排序、隐藏和恢复默认，但必须有固定默认布局、模块数量上限、移动端降级和局部失败状态。首页只编排摘要，不拥有题目、错题、复习、项目或 AI 的领域写入逻辑。

## 5. 个人资料与品牌

欢迎语、显示名称、身份标题、签名、头像、站点名称、副标题、时区和首页偏好均由设置数据驱动。动态问候按用户时区计算；匿名公开页面不得请求或暴露管理员私有资料。

首版只支持当前单管理员模型，不扩展多用户、共享空间或 RBAC。

## 6. 文件与知识工作区

文件工作区统一组织文件夹、Markdown 内容、附件和跨域资源引用，但不取代业务领域实体。

首个可验收切片：

```text
文件夹树 → 上传 → 私有访问 → 预览 → 移动/重命名 → 回收站 → 恢复
```

后续再增加：版本历史、全文搜索、标签、属性、WikiLink、反向链接、导入导出和命令面板。

所有资源使用稳定 ID 与显示路径分离；移动和重命名不能破坏内部链接。附件采用临时对象、哈希校验、正式对象切换和数据库记录的事务流程。

## 7. 学习闭环

首版必须保持：

```text
Subject / Knowledge Point
        ↓
Question Draft → Question → Practice Attempt
                              ↓
                         Mistake Draft → Mistake
                                             ↓
                                        Review Item
                                             ↓
                                        Review Record
```

AI、OCR 和 Capture 失败时，用户仍可手工完成闭环。BKT、复杂掌握度、自适应出题和复杂报告不进入首版强制范围。

## 8. AI、OCR 与草稿审核

自动化输出必须遵循：

```text
generated → pending_review → accepted / rejected
```

每项输出记录来源、版本、置信度、警告、关联对象和 AI Run ID。AI 不直接修改正式知识库；公开页面只能展示已确认内容，不提供重新生成等管理员操作。

## 9. 公开、管理和存储边界

```text
公开读取：/api/public/** → published + public + 未删除
管理员操作：/api/admin/** → JWT + get_current_admin
私有附件：默认管理员可读，公开需显式发布
治理操作：AI、任务、备份、迁移、审计仅管理员
```

旧 `/write-*`、`/mistakes/review` 等兼容路由在迁移期保留并遵守认证规则，不能静默删除或把旧 `Note(type="mistake")` 当作已完成迁移。

### 9.1 API 过渡原则

`/api/public/**` 和 `/api/admin/**` 是目标分层，不是对当前端点的即时重命名。Phase 0 必须先形成端点清单与兼容矩阵：当前路径、目标路径、字段映射、可见性、认证、调用方、契约测试、观测窗口和退役决定。未完成矩阵前，既有公开读取端点按其当前已验证的可见性规则继续服务。

## 10. 迁移治理

迁移范围包括旧博客、笔记、题目、错题、复习、草稿、留言、图片、PDF、Office 文件、项目资料、附件记录、关系和旧路径。

每条记录必须进入以下终态之一：

```text
MIGRATED | MERGED | ARCHIVED | QUARANTINED | REJECTED_WITH_REASON
```

阶段为：

```text
盘点 → 映射 → 只读 dry-run → 影子迁移 → 增量同步 → 权威切换 → 观察期 → 归档
```

在备份恢复、附件恢复、schema authority、冲突清单和公开/管理路由验收完成前，Migration Gate 保持 `BLOCKED`。

## 11. 统一阶段计划

### Phase 0：冻结与审计

冻结术语、权限、数据源、路由、owner、备份恢复和 schema authority。

### Phase 1：学习 MVP

完成科目、知识点、题目、错题、复习的最小人工闭环。

### Phase 2：产品化壳层

完成统一导航、今日首页、动态资料、移动端导航、状态文案和视觉变量。

### Phase 3：采集与附件

完成私有附件、单文件 OCR、Capture 和统一草稿闸门。

### Phase 4：知识与文件基础

完成文件树、预览、移动、回收站、Markdown、版本和稳定资源引用。

### Phase 5：搜索与治理

完成结构化/全文搜索、AI Run、草稿审核、任务状态和附件中心。

### Phase 6：统计与设置

只根据真实数据增加学习统计、报告、设置和项目聚合。

### Phase 7：迁移准备

完成只读盘点、映射、哈希、冲突和 dry-run；不切换任何正式读写权威来源。dry-run 只能在已达到 `DRY_RUN_READY` 的隔离目标环境写入，不能接触生产主库、生产附件、旧写入口或公开路由。

### Phase 8：切换与归档

获得单独批准后执行影子迁移、增量同步、权威切换、观察期和 Legacy 归档。

## 12. 最终完成定义

```text
MVP Learning Loop:       PASS
Productized UI:          PASS
Knowledge Workspace:     PASS
AI / OCR Governance:     PASS
Backup / Recovery:       PASS
Migration Dry Run:       PASS
Authority Switch:        APPROVED AND VERIFIED
Legacy Writes:           DISABLED
Legacy Archive:          COMPLETE
Production Readiness:    PASS
```

任何一项没有对应证据，都必须保持 `PARTIAL`、`BLOCKED`、`UNKNOWN` 或 `NOT VERIFIED`，不能用设计文档代替实现和验收。
