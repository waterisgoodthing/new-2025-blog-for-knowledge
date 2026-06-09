import uuid

from fastapi import APIRouter, Cookie, Depends, HTTPException, Request, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.folder import Folder
from app.models.note import Note
from app.models.note import User
from app.routers.auth import get_current_admin
from app.schemas.folder import (
    FolderCreate,
    FolderOut,
    FolderReorderRequest,
    FolderUpdate,
    MoveNoteRequest,
)

router = APIRouter(prefix="/api/folders", tags=["folders"])

MAX_FOLDER_DEPTH = 4


async def _get_folder_depth(db: AsyncSession, folder_id: uuid.UUID) -> int:
    depth = 0
    current_id: uuid.UUID | None = folder_id
    visited: set[uuid.UUID] = set()
    while current_id is not None:
        if current_id in visited:
            break
        visited.add(current_id)
        folder = await db.get(Folder, current_id)
        if not folder:
            break
        depth += 1
        current_id = folder.parent_id
    return depth


async def _is_descendant(db: AsyncSession, ancestor_id: uuid.UUID, descendant_id: uuid.UUID) -> bool:
    current_id: uuid.UUID | None = descendant_id
    visited: set[uuid.UUID] = set()
    while current_id is not None:
        if current_id == ancestor_id:
            return True
        if current_id in visited:
            break
        visited.add(current_id)
        folder = await db.get(Folder, current_id)
        if not folder:
            break
        current_id = folder.parent_id
    return False


def _build_tree(folders: list[Folder], parent_id: uuid.UUID | None = None) -> list[FolderOut]:
    result = []
    for f in folders:
        if f.parent_id == parent_id:
            children = _build_tree(folders, f.id)
            note_count = len(f.notes) if hasattr(f, 'notes') and f.notes else 0
            result.append(FolderOut(
                id=f.id,
                name=f.name,
                parent_id=f.parent_id,
                sort_order=f.sort_order,
                created_at=f.created_at,
                updated_at=f.updated_at,
                children=children,
                note_count=note_count,
            ))
    result.sort(key=lambda x: x.sort_order)
    return result


@router.get("", response_model=list[FolderOut])
async def list_folders(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Folder).options(selectinload(Folder.children))
    )
    folders = list(result.scalars().all())
    return _build_tree(folders, None)


@router.post("", response_model=FolderOut, status_code=status.HTTP_201_CREATED)
async def create_folder(
    req: FolderCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_current_admin),
    session_token: str | None = Cookie(None, alias="admin_session"),
):
    if req.parent_id:
        parent = await db.get(Folder, req.parent_id)
        if not parent:
            raise HTTPException(status_code=404, detail="Parent folder not found")
        parent_depth = await _get_folder_depth(db, req.parent_id)
        if parent_depth >= MAX_FOLDER_DEPTH:
            raise HTTPException(status_code=400, detail=f"Maximum nesting depth of {MAX_FOLDER_DEPTH} exceeded")

    max_order_result = await db.execute(
        select(func.max(Folder.sort_order)).where(Folder.parent_id == req.parent_id)
    )
    max_order = max_order_result.scalar() or 0

    folder = Folder(name=req.name, parent_id=req.parent_id, sort_order=max_order + 1)
    db.add(folder)
    await db.flush()
    await db.refresh(folder)

    from app.services.audit_service import audit_action
    await audit_action(
        db, action="create", session_token=session_token, request=request,
        entity_type="folder", entity_id=str(folder.id),
        after={"name": folder.name, "parent_id": str(folder.parent_id) if folder.parent_id else None},
    )

    return FolderOut(
        id=folder.id, name=folder.name, parent_id=folder.parent_id,
        sort_order=folder.sort_order, created_at=folder.created_at,
        updated_at=folder.updated_at, children=[], note_count=0,
    )


@router.put("/{folder_id}", response_model=FolderOut)
async def update_folder(
    folder_id: uuid.UUID,
    req: FolderUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_current_admin),
    session_token: str | None = Cookie(None, alias="admin_session"),
):
    folder = await db.get(Folder, folder_id)
    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")

    if req.name is not None:
        folder.name = req.name
    if req.parent_id is not None:
        if req.parent_id == folder_id:
            raise HTTPException(status_code=400, detail="Cannot move folder into itself")
        if await _is_descendant(db, folder_id, req.parent_id):
            raise HTTPException(status_code=400, detail="Cannot move folder into its own descendant")
        parent_depth = await _get_folder_depth(db, req.parent_id)
        if parent_depth >= MAX_FOLDER_DEPTH:
            raise HTTPException(status_code=400, detail=f"Maximum nesting depth of {MAX_FOLDER_DEPTH} exceeded")
        folder.parent_id = req.parent_id
    if req.sort_order is not None:
        folder.sort_order = req.sort_order

    await db.flush()
    await db.refresh(folder)

    from app.services.audit_service import audit_action
    await audit_action(
        db, action="update", session_token=session_token, request=request,
        entity_type="folder", entity_id=str(folder.id),
        after={"name": folder.name, "parent_id": str(folder.parent_id) if folder.parent_id else None},
    )

    return FolderOut(
        id=folder.id, name=folder.name, parent_id=folder.parent_id,
        sort_order=folder.sort_order, created_at=folder.created_at,
        updated_at=folder.updated_at, children=[], note_count=0,
    )


@router.delete("/{folder_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_folder(
    folder_id: uuid.UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_current_admin),
    session_token: str | None = Cookie(None, alias="admin_session"),
):
    folder = await db.get(Folder, folder_id)
    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")

    folder_name = folder.name

    result = await db.execute(
        select(Folder).where(Folder.parent_id == folder_id)
    )
    child_folders = list(result.scalars().all())
    for child in child_folders:
        child.parent_id = folder.parent_id
        db.add(child)

    result = await db.execute(
        select(Note).where(Note.folder_id == folder_id)
    )
    notes_in_folder = list(result.scalars().all())
    for note in notes_in_folder:
        note.folder_id = None
        db.add(note)

    from app.services.audit_service import audit_action
    await audit_action(
        db, action="delete", session_token=session_token, request=request,
        entity_type="folder", entity_id=str(folder_id),
        before={"name": folder_name, "child_folders": len(child_folders), "notes_moved": len(notes_in_folder)},
    )

    await db.delete(folder)


@router.post("/reorder")
async def reorder_folders(
    req: FolderReorderRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_current_admin),
    session_token: str | None = Cookie(None, alias="admin_session"),
):
    for item in req.items:
        folder = await db.get(Folder, item.id)
        if folder:
            folder.sort_order = item.sort_order

    from app.services.audit_service import audit_action
    await audit_action(
        db, action="reorder", session_token=session_token, request=request,
        entity_type="folder", after={"count": len(req.items)},
    )

    return {"ok": True}


@router.post("/move-note/{slug}")
async def move_note_to_folder(
    slug: str,
    req: MoveNoteRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_current_admin),
    session_token: str | None = Cookie(None, alias="admin_session"),
):
    result = await db.execute(select(Note).where(Note.slug == slug))
    note = result.scalar_one_or_none()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    if req.folder_id:
        folder = await db.get(Folder, req.folder_id)
        if not folder:
            raise HTTPException(status_code=404, detail="Folder not found")

    old_folder_id = str(note.folder_id) if note.folder_id else None
    note.folder_id = req.folder_id

    from app.services.audit_service import audit_action
    await audit_action(
        db, action="move", session_token=session_token, request=request,
        entity_type=note.type, entity_id=str(note.id),
        before={"folder_id": old_folder_id},
        after={"folder_id": str(req.folder_id) if req.folder_id else None},
    )

    return {"ok": True, "slug": slug, "folder_id": str(req.folder_id) if req.folder_id else None}
