# I4 计划：学习首页状态与统一导航收口

## 目标

完成一个可恢复、权限不退化的学习管理入口：管理员能理解首页的今日任务与局部数据问题，且桌面/移动导航准确反映已经交付与仍属后续的能力。

## 允许范围

- `src/app/manage/(workspace)/dashboard/**`、`src/app/manage/components/manage-sidebar.tsx` 及其必要共享展示组件/测试。
- `src/lib/api/dashboard.ts`、`backend/app/schemas/dashboard.py`、`backend/app/services/dashboard_service.py`、`backend/app/routers/dashboard.py`，但仅在实现摘要状态契约所需时修改。
- 本工作区的设计、任务、验证和进度记录。

## 不做

- I5 的资料、品牌、时区和首页偏好。
- 新的学习领域模型、Alembic migration、OCR/AI 成功调用、文件工作区、部署、源库写入、权威切换或旧系统停写。

## 前置与停止条件

- 前置：I3 已在隔离恢复环境通过并已清理；当前源库和生产状态不在本轮范围。
- 停止：若为局部状态需改变领域数据模型或 migration；若旧入口盘点发现无法安全兼容的未知写入口；若公开页面受到管理端改动影响；若任何匿名请求得到私有摘要。

## 验收

1. 定向单测覆盖 loading、summary 失败、局部 unavailable、empty 与导航能力状态。
2. TypeScript、相关后端测试/启动检查与生产构建通过。
3. 独立恢复数据库和独立生产构建中：匿名 401、管理员成功、空态、局部失败、桌面/移动三种尺寸和键盘导航均有浏览器证据。
4. 临时环境停止并移入废纸篓；记录 C-04/C-05 的 PASS、PARTIAL 或 BLOCKED，不推导生产发布。
