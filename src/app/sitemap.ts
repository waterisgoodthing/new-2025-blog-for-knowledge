import { MetadataRoute } from 'next'
import type { BlogIndexItem } from '@/app/blog/types'
import { getApiBase } from '@/lib/api/config'

const API_BASE = getApiBase()

export const dynamic = 'force-dynamic'

async function fetchBlogs(): Promise<BlogIndexItem[]> {
	try {
		const res = await fetch(`${API_BASE}/api/notes?type=blog&status=published&size=100`, {
			next: { revalidate: 600 }
		})
		if (!res.ok) return []
		const data = await res.json()
		return (data.items || []).map((n: any) => ({
			slug: n.slug,
			title: n.title,
			tags: n.tags?.map((t: any) => t.name) || [],
			date: n.created_at,
			summary: n.summary,
			cover: n.cover,
			hidden: n.hidden,
			category: n.category,
		}))
	} catch {
		return []
	}
}

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
	const baseUrl = process.env.SITE_URL ? process.env.SITE_URL : process.env.VERCEL_URL ? `https://${process.env.VERCEL_URL}` : 'http://localhost:3000'

	const posts = await fetchBlogs()

	const postEntries: MetadataRoute.Sitemap = posts.map(post => ({
		url: `${baseUrl}/blog/${post.slug}`,
		lastModified: post.date ? new Date(post.date) : new Date(),
		changeFrequency: 'weekly',
		priority: 0.8
	}))

	const staticEntries: MetadataRoute.Sitemap = [
		{
			url: baseUrl,
			lastModified: new Date(),
			changeFrequency: 'daily',
			priority: 1
		}
	]

	return [...staticEntries, ...postEntries]
}
