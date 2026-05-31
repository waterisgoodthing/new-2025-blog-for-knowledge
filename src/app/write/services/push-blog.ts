import { createNote, updateNote } from '@/lib/api/notes'
import type { ImageItem } from '../types'

export type PushBlogParams = {
	form: {
		slug: string
		title: string
		md: string
		tags: string[]
		date?: string
		summary?: string
		hidden?: boolean
		category?: string
	}
	cover?: ImageItem | null
	images?: ImageItem[]
	mode?: 'create' | 'edit'
	originalSlug?: string | null
}

export async function pushBlog(params: PushBlogParams): Promise<void> {
	const { form, cover, mode = 'create', originalSlug } = params

	if (!form?.slug) throw new Error('需要 slug')

	if (mode === 'edit' && originalSlug && originalSlug !== form.slug) {
		throw new Error('编辑模式下不支持修改 slug，请保持原 slug 不变')
	}

	if (mode === 'edit' && originalSlug) {
		await updateNote(originalSlug, {
			title: form.title,
			content: form.md,
			tags: form.tags,
			summary: form.summary || undefined,
			cover: cover?.type === 'url' ? cover.url : undefined,
			hidden: form.hidden,
			category: form.category || undefined,
		})
	} else {
		await createNote({
			slug: form.slug,
			title: form.title,
			content: form.md,
			type: 'blog',
			status: 'published',
			tags: form.tags,
			summary: form.summary || undefined,
			cover: cover?.type === 'url' ? cover.url : undefined,
			hidden: form.hidden,
			category: form.category || undefined,
		})
	}
}
