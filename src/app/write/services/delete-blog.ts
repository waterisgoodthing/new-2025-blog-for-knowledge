import { deleteNote } from '@/lib/api/notes'

export async function deleteBlog(slug: string): Promise<void> {
	if (!slug) throw new Error('需要 slug')
	await deleteNote(slug)
}
