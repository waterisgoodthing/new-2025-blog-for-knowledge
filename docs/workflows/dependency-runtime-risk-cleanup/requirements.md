# 需求文档：Dependency And Runtime Risk Cleanup

## 背景

2026-07-17 公网部署后的只读检查发现：当前 Next.js 版本 `16.0.10` 命中多个已公开安全公告，且不满足 `@opennextjs/cloudflare@1.20.1` 的 Next.js peer dependency 范围。生产依赖审计仍有 4 项漏洞，构建还提示旧 compatibility date、过期浏览器映射数据和 Node 弃用 API。

## 用户与运维角色

- 站点访客：需要继续访问公开首页、博客、笔记和错题页面。
- 管理员：需要继续访问受保护的管理和编辑流程。
- 发布执行者：需要获得可复现、可审计、只使用已验证源代码的部署证据。

## 需求

### REQ-DRC-01 Next.js 安全版本与 OpenNext 契约

- 输入：当前 `package.json`、`package-lock.json`、OpenNext peer dependency 和 npm audit 结果。
- 处理：将 Next.js 升级到 OpenNext 支持且覆盖当前公告修复范围的稳定版本；保持 React/React DOM 和 OpenNext 兼容。
- 输出：`npm ls` 不再报告 Next.js peer invalid；`npm audit` 不再报告由当前 Next.js 版本引入的 high/medium 项。
- 失败处理：若升级引发构建、路由、认证或公开页面回归，停止部署并记录风险，不强行兼容。

### REQ-DRC-02 生产传递依赖风险

- 输入：`dompurify`、`undici`、`postcss` 的依赖树和实际 bundle 可达性。
- 处理：优先升级直接父依赖；只有在兼容性证据充分时才使用受控 override，禁止无审查的大范围强制修复。
- 输出：`npm audit --omit=dev` 的生产漏洞清单归零，或每项剩余风险有明确可达性、缓解措施和审批记录。
- 失败处理：无法安全升级时保留当前版本，生成单独风险决策，不伪造“已清理”。

### REQ-DRC-03 开发依赖审计

- 输入：`js-yaml` 等仅开发依赖的 audit 项。
- 处理：区分构建期风险与公网运行时风险，采用最小升级或明确接受记录。
- 输出：`npm audit` 与 `npm audit --omit=dev` 的差异可解释。
- 失败处理：若依赖被生产 bundle 间接包含，重新归类为 REQ-DRC-02。

### REQ-DRC-04 Cloudflare Runtime 兼容性维护

- 输入：当前 `compatibility_date = 2025-03-25`、Cloudflare compatibility flags 变更说明和构建/运行回归结果。
- 处理：单独评估是否更新 compatibility date；若更新，先在隔离环境构建、预览和验证，再发布。
- 输出：明确“保持旧日期并接受”或“更新日期并通过回归”的决策。
- 失败处理：更新后出现运行时行为变化时回退该配置变更，不与依赖升级混成无法审查的大 diff。

### REQ-DRC-05 构建警告收敛

- 输入：`baseline-browser-mapping`、Node `DEP0205`、npm deprecated package warnings。
- 处理：区分信息性提示、工具链弃用和实际生产故障；只处理能够验证收益的项。
- 输出：构建日志中每项警告都有状态：已清理、非阻塞已接受或另立任务。

## 非功能要求

- 安全：不得降低后端权限校验，不得启用 `AUTH_BYPASS`。
- 兼容：公开路由、管理路由、legacy redirects 和 API client 行为保持不变。
- 可回滚：每次升级使用独立提交，可回到当前公网已知版本。
- 可审计：记录依赖树、audit 输出、测试、构建、预览和公网验证证据。
- 数据安全：不执行 migration、DDL、DML，不改变数据库数据。

## 范围外

- 后端 Python 依赖升级，除非另立任务并获得批准。
- 数据库、业务模型和 API contract 调整。
- AI/OCR/Capture、Search、Analytics、Practice、BKT。
- 公共站点 UI 重构和新功能。

## 验收标准

1. 依赖版本满足 OpenNext peer contract，且生产 audit 结果达到预设门槛。
2. `npm test`、TypeScript check、生产 build 和 Cloudflare build 全部通过。
3. 匿名公开路由仍返回成功，私有管理入口仍受保护。
4. 预览和公网验证不出现新增 4xx/5xx、RSC 错误或 API 配置错误。
5. 数据库 revision 和基线数量/关键 ID 不变。
