import useSWR from 'swr'
import { listNotes } from '@/lib/api/notes'
import { apiFetch } from '@/lib/api/client'
import type { BlogIndexItem } from '@/app/blog/types'

export type { BlogIndexItem } from '@/app/blog/types'

async function checkAdminAuth(): Promise<boolean> {
	try {
		await apiFetch('/api/auth/me')
		return true
	} catch {
		return false
	}
}

async function fetchBlogIndex(): Promise<BlogIndexItem[]> {
	const result = await listNotes({ type: 'blog', status: 'published', size: 100 })
	return result.items.map(n => ({
		slug: n.slug,
		title: n.title,
		tags: n.tags.map(t => t.name),
		date: n.created_at,
		summary: n.summary,
		cover: n.cover,
		hidden: n.hidden,
		category: n.category,
	}))
}

export function useBlogIndex() {
	const { data: isAdmin } = useSWR<boolean>('admin-auth-check', checkAdminAuth, {
		revalidateOnFocus: false,
		revalidateOnReconnect: false,
		dedupingInterval: 60000,
	})

	const { data, error, isLoading } = useSWR<BlogIndexItem[]>('blog-index', fetchBlogIndex, {
		revalidateOnFocus: false,
		revalidateOnReconnect: true
	})

	let result = data || []
	if (!isAdmin) {
		result = result.filter(item => !item.hidden)
	}

	return {
		items: result,
		loading: isLoading,
		error
	}
}

export function useLatestBlog() {
	const { items, loading, error } = useBlogIndex()

	const latestBlog = items.length > 0 ? items.sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())[0] : null

	return {
		blog: latestBlog,
		loading,
		error
	}
}
