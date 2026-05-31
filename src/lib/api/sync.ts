import { apiFetch } from './client'

export type SyncImageItem = {
	id: string
	type: 'url' | 'file'
	url?: string
	content_base64?: string
	filename?: string
	hash?: string
}

export type PublishBlogRequest = {
	slug: string
	title: string
	md: string
	tags: string[]
	date?: string
	summary?: string
	hidden?: boolean
	category?: string
	cover?: SyncImageItem | null
	images?: SyncImageItem[]
	mode?: 'create' | 'edit'
	originalSlug?: string | null
}

export async function publishBlogToGithub(req: PublishBlogRequest): Promise<{ commit_sha: string }> {
	return apiFetch('/api/sync/publish-blog', {
		method: 'POST',
		body: JSON.stringify(req)
	})
}

export async function deleteBlogFromGithub(slug: string): Promise<{ commit_sha: string }> {
	return apiFetch('/api/sync/delete-blog', {
		method: 'POST',
		body: JSON.stringify({ slug })
	})
}

export type UploadFileItem = {
	content_base64: string
	filename: string
}

export type SaveConfigRequest = {
	siteContent: any
	cardStyles: any
	favicon?: UploadFileItem | null
	avatar?: UploadFileItem | null
	artImageUploads?: Record<string, UploadFileItem>
	removedArtImages?: Array<{ id: string; url: string }>
	backgroundImageUploads?: Record<string, UploadFileItem>
	removedBackgroundImages?: Array<{ id: string; url: string }>
	socialButtonImageUploads?: Record<string, UploadFileItem>
}

export async function saveConfigToGithub(req: SaveConfigRequest): Promise<{ commit_sha: string }> {
	return apiFetch('/api/sync/save-config', {
		method: 'POST',
		body: JSON.stringify(req)
	})
}

export type BlogIndexItem = {
	slug: string
	title: string
	type?: string
	tags: string[]
	date: string
	hidden?: boolean
	summary?: string
	cover?: string
	category?: string
}

export type BatchEditBlogsRequest = {
	removedSlugs: string[]
	nextItems: BlogIndexItem[]
	categories: string[]
}

export async function batchEditBlogsOnGithub(req: BatchEditBlogsRequest): Promise<{ commit_sha: string }> {
	return apiFetch('/api/sync/batch-edit-blogs', {
		method: 'POST',
		body: JSON.stringify(req)
	})
}

export type SaveJsonFileRequest = {
	path: string
	content: any
	commitMessage: string
}

export async function saveJsonFileToGithub(req: SaveJsonFileRequest): Promise<{ commit_sha: string }> {
	return apiFetch('/api/sync/save-json-file', {
		method: 'POST',
		body: JSON.stringify(req)
	})
}

export type CommitFileItem = {
	path: string
	content_base64: string | null
	encoding?: string
}

export type CommitRequest = {
	commitMessage: string
	files: CommitFileItem[]
}

export async function commitFilesToGithub(req: CommitRequest): Promise<{ commit_sha: string }> {
	return apiFetch('/api/sync/commit', {
		method: 'POST',
		body: JSON.stringify(req)
	})
}




