from typing import Optional, List, Dict, Any
from pydantic import BaseModel

class ImageItem(BaseModel):
    id: str
    type: str  # "url" | "file"
    url: Optional[str] = None
    content_base64: Optional[str] = None
    filename: Optional[str] = None
    hash: Optional[str] = None

class PublishBlogRequest(BaseModel):
    slug: str
    title: str
    md: str
    tags: List[str]
    date: Optional[str] = None
    summary: Optional[str] = None
    hidden: Optional[bool] = False
    category: Optional[str] = None
    cover: Optional[ImageItem] = None
    images: Optional[List[ImageItem]] = []
    mode: Optional[str] = "create"
    originalSlug: Optional[str] = None

class DeleteBlogRequest(BaseModel):
    slug: str

class UploadFileItem(BaseModel):
    content_base64: str
    filename: str

class ArtImageConfig(BaseModel):
    id: str
    url: str

class BackgroundImageConfig(BaseModel):
    id: str
    url: str

class SaveConfigRequest(BaseModel):
    siteContent: dict
    cardStyles: dict
    favicon: Optional[UploadFileItem] = None
    avatar: Optional[UploadFileItem] = None
    artImageUploads: Optional[Dict[str, UploadFileItem]] = None
    removedArtImages: Optional[List[ArtImageConfig]] = None
    backgroundImageUploads: Optional[Dict[str, UploadFileItem]] = None
    removedBackgroundImages: Optional[List[BackgroundImageConfig]] = None
    socialButtonImageUploads: Optional[Dict[str, UploadFileItem]] = None

class BlogIndexItem(BaseModel):
    slug: str
    title: str
    type: Optional[str] = None
    tags: List[str]
    date: str
    hidden: Optional[bool] = False
    summary: Optional[str] = None
    cover: Optional[str] = None
    category: Optional[str] = None

class BatchEditBlogsRequest(BaseModel):
    removedSlugs: List[str]
    nextItems: List[BlogIndexItem]
    categories: List[str]

class SaveJsonFileRequest(BaseModel):
    path: str
    content: Any
    commitMessage: str

class CommitFileItem(BaseModel):
    path: str
    content_base64: Optional[str] = None  # None means delete
    encoding: Optional[str] = "base64"

class CommitRequest(BaseModel):
    commitMessage: str
    files: List[CommitFileItem]
