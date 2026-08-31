import { createNote, updateNote, uploadImage } from '@/lib/api/notes'
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

type LocalImageItem = Extract<ImageItem, { type: 'file' }>

async function uploadLocalImage(image: LocalImageItem, slug: string, uploadedUrls: Map<string, string>): Promise<string> {
	const cachedUrl = uploadedUrls.get(image.id)
	if (cachedUrl) return cachedUrl

	const result = await uploadImage(image.file, { noteType: 'blog', slug })
	uploadedUrls.set(image.id, result.url)
	return result.url
}

async function resolveCoverUrl(cover: ImageItem | null | undefined, slug: string, uploadedUrls: Map<string, string>): Promise<string | undefined> {
	if (!cover) return undefined
	if (cover.type === 'url') return cover.url

	return uploadLocalImage(cover, slug, uploadedUrls)
}

async function resolveMarkdownImageUrls(markdown: string, images: ImageItem[] | undefined, slug: string, uploadedUrls: Map<string, string>): Promise<string> {
	let resolvedMarkdown = markdown
	for (const image of images || []) {
		if (image.type !== 'file') continue

		const placeholder = `local-image:${image.id}`
		if (!resolvedMarkdown.includes(placeholder)) continue

		const url = await uploadLocalImage(image, slug, uploadedUrls)
		resolvedMarkdown = resolvedMarkdown.split(placeholder).join(url)
	}

	return resolvedMarkdown
}

export async function pushBlog(params: PushBlogParams): Promise<void> {
	const { form, cover, images, mode = 'create', originalSlug } = params

	if (!form?.slug) throw new Error('需要 slug')

	if (mode === 'edit' && originalSlug && originalSlug !== form.slug) {
		throw new Error('编辑模式下不支持修改 slug，请保持原 slug 不变')
	}

	const uploadedUrls = new Map<string, string>()
	const coverUrl = await resolveCoverUrl(cover, form.slug, uploadedUrls)
	const content = await resolveMarkdownImageUrls(form.md, images, form.slug, uploadedUrls)

	if (mode === 'edit' && originalSlug) {
		await updateNote(originalSlug, {
			title: form.title,
			content,
			tags: form.tags,
			summary: form.summary || undefined,
			cover: coverUrl,
			hidden: form.hidden,
			category: form.category || undefined,
		})
	} else {
		await createNote({
			slug: form.slug,
			title: form.title,
			content,
			type: 'blog',
			status: 'published',
			tags: form.tags,
			summary: form.summary || undefined,
			cover: coverUrl,
			hidden: form.hidden,
			category: form.category || undefined,
		})
	}
}
