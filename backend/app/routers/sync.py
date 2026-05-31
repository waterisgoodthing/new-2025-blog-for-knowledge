from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.routers.auth import get_current_admin
from app.schemas.sync import PublishBlogRequest, DeleteBlogRequest, SaveConfigRequest, BatchEditBlogsRequest, SaveJsonFileRequest, CommitRequest
from app.services.github_sync import (
    push_notes_to_github,
    publish_blog_to_github,
    delete_blog_from_github,
    save_config_to_github,
    batch_edit_blogs_on_github,
    save_json_file_to_github,
    commit_files_to_github,
)

router = APIRouter(prefix="/api/sync", tags=["sync"])


@router.post("/push")
async def sync_push(db: AsyncSession = Depends(get_db), _admin=Depends(get_current_admin)):
    try:
        result = await push_notes_to_github(db)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sync failed: {e}")


@router.post("/publish-blog")
async def publish_blog(req: PublishBlogRequest, _admin=Depends(get_current_admin)):
    try:
        commit_sha = await publish_blog_to_github(req)
        return {"status": "success", "commit_sha": commit_sha}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to publish blog to GitHub: {e}")


@router.post("/delete-blog")
async def delete_blog(req: DeleteBlogRequest, _admin=Depends(get_current_admin)):
    try:
        commit_sha = await delete_blog_from_github(req)
        return {"status": "success", "commit_sha": commit_sha}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete blog from GitHub: {e}")


@router.post("/save-config")
async def save_config(req: SaveConfigRequest, _admin=Depends(get_current_admin)):
    try:
        commit_sha = await save_config_to_github(req)
        return {"status": "success", "commit_sha": commit_sha}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save site config to GitHub: {e}")


@router.post("/batch-edit-blogs")
async def batch_edit_blogs(
    req: BatchEditBlogsRequest,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(get_current_admin)
):
    try:
        commit_sha = await batch_edit_blogs_on_github(req)
        
        from sqlalchemy import select
        from app.models.note import Note
        
        if req.removedSlugs:
            result = await db.execute(select(Note).where(Note.slug.in_(req.removedSlugs)))
            notes = result.scalars().all()
            for note in notes:
                await db.delete(note)
            await db.flush()
            
        return {"status": "success", "commit_sha": commit_sha}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to batch edit blogs on GitHub: {e}")


@router.post("/save-json-file")
async def save_json_file(req: SaveJsonFileRequest, _admin=Depends(get_current_admin)):
    try:
        commit_sha = await save_json_file_to_github(req)
        return {"status": "success", "commit_sha": commit_sha}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file to GitHub: {e}")


@router.post("/commit")
async def commit(req: CommitRequest, _admin=Depends(get_current_admin)):
    try:
        commit_sha = await commit_files_to_github(req)
        return {"status": "success", "commit_sha": commit_sha}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to push commit: {e}")





