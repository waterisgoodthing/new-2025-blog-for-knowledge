import { batchDeleteNotes } from '@/lib/api/notes'

export async function batchDeleteBlogs(slugs: string[]): Promise<void> {
	const uniqueSlugs = Array.from(new Set(slugs.filter(Boolean)))
	if (uniqueSlugs.length === 0) {
		throw new Error('需要至少选择一篇文章')
	}
	await batchDeleteNotes(uniqueSlugs)
}
