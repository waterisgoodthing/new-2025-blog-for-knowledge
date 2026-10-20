# Validation

Implementation validation has run. Automated/backend/local HTTP validation passed; authenticated browser acceptance remains documented as a residual risk.

Initial inspection completed:

- `git status --short` was checked before planning.
- Touched domain identified as `notes`, with shared folder API/client contract.
- Relevant frontend and backend files were read before any source edits.

## 2026-06-13 T1 Diagnostic Evidence

- `src/app/notes/page.tsx` create link uses `href={createAction.href}` and does not include `activeFolderId`.
- `src/app/write-note/page.tsx` create payload does not include `folder_id`.
- `src/lib/api/notes.ts` `NoteCreateInput` does not include `folder_id`.
- `backend/app/schemas/note.py` `NoteCreate` does not include `folder_id`.
- Red check command:

```bash
cd backend && .venv/bin/python - <<'PY'
import sys
sys.path.insert(0, '.')
from app.schemas.note import NoteCreate
print('folder_id' in NoteCreate.model_fields)
PY
```

Result:

```text
False
```

## 2026-06-13 Implementation Validation

Backend schema/router check:

```bash
cd backend && .venv/bin/python - <<'PY'
import sys
sys.path.insert(0, '.')
from uuid import uuid4
from app.schemas.note import NoteCreate, NoteListItem, NoteOut
from app.routers.notes import create_note
payload = NoteCreate(slug='x', title='X', content='body', folder_id=uuid4())
print(payload.folder_id is not None)
print('folder_id' in NoteListItem.model_fields)
print('folder_id' in NoteOut.model_fields)
print(create_note.__name__)
PY
```

Result:

```text
True
True
True
create_note
```

Backend syntax check:

```bash
cd backend && .venv/bin/python -m compileall app/routers/notes.py app/schemas/note.py
```

Result: passed.

Folder listing count regression check:

```bash
cd backend && .venv/bin/python - <<'PY'
import asyncio
import sys
from uuid import uuid4

sys.path.insert(0, '.')

from app.database import async_session
from app.models.folder import Folder
from app.models.note import Note
from app.routers.folders import list_folders

async def main():
    async with async_session() as session:
        folder = Folder(name=f'codex-folder-count-{uuid4().hex[:8]}')
        session.add(folder)
        await session.flush()

        for i in range(2):
            session.add(Note(
                slug=f'codex-folder-count-{uuid4().hex}-{i}',
                title=f'Codex folder count {i}',
                content='temporary validation note',
                type='note',
                status='published',
                hidden=False,
                folder_id=folder.id,
                sort_order=0,
            ))
        await session.flush()

        tree = await list_folders(db=session)
        target = next((item for item in tree if item.id == folder.id), None)
        print(target.note_count if target else 'missing')
        await session.rollback()

asyncio.run(main())
PY
```

Initial result before the relationship fix:

```text
TypeError: object of type 'Note' has no len()
```

Result after fixing `Folder.notes` as a collection relationship and explicitly loading notes in `list_folders`:

```text
2
```

Post-review verification:

- `cd backend && .venv/bin/python -m compileall app/models/folder.py app/routers/folders.py app/routers/notes.py app/schemas/note.py`: passed.
- Folder listing count regression check rerun: passed with output `2`.
- `npx tsc --noEmit`: passed.
- `git diff --check`: passed.

Frontend type check:

```bash
npx tsc --noEmit
```

Result: passed before and after final cleanup.

Frontend build check:

```bash
npm run build
```

Result: passed. Next.js compiled successfully and generated all routes.

Diff hygiene check:

```bash
git diff --check
```

Result: passed.

Local HTTP checks against the already-running dev server on port 2025:

```bash
curl -I --max-time 10 http://localhost:2025/notes
curl -s --max-time 10 'http://localhost:2025/write-note?folder_id=00000000-0000-0000-0000-000000000000' | head -c 500
```

Result:

- `/notes` returned `HTTP/1.1 200 OK`.
- `/write-note?folder_id=...` returned HTML content.

Browser note:

- The in-app Browser plugin was attempted for `/notes`, but its URL policy blocked visiting `http://localhost:2025/notes`. No browser workaround was attempted.

Residual validation gap:

- A full authenticated browser move/create flow was not completed because the in-app Browser plugin blocked the localhost URL. API/type/build checks passed, and the local server returned the relevant pages.

## 2026-06-14 Public Deployment Validation

Code push:

- Commit: `44e7fa9 fix notes folder assignment flow`
- Branch: `notes-workspace-ux-upgrade`
- Remote push: `mine/notes-workspace-ux-upgrade`
- Push result: succeeded. GitHub reported the repository has moved to `https://github.com/waterisgoodthing/new-2025-blog-for-knowledge.git`, but the configured `mine` remote accepted the push.

Public deployment command:

```bash
source ~/.zshrc && npm run deploy:full
```

Result:

- `npx tsc --noEmit`: passed as part of `deploy:full`.
- `opennextjs-cloudflare build`: passed.
- `wrangler deploy --route 'blog.limengyang.me/*'`: passed.
- Worker: `2025-blog-public`
- Worker URL: `https://2025-blog-public.17527677392.workers.dev`
- Route: `blog.limengyang.me/*`
- Version ID: `9b3dfd5f-00ec-45d4-acca-47090a567373`

Public HTTP checks:

```bash
curl -I --max-time 20 https://blog.limengyang.me/notes
curl -I --max-time 20 'https://blog.limengyang.me/write-note?folder_id=00000000-0000-0000-0000-000000000000'
```

Result:

- `https://blog.limengyang.me/notes`: `HTTP/2 200`, `x-opennext: 1`.
- `https://blog.limengyang.me/write-note?folder_id=...`: `HTTP/2 200`, `x-opennext: 1`.

## 2026-06-14 Public Folder API Recovery

User-visible symptom:

- Move dialog showed `暂无文件夹` even though the expected folder was `计算机网络`.

Root cause:

- `https://public-api.limengyang.me/api/folders` returned `HTTP/2 500`.
- Backend log showed the old folder relationship error:

```text
TypeError: object of type 'Note' has no len()
```

Recovery action:

```bash
launchctl kickstart -k gui/501/com.blog.backend
```

Result:

- Backend restarted from old PID `65869` to new PID `2663`.
- `http://127.0.0.1:8000/api/folders`: `HTTP/1.1 200 OK`.
- `https://public-api.limengyang.me/api/folders`: `HTTP/2 200`.
- Response included folder `计算机网络` with `note_count: 1`.
- `https://public-api.limengyang.me/api/health`: `HTTP/2 200`, body `{"status":"ok","db":"ok"}`.
