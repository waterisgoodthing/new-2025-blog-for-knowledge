import uuid

from fastapi import APIRouter, Depends, HTTPException, status
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
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_current_admin),
):
    if req.parent_id:
        parent = await db.get(Folder, req.parent_id)
        if not parent:
            raise HTTPException(status_code=404, detail="Parent folder not found")

    folder = Folder(name=req.name, parent_id=req.parent_id)
    db.add(folder)
    await db.flush()
    await db.refresh(folder)
    return FolderOut(
        id=folder.id, name=folder.name, parent_id=folder.parent_id,
        sort_order=folder.sort_order, created_at=folder.created_at,
        updated_at=folder.updated_at, children=[], note_count=0,
    )


@router.put("/{folder_id}", response_model=FolderOut)
async def update_folder(
    folder_id: uuid.UUID,
    req: FolderUpdate,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_current_admin),
):
    folder = await db.get(Folder, folder_id)
    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")

    if req.name is not None:
        folder.name = req.name
    if req.parent_id is not None:
        if req.parent_id == folder_id:
            raise HTTPException(status_code=400, detail="Cannot move folder into itself")
        folder.parent_id = req.parent_id
    if req.sort_order is not None:
        folder.sort_order = req.sort_order

    await db.flush()
    await db.refresh(folder)
    return FolderOut(
        id=folder.id, name=folder.name, parent_id=folder.parent_id,
        sort_order=folder.sort_order, created_at=folder.created_at,
        updated_at=folder.updated_at, children=[], note_count=0,
    )


@router.delete("/{folder_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_folder(
    folder_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_current_admin),
):
    folder = await db.get(Folder, folder_id)
    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")
    await db.delete(folder)


@router.post("/reorder")
async def reorder_folders(
    req: FolderReorderRequest,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_current_admin),
):
    for item in req.items:
        folder = await db.get(Folder, item.id)
        if folder:
            folder.sort_order = item.sort_order
    return {"ok": True}


@router.post("/move-note/{slug}")
async def move_note_to_folder(
    slug: str,
    req: MoveNoteRequest,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_current_admin),
):
    result = await db.execute(select(Note).where(Note.slug == slug))
    note = result.scalar_one_or_none()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    if req.folder_id:
        folder = await db.get(Folder, req.folder_id)
        if not folder:
            raise HTTPException(status_code=404, detail="Folder not found")

    note.folder_id = req.folder_id
    return {"ok": True, "slug": slug, "folder_id": str(req.folder_id) if req.folder_id else None}
