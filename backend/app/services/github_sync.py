import json

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import get_settings
from app.models.note import Note, Tag

settings = get_settings()

GITHUB_API = "https://api.github.com"


async def _get_headers() -> dict:
    return {
        "Authorization": f"token {settings.GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


async def _get_branch_sha(client: httpx.AsyncClient) -> str:
    res = await client.get(
        f"{GITHUB_API}/repos/{settings.GITHUB_OWNER}/{settings.GITHUB_REPO}/git/refs/heads/{settings.GITHUB_BRANCH}",
        headers=await _get_headers(),
    )
    res.raise_for_status()
    return res.json()["object"]["sha"]


async def _create_blob(client: httpx.AsyncClient, content: str, encoding: str = "utf-8") -> str:
    headers = await _get_headers()
    body: dict = {"encoding": encoding}
    if encoding == "utf-8":
        body["content"] = content
    else:
        body["content"] = content
        body["encoding"] = "base64"
    res = await client.post(
        f"{GITHUB_API}/repos/{settings.GITHUB_OWNER}/{settings.GITHUB_REPO}/git/blobs",
        headers=headers,
        json=body,
    )
    res.raise_for_status()
    return res.json()["sha"]


async def _create_tree(client: httpx.AsyncClient, base_tree_sha: str, tree_items: list[dict]) -> str:
    headers = await _get_headers()
    res = await client.post(
        f"{GITHUB_API}/repos/{settings.GITHUB_OWNER}/{settings.GITHUB_REPO}/git/trees",
        headers=headers,
        json={"base_tree": base_tree_sha, "tree": tree_items},
    )
    res.raise_for_status()
    return res.json()["sha"]


async def _create_commit(client: httpx.AsyncClient, tree_sha: str, parent_sha: str, message: str) -> str:
    headers = await _get_headers()
    res = await client.post(
        f"{GITHUB_API}/repos/{settings.GITHUB_OWNER}/{settings.GITHUB_REPO}/git/commits",
        headers=headers,
        json={"message": message, "tree": tree_sha, "parents": [parent_sha]},
    )
    res.raise_for_status()
    return res.json()["sha"]


async def _update_ref(client: httpx.AsyncClient, commit_sha: str) -> None:
    headers = await _get_headers()
    res = await client.patch(
        f"{GITHUB_API}/repos/{settings.GITHUB_OWNER}/{settings.GITHUB_REPO}/git/refs/heads/{settings.GITHUB_BRANCH}",
        headers=headers,
        json={"sha": commit_sha, "force": False},
    )
    res.raise_for_status()


async def _list_repo_files(client: httpx.AsyncClient, path: str) -> list[dict]:
    headers = await _get_headers()
    res = await client.get(
        f"{GITHUB_API}/repos/{settings.GITHUB_OWNER}/{settings.GITHUB_REPO}/contents/{path}",
        headers=headers,
        params={"ref": settings.GITHUB_BRANCH},
    )
    if res.status_code == 404:
        return []
    res.raise_for_status()
    return res.json() if isinstance(res.json(), list) else []


async def push_notes_to_github(db: AsyncSession) -> dict:
    if not settings.GITHUB_TOKEN or not settings.GITHUB_OWNER or not settings.GITHUB_REPO:
        raise ValueError("GitHub sync not configured. Set GITHUB_TOKEN, GITHUB_OWNER, GITHUB_REPO in .env")

    result = await db.execute(select(Note).options(selectinload(Note.tags)).order_by(Note.updated_at.desc()))
    notes = result.scalars().all()

    index_items = []
    for note in notes:
        index_items.append({
            "slug": note.slug,
            "title": note.title,
            "type": note.type,
            "tags": [t.name for t in note.tags],
            "date": note.created_at.isoformat() if note.created_at else "",
            "hidden": note.hidden,
            "summary": note.summary,
            "cover": note.cover,
            "category": note.category,
            "subject": note.subject,
            "difficulty": note.difficulty,
            "ef": note.ef,
            "interval": note.interval,
            "repetitions": note.repetitions,
            "next_review": note.next_review.isoformat() if note.next_review else None,
            "last_reviewed": note.last_reviewed.isoformat() if note.last_reviewed else None,
        })

    async with httpx.AsyncClient(timeout=30) as client:
        parent_sha = await _get_branch_sha(client)
        tree_items = []

        index_blob_sha = await _create_blob(client, json.dumps(index_items, ensure_ascii=False, indent=2))
        tree_items.append({"path": "public/notes/index.json", "mode": "100644", "type": "blob", "sha": index_blob_sha})

        all_tags = set()
        all_subjects = set()
        all_categories = set()

        for note in notes:
            all_tags.update(t.name for t in note.tags)
            if note.subject:
                all_subjects.add(note.subject)
            if note.category:
                all_categories.add(note.category)

            note_data = {
                "title": note.title,
                "tags": [t.name for t in note.tags],
                "type": note.type,
                "hidden": note.hidden,
                "summary": note.summary,
                "cover": note.cover,
                "category": note.category,
                "subject": note.subject,
                "difficulty": note.difficulty,
                "ef": note.ef,
                "interval": note.interval,
                "repetitions": note.repetitions,
                "next_review": note.next_review.isoformat() if note.next_review else None,
                "last_reviewed": note.last_reviewed.isoformat() if note.last_reviewed else None,
                "question": note.question,
                "my_answer": note.my_answer,
                "correct_answer": note.correct_answer,
                "analysis": note.analysis,
                "knowledge_points": note.knowledge_points,
                "ai_metadata": note.ai_metadata,
            }

            config_sha = await _create_blob(client, json.dumps(note_data, ensure_ascii=False, indent=2))
            tree_items.append({"path": f"public/notes/{note.slug}/config.json", "mode": "100644", "type": "blob", "sha": config_sha})

            content_sha = await _create_blob(client, note.content or "")
            tree_items.append({"path": f"public/notes/{note.slug}/index.md", "mode": "100644", "type": "blob", "sha": content_sha})

        tags_sha = await _create_blob(client, json.dumps({"tags": sorted(all_tags)}, ensure_ascii=False, indent=2))
        tree_items.append({"path": "public/notes/tags.json", "mode": "100644", "type": "blob", "sha": tags_sha})

        subjects_sha = await _create_blob(client, json.dumps({"subjects": sorted(all_subjects)}, ensure_ascii=False, indent=2))
        tree_items.append({"path": "public/notes/subjects.json", "mode": "100644", "type": "blob", "sha": subjects_sha})

        categories_sha = await _create_blob(client, json.dumps({"categories": sorted(all_categories)}, ensure_ascii=False, indent=2))
        tree_items.append({"path": "public/notes/categories.json", "mode": "100644", "type": "blob", "sha": categories_sha})

        tree_sha = await _create_tree(client, parent_sha, tree_items)
        commit_sha = await _create_commit(client, tree_sha, parent_sha, f"sync: update {len(notes)} notes")
        await _update_ref(client, commit_sha)

    return {"pushed": len(notes), "commit": commit_sha[:8]}


async def _read_text_file_from_repo(client: httpx.AsyncClient, path: str) -> str | None:
    headers = await _get_headers()
    res = await client.get(
        f"{GITHUB_API}/repos/{settings.GITHUB_OWNER}/{settings.GITHUB_REPO}/contents/{path}",
        headers=headers,
        params={"ref": settings.GITHUB_BRANCH},
    )
    if res.status_code == 404:
        return None
    res.raise_for_status()
    data = res.json()
    if isinstance(data, list) or "content" not in data:
        return None
    import base64
    content_b64 = data["content"]
    try:
        cleaned_b64 = content_b64.replace("\n", "").replace("\r", "")
        return base64.b64decode(cleaned_b64).decode("utf-8")
    except Exception:
        return base64.b64decode(content_b64).decode("utf-8", errors="ignore")


async def _list_repo_files_recursive(client: httpx.AsyncClient, path: str) -> list[str]:
    headers = await _get_headers()
    res = await client.get(
        f"{GITHUB_API}/repos/{settings.GITHUB_OWNER}/{settings.GITHUB_REPO}/contents/{path}",
        headers=headers,
        params={"ref": settings.GITHUB_BRANCH},
    )
    if res.status_code == 404:
        return []
    res.raise_for_status()
    data = res.json()
    files = []
    if isinstance(data, list):
        for item in data:
            if item["type"] == "file":
                files.append(item["path"])
            elif item["type"] == "dir":
                nested = await _list_repo_files_recursive(client, item["path"])
                files.extend(nested)
    elif isinstance(data, dict):
        if data["type"] == "file":
            files.append(data["path"])
        elif data["type"] == "dir":
            nested = await _list_repo_files_recursive(client, data["path"])
            files.extend(nested)
    return files


from app.schemas.sync import PublishBlogRequest, DeleteBlogRequest, SaveConfigRequest, BatchEditBlogsRequest, SaveJsonFileRequest, CommitRequest

async def publish_blog_to_github(req: PublishBlogRequest) -> str:
    if not settings.GITHUB_TOKEN or not settings.GITHUB_OWNER or not settings.GITHUB_REPO:
        raise ValueError("GitHub sync not configured. Set GITHUB_TOKEN, GITHUB_OWNER, GITHUB_REPO in environment")

    async with httpx.AsyncClient(timeout=30) as client:
        parent_sha = await _get_branch_sha(client)
        
        base_path = f"public/blogs/{req.slug}"
        commit_message = f"更新文章: {req.slug}" if req.mode == "edit" else f"新增文章: {req.slug}"
        
        all_local_images = []
        if req.images:
            for img in req.images:
                if img.type == "file" and img.content_base64:
                    all_local_images.append(img)
        if req.cover and req.cover.type == "file" and req.cover.content_base64:
            all_local_images.append(req.cover)
            
        uploaded_hashes = set()
        md_to_upload = req.md
        cover_path = None
        
        tree_items = []
        
        for img in all_local_images:
            img_hash = img.hash
            if not img_hash:
                import hashlib
                img_hash = hashlib.sha256(img.content_base64.encode("utf-8")).hexdigest()
                
            import os
            ext = os.path.splitext(img.filename)[1] if img.filename else ".png"
            filename = f"{img_hash}{ext}"
            public_path = f"/blogs/{req.slug}/{filename}"
            
            if img_hash not in uploaded_hashes:
                path = f"{base_path}/{filename}"
                blob_sha = await _create_blob(client, img.content_base64, encoding="base64")
                tree_items.append({
                    "path": path,
                    "mode": "100644",
                    "type": "blob",
                    "sha": blob_sha
                })
                uploaded_hashes.add(img_hash)
                
            placeholder = f"local-image:{img.id}"
            md_to_upload = md_to_upload.replace(f"({placeholder})", f"({public_path})")
            
            if req.cover and req.cover.type == "file" and req.cover.id == img.id:
                cover_path = public_path
                
        if req.cover and req.cover.type == "url":
            cover_path = req.cover.url
            
        md_blob_sha = await _create_blob(client, md_to_upload)
        tree_items.append({
            "path": f"{base_path}/index.md",
            "mode": "100644",
            "type": "blob",
            "sha": md_blob_sha
        })
        
        from datetime import datetime, timezone
        date_str = req.date or datetime.now(timezone.utc).isoformat()
        
        config_data = {
            "title": req.title,
            "tags": req.tags,
            "date": date_str,
            "summary": req.summary or "",
            "cover": cover_path,
            "hidden": req.hidden,
            "category": req.category
        }
        
        config_blob_sha = await _create_blob(client, json.dumps(config_data, ensure_ascii=False, indent=2))
        tree_items.append({
            "path": f"{base_path}/config.json",
            "mode": "100644",
            "type": "blob",
            "sha": config_blob_sha
        })
        
        index_path = "public/blogs/index.json"
        blogs_index = []
        try:
            txt = await _read_text_file_from_repo(client, index_path)
            if txt:
                blogs_index = json.loads(txt)
        except Exception:
            pass
            
        entry = {
            "slug": req.slug,
            "title": req.title,
            "tags": req.tags,
            "date": date_str,
            "summary": req.summary or "",
            "cover": cover_path,
            "hidden": req.hidden,
            "category": req.category
        }
        
        index_map = {item["slug"]: item for item in blogs_index if isinstance(item, dict) and "slug" in item}
        index_map[req.slug] = entry
        
        updated_index = list(index_map.values())
        updated_index.sort(key=lambda x: x.get("date", ""), reverse=True)
        
        index_blob_sha = await _create_blob(client, json.dumps(updated_index, ensure_ascii=False, indent=2))
        tree_items.append({
            "path": index_path,
            "mode": "100644",
            "type": "blob",
            "sha": index_blob_sha
        })
        
        tree_sha = await _create_tree(client, parent_sha, tree_items)
        commit_sha = await _create_commit(client, tree_sha, parent_sha, commit_message)
        await _update_ref(client, commit_sha)
        
        return commit_sha


async def delete_blog_from_github(req: DeleteBlogRequest) -> str:
    if not settings.GITHUB_TOKEN or not settings.GITHUB_OWNER or not settings.GITHUB_REPO:
        raise ValueError("GitHub sync not configured. Set GITHUB_TOKEN, GITHUB_OWNER, GITHUB_REPO in environment")

    async with httpx.AsyncClient(timeout=30) as client:
        parent_sha = await _get_branch_sha(client)
        
        base_path = f"public/blogs/{req.slug}"
        files = await _list_repo_files_recursive(client, base_path)
        if not files:
            raise ValueError("文章不存在或已删除")
            
        tree_items = []
        for file_path in files:
            tree_items.append({
                "path": file_path,
                "mode": "100644",
                "type": "blob",
                "sha": None
            })
            
        index_path = "public/blogs/index.json"
        blogs_index = []
        try:
            txt = await _read_text_file_from_repo(client, index_path)
            if txt:
                blogs_index = json.loads(txt)
        except Exception:
            pass
            
        updated_index = [item for item in blogs_index if isinstance(item, dict) and item.get("slug") != req.slug]
        index_blob_sha = await _create_blob(client, json.dumps(updated_index, ensure_ascii=False, indent=2))
        tree_items.append({
            "path": index_path,
            "mode": "100644",
            "type": "blob",
            "sha": index_blob_sha
        })
        
        tree_sha = await _create_tree(client, parent_sha, tree_items)
        commit_sha = await _create_commit(client, tree_sha, parent_sha, f"删除文章: {req.slug}")
        await _update_ref(client, commit_sha)
        
        return commit_sha


async def save_config_to_github(req: SaveConfigRequest) -> str:
    if not settings.GITHUB_TOKEN or not settings.GITHUB_OWNER or not settings.GITHUB_REPO:
        raise ValueError("GitHub sync not configured. Set GITHUB_TOKEN, GITHUB_OWNER, GITHUB_REPO in environment")

    async with httpx.AsyncClient(timeout=30) as client:
        parent_sha = await _get_branch_sha(client)
        
        tree_items = []
        
        # Favicon
        if req.favicon:
            blob_sha = await _create_blob(client, req.favicon.content_base64, encoding="base64")
            tree_items.append({
                "path": "public/favicon.png",
                "mode": "100644",
                "type": "blob",
                "sha": blob_sha
            })
            
        # Avatar
        if req.avatar:
            blob_sha = await _create_blob(client, req.avatar.content_base64, encoding="base64")
            tree_items.append({
                "path": "public/images/avatar.png",
                "mode": "100644",
                "type": "blob",
                "sha": blob_sha
            })
            
        # Art images upload
        if req.artImageUploads:
            for art_id, item in req.artImageUploads.items():
                art_config = None
                if "artImages" in req.siteContent:
                    for art in req.siteContent["artImages"]:
                        if art.get("id") == art_id:
                            art_config = art
                            break
                if not art_config:
                    continue
                url_path = art_config.get("url", "")
                normalized = url_path if url_path.startswith("/") else f"/{url_path}"
                path = f"public{normalized}"
                
                blob_sha = await _create_blob(client, item.content_base64, encoding="base64")
                tree_items.append({
                    "path": path,
                    "mode": "100644",
                    "type": "blob",
                    "sha": blob_sha
                })
                
        # Art images deletion
        if req.removedArtImages:
            for art in req.removedArtImages:
                url_path = art.url
                normalized = url_path if url_path.startswith("/") else f"/{url_path}"
                path = f"public{normalized}"
                tree_items.append({
                    "path": path,
                    "mode": "100644",
                    "type": "blob",
                    "sha": None
                })
                
        # Background images upload
        if req.backgroundImageUploads:
            for bg_id, item in req.backgroundImageUploads.items():
                bg_config = None
                if "backgroundImages" in req.siteContent:
                    for bg in req.siteContent["backgroundImages"]:
                        if bg.get("id") == bg_id:
                            bg_config = bg
                            break
                if not bg_config:
                    continue
                url_path = bg_config.get("url", "")
                if not url_path.startswith("/images/background/"):
                    continue
                normalized = url_path if url_path.startswith("/") else f"/{url_path}"
                path = f"public{normalized}"
                
                blob_sha = await _create_blob(client, item.content_base64, encoding="base64")
                tree_items.append({
                    "path": path,
                    "mode": "100644",
                    "type": "blob",
                    "sha": blob_sha
                })
                
        # Background images deletion
        if req.removedBackgroundImages:
            for bg in req.removedBackgroundImages:
                url_path = bg.url
                if not url_path.startswith("/images/background/"):
                    continue
                normalized = url_path if url_path.startswith("/") else f"/{url_path}"
                path = f"public{normalized}"
                tree_items.append({
                    "path": path,
                    "mode": "100644",
                    "type": "blob",
                    "sha": None
                })
                
        # Social button images upload
        if req.socialButtonImageUploads:
            for btn_id, item in req.socialButtonImageUploads.items():
                btn_config = None
                if "socialButtons" in req.siteContent:
                    for btn in req.siteContent["socialButtons"]:
                        if btn.get("id") == btn_id:
                            btn_config = btn
                            break
                if not btn_config:
                    continue
                url_path = btn_config.get("value", "")
                if not url_path.startswith("/images/social-buttons/"):
                    continue
                normalized = url_path if url_path.startswith("/") else f"/{url_path}"
                path = f"public{normalized}"
                
                blob_sha = await _create_blob(client, item.content_base64, encoding="base64")
                tree_items.append({
                    "path": path,
                    "mode": "100644",
                    "type": "blob",
                    "sha": blob_sha
                })
                
        # Site content JSON
        site_content_json = json.dumps(req.siteContent, ensure_ascii=False, indent="\t")
        site_content_blob = await _create_blob(client, site_content_json)
        tree_items.append({
            "path": "src/config/site-content.json",
            "mode": "100644",
            "type": "blob",
            "sha": site_content_blob
        })
        
        # Card styles JSON
        card_styles_json = json.dumps(req.cardStyles, ensure_ascii=False, indent="\t")
        card_styles_blob = await _create_blob(client, card_styles_json)
        tree_items.append({
            "path": "src/config/card-styles.json",
            "mode": "100644",
            "type": "blob",
            "sha": card_styles_blob
        })
        
        # Create tree, commit, ref
        tree_sha = await _create_tree(client, parent_sha, tree_items)
        commit_sha = await _create_commit(client, tree_sha, parent_sha, "更新站点配置")
        await _update_ref(client, commit_sha)
        
        return commit_sha


async def batch_edit_blogs_on_github(req: BatchEditBlogsRequest) -> str:
    if not settings.GITHUB_TOKEN or not settings.GITHUB_OWNER or not settings.GITHUB_REPO:
        raise ValueError("GitHub sync not configured. Set GITHUB_TOKEN, GITHUB_OWNER, GITHUB_REPO in environment")

    async with httpx.AsyncClient(timeout=30) as client:
        parent_sha = await _get_branch_sha(client)
        
        tree_items = []
        
        # Deletions
        unique_removed = list(set(req.removedSlugs))
        for slug in unique_removed:
            if not slug:
                continue
            base_path = f"public/blogs/{slug}"
            files = await _list_repo_files_recursive(client, base_path)
            for file_path in files:
                tree_items.append({
                    "path": file_path,
                    "mode": "100644",
                    "type": "blob",
                    "sha": None
                })
                
        # Index json
        sorted_items = [item.model_dump() for item in req.nextItems]
        sorted_items.sort(key=lambda x: x.get("date", ""), reverse=True)
        index_json = json.dumps(sorted_items, ensure_ascii=False, indent=2)
        index_blob_sha = await _create_blob(client, index_json)
        tree_items.append({
            "path": "public/blogs/index.json",
            "mode": "100644",
            "type": "blob",
            "sha": index_blob_sha
        })
        
        # Categories json
        unique_categories = list(set(c.strip() for c in req.categories if c.strip()))
        categories_json = json.dumps({"categories": unique_categories}, ensure_ascii=False, indent=2)
        categories_blob_sha = await _create_blob(client, categories_json)
        tree_items.append({
            "path": "public/blogs/categories.json",
            "mode": "100644",
            "type": "blob",
            "sha": categories_blob_sha
        })
        
        # Commit message
        action_labels = []
        if unique_removed:
            action_labels.append(f"删除:{','.join(unique_removed)}")
        action_labels.append("更新索引")
        if unique_categories:
            action_labels.append("更新分类")
        commit_message = " | ".join(action_labels)
        
        tree_sha = await _create_tree(client, parent_sha, tree_items)
        commit_sha = await _create_commit(client, tree_sha, parent_sha, commit_message)
        await _update_ref(client, commit_sha)
        
        return commit_sha


async def save_json_file_to_github(req: SaveJsonFileRequest) -> str:
    # Security check: path must be inside src/ or public/ and end with .json or .xml
    if not (req.path.startswith("src/") or req.path.startswith("public/")):
        raise ValueError("Invalid path prefix. Only src/ and public/ files are allowed.")
    if not (req.path.endswith(".json") or req.path.endswith(".xml")):
        raise ValueError("Invalid path file extension. Only .json and .xml files are allowed.")
        
    if not settings.GITHUB_TOKEN or not settings.GITHUB_OWNER or not settings.GITHUB_REPO:
        raise ValueError("GitHub sync not configured. Set GITHUB_TOKEN, GITHUB_OWNER, GITHUB_REPO in environment")

    async with httpx.AsyncClient(timeout=30) as client:
        parent_sha = await _get_branch_sha(client)
        
        content_str = json.dumps(req.content, ensure_ascii=False, indent="\t")
        blob_sha = await _create_blob(client, content_str)
        
        tree_items = [{
            "path": req.path,
            "mode": "100644",
            "type": "blob",
            "sha": blob_sha
        }]
        
        tree_sha = await _create_tree(client, parent_sha, tree_items)
        commit_sha = await _create_commit(client, tree_sha, parent_sha, req.commitMessage)
        await _update_ref(client, commit_sha)
        
        return commit_sha


async def commit_files_to_github(req: CommitRequest) -> str:
    for file_item in req.files:
        if not (file_item.path.startswith("src/") or file_item.path.startswith("public/")):
            raise ValueError(f"Invalid path prefix for {file_item.path}. Only src/ and public/ files are allowed.")
            
    if not settings.GITHUB_TOKEN or not settings.GITHUB_OWNER or not settings.GITHUB_REPO:
        raise ValueError("GitHub sync not configured. Set GITHUB_TOKEN, GITHUB_OWNER, GITHUB_REPO in environment")

    async with httpx.AsyncClient(timeout=30) as client:
        parent_sha = await _get_branch_sha(client)
        
        tree_items = []
        for file_item in req.files:
            if file_item.content_base64 is None:
                tree_items.append({
                    "path": file_item.path,
                    "mode": "100644",
                    "type": "blob",
                    "sha": None
                })
            else:
                blob_sha = await _create_blob(client, file_item.content_base64, encoding=file_item.encoding)
                tree_items.append({
                    "path": file_item.path,
                    "mode": "100644",
                    "type": "blob",
                    "sha": blob_sha
                })
                
        tree_sha = await _create_tree(client, parent_sha, tree_items)
        commit_sha = await _create_commit(client, tree_sha, parent_sha, req.commitMessage)
        await _update_ref(client, commit_sha)
        
        return commit_sha





