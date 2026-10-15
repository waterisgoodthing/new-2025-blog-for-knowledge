# Validation

## Status

All phases (0–7) implemented and validated. Browser validation completed on 2026-06-12.

## Frontend Validation

- **`npx tsc --noEmit`**: 0 errors (verified 2026-06-12).
- All modified files compile cleanly.
- New files compile cleanly: `discover/page.tsx`, `guestbook/page.tsx`, `lib/api/guest-messages.ts`.

## Backend Validation

- `from app.models.guest_message import GuestMessage, GuestMessageBan`: OK
- `from app.schemas.guest_message import GuestMessageCreate, GuestMessageOut`: OK
- `from app.routers.guest_messages import router`: OK
- `from main import app`: OK, 108 routes loaded.
- New router registered: `guest_messages.router` at `/api/guest-messages`.

## Browser Validation

Performed on 2026-06-12 with dev server on `:2025` and backend on `:8000`.

### Verified

| Item | Route | Result |
|------|-------|--------|
| 首页 nav-card 分组 | `/` | `公开内容`(博客/笔记/错题) + `互动探索`(发现/留言/关于) + `管理`底部弱化 ✅ |
| Desktop vertical-nav | `/blog` (内页) | 展开后分组容器+管理底部 ✅ |
| `/manage` 匿名态 | `/manage` | 头像+品牌+描述+登录表单+快捷公开链接 ✅ |
| `/discover` 页面 | `/discover` | 标题+tab+搜索+空状态+底部闭环链接(博客/笔记/错题/留言板) ✅ |
| `/guestbook` 提交流程 | `/guestbook` | 填写→提交→消息出现列表顶部→表单重置 ✅ |
| `/guestbook` 回链 | `/guestbook` | home→`/`, blog(无slug)→`/blog`, mistake/ipv4→`/notes/ipv4` ✅ |
| `/about` 闭环链接 | `/about` | 回到首页/发现/博客/笔记/留言 ✅ |
| `/share` 重定向 | `/share` | → `/discover?tab=shares` ✅ |
| `/bloggers` 重定向 | `/bloggers` | → `/discover?tab=bloggers` ✅ |
| 错题公开裁剪 | `/notes/ipv4` | 题目+正确答案+标签+图片 可见；我的答案/复习状态/错因解析/AI解析/关联知识/编辑按钮 全部隐藏 ✅ |
| 错题闭环链接 | `/notes/ipv4` | 发现更多/留言/回到首页 ✅ |
| 留言审核 API | POST/PUT/GET | 列出→按状态筛选→隐藏→恢复可见 ✅ |

### Limited

- **管理员登录态 UI**：浏览器因 `SameSite=Lax` cookie 跨域（`localhost` → `public-api.limengyang.me`）无法完成登录。manage 留言审核 tab 功能通过 API 全链路验证。
- **write-note sort_order 输入框**：因未登录被 AuthGate 重定向，通过源码确认字段存在于创建/编辑页。
- **移动端导航**：未在移动视口下验证，代码结构已对齐桌面端分组。

## Changed Files

### Modified

| File | Phase | Change |
|------|-------|--------|
| `src/components/vertical-nav.tsx` | P1-01 | Rebuilt with 公开内容/互动探索 groups, management demoted |
| `src/components/mobile-nav.tsx` | P1-02 | Aligned with same IA, 更多 sheet grouped |
| `src/components/nav-card.tsx` | P1-03 | Replaced GENERAL with 公开内容/互动探索, management at bottom |
| `src/app/(home)/share-card.tsx` | P1-04 | ShareCard link updated to `/discover` |
| `src/app/manage/page.tsx` | P2-01/02, P5-03 | Redesigned anonymous LoginForm + added 留言审核 tab with hide/restore moderation |
| `src/app/blog/[id]/blog-detail-content.tsx` | P3-01, P6-02 | Admin-gated edit button + closure links for non-admin |
| `src/app/notes/[id]/note-detail-content.tsx` | P3-02/03, P6-02 | Admin-gated buttons, limited public mistake view, closure links |
| `src/app/share/page.tsx` | P4-04 | Non-admin redirect to `/discover?tab=shares` |
| `src/app/bloggers/page.tsx` | P4-04 | Non-admin redirect to `/discover?tab=bloggers` |
| `src/app/about/about-content.tsx` | P6-04 | Added closure links to 首页/发现/博客/笔记/留言 |
| `src/app/guestbook/page.tsx` | P5-04 fix | Fixed attachment link logic: home→`/`, with slug→detail, without slug→list |
| `backend/app/schemas/guest_message.py` | P5-01 fix | Fixed `id` type from `str` to `uuid.UUID` for FastAPI serialization |
| `src/app/write-note/page.tsx` | P4-03 | Added `sort_order` field to form state and `createNote()` call |
| `src/app/write-note/[slug]/page.tsx` | P4-03 | Added `sort_order` field to form state, load from note, pass to `updateNote()` |
| `backend/app/schemas/note.py` | P4-02/03 | Added `sort_order` to NoteCreate, NoteUpdate, NoteOut, NoteListItem |
| `backend/app/routers/notes.py` | P4-02/03 | Added `featured`/`sort_by` params, pass `sort_order` in create_note |
| `src/lib/api/notes.ts` | P4-02/03 fix | Added `featured` and `sort_by` to NoteListParams |
| `backend/main.py` | P5-01 | Registered `guest_messages` router |
| `backend/app/models/__init__.py` | P5-01 | Added `GuestMessage`, `GuestMessageBan` exports |
| `docs/workflows/public-site-closure-upgrade/tasks.md` | P7-04 | Updated task status |

### Created

| File | Phase | Purpose |
|------|-------|---------|
| `src/app/discover/page.tsx` | P4-01/02/03 | Discover page with 推荐分享/优秀博客/优秀笔记 tabs |
| `src/app/guestbook/page.tsx` | P5-02/04 | Public guestbook with submission, display, closure |
| `src/lib/api/guest-messages.ts` | P5-02 | Frontend API client for guest messages |
| `backend/app/models/guest_message.py` | P5-01 | GuestMessage + GuestMessageBan models |
| `backend/app/schemas/guest_message.py` | P5-01 | Pydantic schemas for guest messages |
| `backend/app/routers/guest_messages.py` | P5-01/03 | Router with rate limiting, moderation, ban system |

## Risk / Notes

- Alembic migration for `guest_messages` and `guest_message_bans` tables not yet generated. Tables will be auto-created by `Base.metadata.create_all` in dev, but a proper migration should be added before production deployment.
- The `stars` field on shares/bloggers is used as sort weight on the discover page, consistent with the editorial curation model.
- Legacy `/share` and `/bloggers` pages remain fully functional for admin users; only non-admin visitors are redirected.
- `GuestMessageOut.id` type was changed from `str` to `uuid.UUID` during browser validation to fix a FastAPI serialization 500 error.
- Dev server `.next` cache caused stale bundles during validation. Clearing the cache resolved rendering issues.
- `SameSite=Lax` cookie prevents cross-origin login when frontend and API are on different domains in development. This is a dev environment configuration issue, not a code defect.
