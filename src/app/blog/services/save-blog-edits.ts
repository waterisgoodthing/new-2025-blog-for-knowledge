import { toast } from 'sonner'
import type { BlogIndexItem } from '@/app/blog/types'
import { batchDeleteNotes, updateNote } from '@/lib/api/notes'

export async function saveBlogEdits(originalItems: BlogIndexItem[], nextItems: BlogIndexItem[], categories: string[]): Promise<void> {
	const removedSlugs = originalItems.filter(item => !nextItems.some(next => next.slug === item.slug)).map(item => item.slug)
	const uniqueRemoved = Array.from(new Set(removedSlugs.filter(Boolean)))

	if (uniqueRemoved.length > 0) {
		toast.info(`正在删除 ${uniqueRemoved.length} 篇文章...`)
		await batchDeleteNotes(uniqueRemoved)
	}

	for (const item of nextItems) {
		const original = originalItems.find(o => o.slug === item.slug)
		const changed = original && (
			original.title !== item.title ||
			original.summary !== item.summary ||
			original.cover !== item.cover ||
			original.hidden !== item.hidden ||
			original.category !== item.category ||
			JSON.stringify(original.tags) !== JSON.stringify(item.tags)
		)
		if (changed) {
			await updateNote(item.slug, {
				title: item.title,
				summary: item.summary,
				cover: item.cover,
				hidden: item.hidden,
				category: item.category,
				tags: item.tags,
			})
		}
	}

	toast.success('保存成功')
}
