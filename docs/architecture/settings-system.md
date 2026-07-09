# Settings System 设置系统

> 状态：拟新增；设置不能绕过权限与业务安全底线。

## 职责

管理 General、Learning、Review、AI、OCR、Upload、Drafts、Jobs、Privacy 和 Subjects 的系统参数、功能开关与默认行为。

## 核心表

`settings`、`review_settings`、`ai_settings`、`ocr_settings`、`upload_settings`、`job_settings`、`privacy_settings`、`subject_review_settings`、`setting_change_logs`。

设置应有显式 schema、类型、作用域、默认值、版本和验证规则，不能以任意 key/value 绕过契约。科目设置只能覆盖允许的全局字段。

第一版不新增 `learning_settings` 或 `draft_settings`：

- Learning 配置统一存入 `settings(namespace='learning')`。
- Drafts 配置统一存入 `settings(namespace='drafts')`。

命名空间内的 key 和 value 仍必须经过服务端类型化 schema 校验；使用通用 `settings` 表不等于允许任意未定义配置。

## 安全边界

API Key 不明文保存数据库；数据库只保存 `api_key_ref`，真实密钥来自环境变量或服务端密钥系统。日志不得记录密钥值。生产环境不得通过设置启用 `AUTH_BYPASS=true AND AUTH_BYPASS_ALLOW=true`。

页面：`/manage/settings` 及 `/review`、`/ai`、`/ocr`、`/upload`、`/drafts`、`/jobs`、`/privacy` 子页。

## 第一版范围

`settings` 的 Learning/Drafts 命名空间、必要的 Review 设置、表单校验、变更日志、默认值和科目级复习覆盖。其他专用设置表按真实复杂度后续启用。

## 暂缓范围

多用户配置继承、复杂策略语言、远程密钥托管 UI 和自动实验平台。
