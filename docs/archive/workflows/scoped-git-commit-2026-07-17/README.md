# Scoped Git Commit Task Group

## Goal

审计当前混合工作区，明确本轮允许进入 Git 提交的文件范围，并在用户批准任务清单后完成精确暂存、验证和提交。

## Touched Domains

- backend personal learning system: models, schemas, routers, services, migrations, tests
- frontend manage workspace UI and API clients
- architecture and workflow documentation
- Git commit scope only; no deployment or push by default

## Current Status

- Status: planning; approval required before staging or committing.
- Branch: `notes-workspace-ux-upgrade`.
- Worktree: mixed and substantially dirty; unrelated or separately owned changes must remain unstaged.
- Remote relation: local branch is ahead of `mine/notes-workspace-ux-upgrade` by one commit.

## Workflow Files

- [design.md](design.md)
- [requirements.md](requirements.md)
- [tasks.md](tasks.md)
- [validation.md](validation.md)
- [diff-report.md](diff-report.md)

## Explicit Non-Goals

- 不执行数据库迁移。
- 不修改业务代码以“顺便修复”审计发现。
- 不使用 `git add -A` 或 `git commit -am`。
- 未经单独授权不执行 push、部署、创建 PR 或改写历史。
