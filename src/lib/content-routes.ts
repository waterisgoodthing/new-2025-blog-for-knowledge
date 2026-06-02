export type ContentType = 'note' | 'blog' | 'mistake'

export function getContentDetailHref(type: ContentType, slug: string): string {
	if (type === 'blog') return `/blog/${slug}`
	return `/notes/${slug}`
}

export function getContentEditHref(type: ContentType, slug: string): string {
	if (type === 'blog') return `/write/${slug}`
	return `/write-note/${slug}`
}

export function getContentListHref(type: ContentType): string {
	if (type === 'blog') return '/blog'
	if (type === 'mistake') return '/mistakes'
	return '/notes'
}
