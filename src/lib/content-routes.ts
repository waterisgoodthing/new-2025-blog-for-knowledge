export type ContentType = 'note' | 'blog' | 'mistake'

export function getContentDetailHref(type: ContentType, slug: string): string {
	if (type === 'blog') return `/blog/${slug}`
	return `/notes/${slug}`
}

export function getContentEditHref(type: ContentType, slug: string): string {
	// Route Cutover: 旧 write-* 编辑入口已停用，统一指向 /manage/* 主线
	if (type === 'mistake') return `/manage/mistakes`
	return `/manage/dashboard`
}

export function getContentListHref(type: ContentType, folderId?: string | null): string {
	const base = type === 'blog' ? '/blog' : type === 'mistake' ? '/mistakes' : '/notes'
	if (folderId) return `${base}?folder_id=${encodeURIComponent(folderId)}`
	return base
}
