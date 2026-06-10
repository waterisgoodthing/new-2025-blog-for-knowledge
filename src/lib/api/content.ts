import { apiFetch } from './client'

export interface AboutContent {
  title: string
  description: string
  content: string
}

export interface ShareItem {
  name: string
  logo: string
  url: string
  description: string
  tags: string[]
  stars: number
}

export interface ProjectItem {
  name: string
  year: number
  description: string
  image: string
  url: string
  tags: string[]
  github?: string | null
  npm?: string | null
}

export interface PictureItem {
  id: string
  uploadedAt: string
  description?: string | null
  image?: string | null
  images?: string[] | null
}

export interface BloggerItem {
  name: string
  avatar: string
  url: string
  description: string
  stars: number
  status?: 'recent' | 'disconnected' | null
}

export interface SiteMetaConfig {
  title: string
  description: string
  username: string
}

export interface SiteThemeConfig {
  colorBrand: string
  colorPrimary: string
  colorSecondary: string
  colorBrandSecondary: string
  colorBg: string
  colorBorder: string
  colorCard: string
  colorArticle: string
}

export interface SiteImageRef {
  id: string
  url: string
}

export interface SiteSocialButton {
  id: string
  type: string
  value: string
  label?: string | null
  order: number
}

export interface SiteBeianConfig {
  text: string
  link: string
}

export interface SiteContentConfig {
  meta: SiteMetaConfig
  theme: SiteThemeConfig
  backgroundColors: string[]
  artImages: SiteImageRef[]
  currentArtImageId: string
  backgroundImages: SiteImageRef[]
  currentBackgroundImageId: string
  socialButtons: SiteSocialButton[]
  clockShowSeconds: boolean
  summaryInContent: boolean
  isCachePem: boolean
  hideEditButton: boolean
  enableCategories: boolean
  currentHatIndex: number
  hatFlipped: boolean
  enableChristmas: boolean
  beian: SiteBeianConfig
  faviconUrl?: string | null
  avatarUrl?: string | null
}

export interface SiteSettingsPayload {
  siteContent: SiteContentConfig
  cardStyles: Record<string, unknown>
}

export interface UploadImageResult {
  url: string
  path: string
}

export async function getAbout(): Promise<AboutContent> {
  return apiFetch<AboutContent>('/api/content/about')
}

export async function updateAbout(data: AboutContent): Promise<AboutContent> {
  return apiFetch<AboutContent>('/api/content/about', {
    method: 'PUT',
    body: JSON.stringify(data),
  })
}

export async function getShares(): Promise<ShareItem[]> {
  return apiFetch<ShareItem[]>('/api/content/shares')
}

export async function updateShares(items: ShareItem[]): Promise<ShareItem[]> {
  return apiFetch<ShareItem[]>('/api/content/shares', {
    method: 'PUT',
    body: JSON.stringify(items),
  })
}

export async function getProjects(): Promise<ProjectItem[]> {
  return apiFetch<ProjectItem[]>('/api/content/projects')
}

export async function updateProjects(items: ProjectItem[]): Promise<ProjectItem[]> {
  return apiFetch<ProjectItem[]>('/api/content/projects', {
    method: 'PUT',
    body: JSON.stringify(items),
  })
}

export async function getPictures(): Promise<PictureItem[]> {
  return apiFetch<PictureItem[]>('/api/content/pictures')
}

export async function updatePictures(items: PictureItem[]): Promise<PictureItem[]> {
  return apiFetch<PictureItem[]>('/api/content/pictures', {
    method: 'PUT',
    body: JSON.stringify(items),
  })
}

export async function getSnippets(): Promise<string[]> {
  return apiFetch<string[]>('/api/content/snippets')
}

export async function updateSnippets(items: string[]): Promise<string[]> {
  return apiFetch<string[]>('/api/content/snippets', {
    method: 'PUT',
    body: JSON.stringify(items),
  })
}

export async function getBloggers(): Promise<BloggerItem[]> {
  return apiFetch<BloggerItem[]>('/api/content/bloggers')
}

export async function updateBloggers(items: BloggerItem[]): Promise<BloggerItem[]> {
  return apiFetch<BloggerItem[]>('/api/content/bloggers', {
    method: 'PUT',
    body: JSON.stringify(items),
  })
}

export async function getSiteSettings(): Promise<SiteSettingsPayload> {
  return apiFetch<SiteSettingsPayload>('/api/content/site-settings')
}

export async function updateSiteSettings(payload: SiteSettingsPayload): Promise<SiteSettingsPayload> {
  return apiFetch<SiteSettingsPayload>('/api/content/site-settings', {
    method: 'PUT',
    body: JSON.stringify(payload),
  })
}

export async function uploadContentImage(file: File, scope: string, group?: string): Promise<UploadImageResult> {
  const formData = new FormData()
  formData.append('file', file)
  let url = `/api/content/upload-image?scope=${encodeURIComponent(scope)}`
  if (group) {
    url += `&group=${encodeURIComponent(group)}`
  }
  return apiFetch<UploadImageResult>(url, {
    method: 'POST',
    body: formData,
  })
}

export async function deleteContentImage(url: string): Promise<void> {
  return apiFetch<void>('/api/content/delete-image', {
    method: 'DELETE',
    body: JSON.stringify({ url }),
  })
}
