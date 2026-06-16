export type ContentType = 'note' | 'blog' | 'mistake'

export function getContentDetailHref(type: ContentType, slug: string): string {
	if (type === 'blog') return `/blog/${slug}`
	return `/notes/${slug}`
}

export function getContentEditHref(type: ContentType, slug: string): string {
	if (type === 'blog') return `/write/${slug}`
	if (type === 'mistake') return `/write-mistake/${slug}`
	return `/write-note/${slug}`
}

export function getContentListHref(type: ContentType, folderId?: string | null): string {
	const base = type === 'blog' ? '/blog' : type === 'mistake' ? '/mistakes' : '/notes'
	if (folderId) return `${base}?folder_id=${encodeURIComponent(folderId)}`
	return base
}
