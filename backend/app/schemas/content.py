from typing import Any, Literal

from pydantic import BaseModel, Field


class AboutContent(BaseModel):
    title: str
    description: str
    content: str


class ShareItem(BaseModel):
    name: str
    logo: str
    url: str
    description: str
    tags: list[str] = Field(default_factory=list)
    stars: int = 0


class ProjectItem(BaseModel):
    name: str
    year: int
    description: str
    image: str
    url: str
    tags: list[str] = Field(default_factory=list)
    github: str | None = None
    npm: str | None = None


class PictureItem(BaseModel):
    id: str
    uploadedAt: str
    description: str | None = None
    image: str | None = None
    images: list[str] | None = None


class BloggerItem(BaseModel):
    name: str
    avatar: str
    url: str
    description: str
    stars: int = 0
    status: Literal["recent", "disconnected"] | None = "recent"


class SiteMetaConfig(BaseModel):
    title: str
    description: str
    username: str


class SiteThemeConfig(BaseModel):
    colorBrand: str
    colorPrimary: str
    colorSecondary: str
    colorBrandSecondary: str
    colorBg: str
    colorBorder: str
    colorCard: str
    colorArticle: str


class SiteImageRef(BaseModel):
    id: str
    url: str


class SiteSocialButton(BaseModel):
    id: str
    type: str
    value: str
    label: str | None = None
    order: int


class SiteBeianConfig(BaseModel):
    text: str
    link: str


class SiteContentConfig(BaseModel):
    meta: SiteMetaConfig
    theme: SiteThemeConfig
    backgroundColors: list[str] = Field(default_factory=list)
    artImages: list[SiteImageRef] = Field(default_factory=list)
    currentArtImageId: str = ""
    backgroundImages: list[SiteImageRef] = Field(default_factory=list)
    currentBackgroundImageId: str = ""
    socialButtons: list[SiteSocialButton] = Field(default_factory=list)
    clockShowSeconds: bool = False
    summaryInContent: bool = False
    isCachePem: bool = False
    hideEditButton: bool = False
    enableCategories: bool = False
    currentHatIndex: int = 0
    hatFlipped: bool = False
    enableChristmas: bool = False
    beian: SiteBeianConfig
    faviconUrl: str | None = None
    avatarUrl: str | None = None


class SiteSettingsPayload(BaseModel):
    siteContent: SiteContentConfig
    cardStyles: dict[str, Any]


class DeleteManagedImageRequest(BaseModel):
    url: str
