# AI 配置、错题工作流与导航体验升级方案

版本: v0.1  
日期: 2026-06-05  
状态: 需求记录与初步方案，尚未进入实现  
关联域: `manage`、`auth`、`mistakes`、`write-mistake`、`write-note`、`notes`、`home`、shared navigation、AI service

## 1. 背景

本轮问题来自公网实际使用截图和交互反馈。当前系统已经具备笔记、博客、错题、复习、AI 分析和网站设置能力，但存在几个产品结构混乱点：

- 错题集页面复用了知识库侧栏，导致出现不符合错题场景的“全部内容”“收件箱”。
- 写错题存在两个入口: `/write-mistake` 和 `/write-note` 内部的“错题”类型。
- 写作页缺少明确返回按钮，左上角主栏点击语义不清。
- 设置页或设置弹窗依赖浏览器返回时，用户可能直接回到原始标签页或非预期页面。
- AI 能力没有统一的管理后台，无法可视化配置 API、供应商、OCR 模型、文本模型和系统提示词。
- 错题 AI 目前主要分析题目，不足以支持“题目 + 我的错误答案 + 错误答案图片”的联合分析。

本文件用于集中记录新一轮需求和初步设计，不代表已经实现。

## 2. 当前问题记录

### 2.1 管理后台缺少 AI API 可视化配置

用户需求:

- 管理后台需要账号密码登录。
- 登录后可以可视化配置 AI API。
- 支持选择不同供应商。
- 支持更换 OCR 识别模型。
- 支持更换文本生成模型。
- 支持更换系统提示词。

当前状态:

- 系统已有后端 JWT auth 概念。
- `/manage` 已有内容管理和网站设置方向。
- AI 配置目前分散在后端环境变量、服务代码或接口参数中，没有统一可视化配置中心。

问题影响:

- 切换模型需要改环境或代码。
- OCR 与文本生成没有独立配置。
- 本地模型、自定义 OpenAI-compatible provider 不易接入。
- 系统提示词无法由用户直接调整。

### 2.2 错题集页面出现“收件箱”和“全部内容”

用户反馈:

- `/mistakes` 页面为什么会有“收件箱”和“全部内容”。
- 这些词不符合错题集语义。

当前根因:

- `/mistakes` 页面复用了 `src/app/notes/components/knowledge-sidebar.tsx`。
- `KnowledgeSidebar` 的基础 navItems 包含:
  - 全部内容
  - 收件箱
  - 笔记
  - 博客
  - 错题
- 即使 `/mistakes` 传入 `contentTypes={['mistake']}`，`全部内容` 与 `收件箱` 因没有 `type` 字段仍然会显示。

结论:

- 当前错题集页面侧栏是知识库侧栏的复用结果，不是错题专属导航。
- 错题页面应改成错题专属筛选侧栏或错题专属模式。

### 2.3 左侧导航栏不清楚

用户反馈:

- 导航栏图标语义不明确。
- 展开前不知道每个按钮是什么。
- 在不同页面中，当前状态与跳转意义不清晰。

当前状态:

- 左侧全局 `VerticalNav` 是图标优先的收缩导航。
- 图标按钮虽有 `aria-label` 和 `title`，但视觉层面仍不够明确。
- `/notes`、`/mistakes` 页面同时有全局导航与页面内侧栏，容易造成“两个导航系统”的冲突。

设计方向:

- 全局导航负责页面级跳转。
- 页面内侧栏只负责当前页面内筛选。
- 错题页面内侧栏不再出现笔记/博客/收件箱这类知识库词汇。
- 收起态需要 hover tooltip 或更明确的展开行为。
- 当前页面高亮必须按 `pathname` 精确计算。

### 2.4 写错题存在两个页面/入口

用户反馈:

- “写东西”页面里写错题有两个页面。
- 实际返回结果不是前面方案描述的那个。

当前真实入口:

- `/write-mistake`: 专门添加错题页面，包含 AI 分析错题区域。
- `/write-note`: 写笔记页面，内部仍有类型 tab: `笔记 / 博客 / 错题`，选择“错题”后也能创建错题。

问题影响:

- 同一个“写错题”能力被两个页面承载。
- `/write-note` 内的错题表单与 `/write-mistake` 的 AI 错题助手能力不一致。
- 用户不知道应该从哪个页面写错题。
- 后续增强“错误答案图片分析”时，如果保留双入口，需要维护两套表单。

建议决策:

- `/write-mistake` 作为唯一新增错题入口。
- `/write-note` 仅保留 `笔记` 与 `博客`。
- 若暂时保留 `/write-note` 的“错题”按钮，则点击后直接跳转 `/write-mistake`，不在 `/write-note` 内部渲染错题表单。

### 2.5 写作页左上角主栏无明显返回效果

用户反馈:

- `/write-note` 页面点击左上角主栏无反应，不返回主页面。
- 该页面没有返回键。

当前状态:

- 写作页左上角显示 mini `NavCard`，视觉上主要是头像。
- 头像 Link 理论上指向 `/`，但缺少明确文字和点击反馈。
- 页面标题区域没有“返回笔记/返回错题集/返回首页”的明确按钮。
- 底部有“取消”按钮，但位置太靠后，不适合作为页面级返回。

设计方向:

- 写作页顶部增加明确返回按钮。
- `/write-note` 返回 `/notes`。
- `/write-mistake` 返回 `/mistakes`。
- 编辑已有内容时，返回到对应详情页或列表页，需要后续按路由细分。
- 左上角 mini 主栏仍可保留“返回首页”语义，但不能作为唯一返回入口。

待确认变更:

- 曾误操作修改过 `src/components/nav-card.tsx`，将写作页 mini 主栏从头像改成“头像 + 首页”。该改动尚未作为正式需求实现确认，应在后续实现前决定保留、调整或回退。

### 2.6 设置页浏览器返回行为异常

用户反馈:

- 在设置页点击 Chrome 返回直接回到原始标签页。
- 需要解决设置页面的返回行为。

当前可能根因:

- 网站设置既存在首页弹窗入口，也存在 `/manage` 内联设置入口。
- 弹窗打开/关闭与浏览器历史没有清晰映射。
- `/manage` tab 切换如果没有 URL 状态，浏览器返回无法回到上一个 tab，只会回到上一个页面。

设计方向:

- `/manage` 的 tab 状态进入 URL query。
- 推荐 URL:
  - `/manage?tab=content`
  - `/manage?tab=music`
  - `/manage?tab=recommendation`
  - `/manage?tab=settings`
  - `/manage?tab=ai`
- 首页设置弹窗不写浏览器历史。
- `/manage` 设置页作为真实管理页面，支持浏览器返回。
- 保存设置后不自动跳转，只 toast 提示。

### 2.7 错题需要“错误答案分析”

用户需求:

- 先输入题目。
- 再输入我的错误答案。
- 错误答案支持图片上传。
- AI 结合题目和错误答案一起分析。

当前状态:

- `/write-mistake` 已有题目文本粘贴和题目图片上传。
- 表单有 `my_answer` 字段。
- 当前 AI 分析主要围绕题目，不明确区分“题目图片”和“错误答案图片”。

设计方向:

- 将错题 AI 输入拆成两组:
  - 题目输入: 题目文本 + 题目图片
  - 错误答案输入: 错误答案文本 + 错误答案图片
- AI 输出结构应包含:
  - 题目识别结果
  - 我的错误答案识别结果
  - 正确答案
  - 错误原因
  - 错误思路分析
  - 正确解法
  - 关键步骤
  - 知识点
  - 易错点
  - 变式训练
  - 复习建议

## 3. 目标信息架构

### 3.1 全局导航

全局导航只做页面跳转:

- 首页
- 近期文章
- 笔记
- 错题集
- 关于网站
- 推荐分享
- 优秀博客
- 网站设置

要求:

- 图标按钮必须有可见解释路径: 展开态文字或 hover tooltip。
- 当前页面高亮必须准确。
- 写笔记页和编辑笔记页高亮“笔记”。
- 写错题页高亮“错题集”。
- 网站设置入口语义独立，不再和 My Blog/首页入口混淆。

### 3.2 笔记页侧栏

`/notes` 侧栏可以继续使用知识库语义:

- 全部内容
- 收件箱
- 笔记
- 博客
- 文件夹
- 标签

可选:

- 是否继续显示“错题”筛选需要重新评估。若错题已经独立为 `/mistakes`，`/notes` 默认不应把错题混在笔记列表里。

### 3.3 错题页侧栏

`/mistakes` 侧栏应改成错题语义:

- 全部错题
- 待复习
- 今日到期
- 已掌握
- 按科目
- 按难度
- 按标签

不应显示:

- 全部内容
- 收件箱
- 笔记
- 博客

## 4. 管理后台 AI 配置设计

### 4.1 入口

新增 `/manage?tab=ai`，或在 `/manage` 的“网站设置”下新增二级 tab “AI 配置”。

建议:

- `/manage?tab=ai` 独立一级 tab。
- 因为 AI 配置涉及密钥、模型和服务测试，重要性高于普通网站设置。

### 4.2 认证

要求:

- 仅管理员可访问和修改。
- 使用后端 JWT。
- 登录入口应清楚显示为“管理登录”。
- API Key 不允许前端明文回显。

### 4.3 配置项

供应商:

- OpenAI-compatible
- DeepSeek
- Gemini
- Local
- Custom

通用字段:

- provider name
- base_url
- api_key
- text_model
- vision_model
- ocr_model
- embedding_model
- enabled

提示词:

- 错题分析系统提示词
- 错误答案分析提示词
- OCR 后处理提示词
- 笔记写作提示词
- 知识库整理提示词

测试:

- 测试文本生成
- 测试 OCR
- 测试错题分析

### 4.4 后端存储建议

新增模型可命名为 `AIProviderConfig` 或 `AIConfig`。

字段建议:

```text
id
name
provider
base_url
api_key_encrypted
text_model
vision_model
ocr_model
embedding_model
system_prompts
is_default
is_enabled
created_at
updated_at
```

安全要求:

- API Key 加密存储。
- 列表接口只返回脱敏 key。
- 修改接口要求 admin。
- 不把 key 写入前端 localStorage。

## 5. 错误答案分析流程

### 5.1 新增输入结构

`/write-mistake` 顶部 AI 区域拆成:

1. 题目区
   - 题目文本
   - 题目图片上传

2. 我的错误答案区
   - 错误答案文本
   - 错误答案图片上传

3. AI 操作区
   - 识别题目
   - 分析错误答案
   - 生成完整解析
   - 生成知识点
   - 生成复习计划

### 5.2 请求接口建议

新增或扩展:

```text
POST /api/ai/analyze-mistake
```

请求结构:

```json
{
  "question_text": "...",
  "wrong_answer_text": "...",
  "question_images": [
    { "base64": "...", "mime_type": "image/png" }
  ],
  "wrong_answer_images": [
    { "base64": "...", "mime_type": "image/png" }
  ],
  "subject": "数学",
  "difficulty": "medium",
  "provider_config_id": "optional"
}
```

响应结构:

```json
{
  "title": "...",
  "question": "...",
  "my_answer": "...",
  "correct_answer": "...",
  "analysis": "...",
  "error_reason": "...",
  "wrong_thinking": "...",
  "key_step": "...",
  "knowledge_points": "...",
  "similar_traps": ["..."],
  "variant_questions": ["..."],
  "review_advice": "...",
  "subject": "...",
  "difficulty": "medium",
  "tags": ["..."]
}
```

### 5.3 保存字段

现有字段继续保留:

- `question`
- `my_answer`
- `correct_answer`
- `analysis`
- `knowledge_points`
- `ai_metadata`

后续可考虑将以下字段一等化:

- `error_reason`
- `wrong_thinking`
- `key_step`
- `review_advice`

## 6. 阶段拆分

### P0: 记录和导航结构修复

目标: 先解决看得见的混乱，不引入新后端模型。

任务:

- 记录本文件。
- 明确 `/mistakes` 不应复用普通知识库侧栏的“全部内容/收件箱”文案。
- 规划错题专属侧栏。
- 明确 `/write-mistake` 是唯一新增错题入口。
- 规划 `/write-note` 移除或跳转“错题”类型。
- 规划写作页顶部返回按钮。
- 规划设置页 URL query tab。

验收:

- 文档明确所有问题与根因。
- 后续实现者能按本文件拆分任务。

### P1: UI 与路由体验实现

目标: 修正错题集、写作页和设置页的导航体验。

任务:

- `/mistakes` 使用错题专属侧栏或 `KnowledgeSidebar` 的 `mode='mistake'`。
- `/write-note` 不再内部创建错题。
- `/write-mistake` 保持唯一新增错题页。
- 写作页添加顶部返回按钮。
- 左侧全局导航增加更清晰的 hover/展开说明。
- `/manage` tab 使用 URL query。

验收:

- 错题集不显示“全部内容/收件箱/笔记/博客”。
- 从 `/notes` 点击写入只进入写笔记。
- 从 `/mistakes` 点击添加只进入 `/write-mistake`。
- `/write-note` 可明确返回 `/notes`。
- `/write-mistake` 可明确返回 `/mistakes`。
- Chrome 返回在 `/manage` tab 之间行为可预期。

### P2: AI 配置中心

目标: 管理后台支持 AI 供应商、模型、OCR 和提示词配置。

任务:

- 新增后端 AI 配置 schema/model/router/service。
- 新增 `/manage?tab=ai` UI。
- 支持 provider/base_url/api_key/model/prompt 配置。
- 支持测试连接。
- API Key 脱敏回显。

验收:

- 登录管理员后可配置 AI。
- 可切换文本模型和 OCR 模型。
- 可配置自定义 provider。
- 测试连接失败不阻断页面。

### P3: 错误答案联合分析

目标: 错题 AI 支持题目与错误答案一起分析。

任务:

- `/write-mistake` 拆分题目输入与错误答案输入。
- 支持错误答案图片上传。
- 后端分析接口支持 `question_images` 与 `wrong_answer_images`。
- AI prompt 输出错误思路、错误原因、正确解法、知识点和复习建议。

验收:

- 输入题目文本 + 错误答案文本可生成分析。
- 上传题目图片 + 错误答案图片可生成分析。
- 分析结果自动填入错题表单。
- 保存后详情页能展示错误答案分析。

## 7. 实现注意事项

### 7.1 架构边界

遵守 `AGENTS.md`:

- 前端页面组件只做页面组合。
- API 调用放入 `src/lib/api/*`。
- 后端 router 保持 thin。
- AI 供应商逻辑放入 `backend/app/services/`。
- 后端配置变更需要 schema/model/migration/API client 同步。

### 7.2 安全

- 管理登录使用 JWT。
- API Key 不进入前端持久存储。
- API Key 不写入公开静态文件。
- 不将 AI 配置导出到 RSS、sitemap 或公开内容。

### 7.3 需要避免

- 不要继续让 `/write-note` 和 `/write-mistake` 两套页面都维护错题创建。
- 不要让错题页继续展示“收件箱”这类笔记整理词。
- 不要把浏览器返回作为唯一导航方式。
- 不要把 AI provider 的 key 明文返回给前端。

## 8. 待确认问题

1. `/write-note` 的“错题”tab 是直接删除，还是点击后跳转 `/write-mistake`？
2. `/notes` 是否还允许筛选和展示 `type=mistake` 的内容？
3. AI 配置中心放在 `/manage?tab=ai`，还是放在 `/manage?tab=settings` 内的二级 tab？
4. API Key 加密使用哪种方案: 环境密钥对称加密、系统 keychain，还是暂时仅本地开发存储？
5. 错误答案图片是否和题目图片共用 `images` 字段，还是新增 `question_images` / `wrong_answer_images` 元数据？
6. 是否新增独立错题详情路由 `/mistakes/{slug}`？

## 9. 当前非实现说明

本文件只整合需求和方案，不代表相关功能已完成。

已知存在一个待确认代码变更:

- `src/components/nav-card.tsx` 曾被误操作调整写作页 mini 主栏显示。后续实现前需要确认保留或回退。
