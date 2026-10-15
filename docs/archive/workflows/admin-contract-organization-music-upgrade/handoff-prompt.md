# Handoff Prompt

You are taking over the completed workflow in:

`docs/workflows/admin-contract-organization-music-upgrade/`

## Status

All phases (0-11) are COMPLETE. All P0 and P1 tasks have been implemented and validated.

## What Was Built

### Authentication System
- HttpOnly cookie sessions with server-side revocation
- Passkey and password auth levels with different permissions
- CLI tools for passkey registration/reset and password management
- Passkey-only areas: page settings, security settings, Apple Music config

### Unified Manage Console
- 9 tabs: 总览, 内容管理, 文件夹与标签, 音乐管理, AI 管理, 页面设置, 安全设置, 同步部署, 操作记录
- Passkey-only tabs gated with lock icon
- Full audit log viewer with pagination

### Content Organization
- Safe folder delete (promotes children, moves content to inbox)
- Folder nesting with max depth 4 validation
- Tag rename/merge/delete with association preservation
- Context menus on folders and tags in KnowledgeSidebar
- Content context menus with admin-gated actions

### NetEase Music Daily Song
- Candidate pool sync from configurable artist sources
- Daily song generation from candidate pool
- Public music page with preview playback and hover cards
- Full management interface with config, sync, candidates, history

### AI Management
- Config status dashboard (AI/DashScope/DeepSeek)
- Feature list overview
- AI test entry with streaming response
- Admin session required for all AI calls

### Weak-Point Diagnosis
- "薄弱点诊断" module replacing flat weak-point list
- Severity classification (high/medium/low)
- Collapsible clusters with evidence links
- Action buttons: start review, copy knowledge point

## Deployment Notes

1. Run Alembic migrations: 006 (sessions), 007 (folder FK), 008 (audit), 009 (music daily)
2. Set AUTH_BYPASS=false for production
3. Configure JWT_SECRET_KEY to a strong random value
4. Register passkey via CLI: `python -m app.cli register-passkey`
5. Optionally set admin password: `python -m app.cli set-password`
6. Deploy NetEaseCloudMusicApi service for music features
7. Configure AI API keys for AI features

## Validation Commands

```bash
npx tsc --noEmit
cd backend && .venv/bin/python3 -c "from app.models import *; print('OK')"
cd backend && .venv/bin/python3 -c "from app.routers.music_manage import router; print('OK')"
```
