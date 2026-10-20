# Tasks: 稳定性修复 — 部署链路、图片存储、错题编辑、解析体验、文本渲染

**版本**: v1.2
**日期**: 2026-06-07
**来源**: requirements.md, design.md
**状态**: 已部署公网（等待用户最终验收）

## P0-1: 图片存储/展示

- [x] **P0-1-01** 后端 `config.py` 新增 `IMAGE_BASE_URL` 配置项
- [x] **P0-1-02** 后端上传接口返回完整 URL
- [x] **P0-1-03** 前端 `config.ts` 新增 `IMAGE_BASE_URL`
- [x] **P0-1-04** 新建 `resolveImageUrl()` 工具函数
- [x] **P0-1-05** 详情页和编辑页使用 `resolveImageUrl()` 渲染图片
- [x] **P0-1-06** 新增 FastAPI `/images` 静态文件挂载
- [x] **P0-1-07** `IMAGE_BASE_URL` 未配置时 fallback
- [x] **P0-1-08** 公网图片可访问验证（curl 返回 200；用户最终验收待确认）

## P0-2: 错题编辑模式

- [x] **P0-2-01** 提取 `mistake-form.tsx` 共享表单组件
- [x] **P0-2-02** 新建 `/write-mistake/[slug]` 编辑路由
- [x] **P0-2-03** 编辑模式保存调用 `updateNote()`
- [x] **P0-2-04** 编辑模式图片管理（已有图片回填 + 增删）
- [x] **P0-2-05** 编辑模式 `ai_metadata` 保留
- [x] **P0-2-06** 更新编辑入口链接
- [x] **P0-2-07** 更新 `content-routes.ts` 中错题编辑路径

## P0-3: Markdown + LaTeX 统一渲染

- [x] **P0-3-01** 新建 `RichText` 组件
- [x] **P0-3-02** `StudyBlock` 改用 `RichText` 渲染
- [x] **P0-3-03** 复习页改用 `RichText` 渲染
- [x] **P0-3-04** AI prompt 增加 LaTeX 规范
- [x] **P0-3-05** 构建验证（`tsc --noEmit` 零错误 + `build:cf` 成功）

## P1: AI 解析结构化图示

- [x] **P1-01** `AnalyzeResponse` 新增 `diagrams` 字段
- [x] **P1-02** AI prompt 增加 diagram 输出规则
- [x] **P1-03** 详情页集成 `MermaidBlock` 渲染 diagrams

## P2: 部署脚本规范化

- [x] **P2-01** `wrangler.toml` 确认 `workers_dev = true`（已存在）
- [x] **P2-02** `package.json` 新增 `deploy:full` 脚本
