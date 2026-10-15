import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'

const root = process.cwd()

function source(file: string): string {
	return readFileSync(resolve(root, file), 'utf8')
}

const optionalConsumers = [
	'src/app/(home)/learning-space-card.tsx',
	'src/app/about/about-content.tsx',
	'src/app/blog/[id]/blog-detail-content.tsx',
	'src/app/blog/page.tsx',
	'src/app/bloggers/page.tsx',
	'src/app/mistakes/page.tsx',
	'src/app/notes/[id]/note-detail-content.tsx',
	'src/app/notes/page.tsx',
	'src/app/pictures/page.tsx',
	'src/app/projects/page.tsx',
	'src/app/share/page.tsx',
	'src/app/snippets/page.tsx',
	'src/components/mobile-nav.tsx'
]

describe('public optional session-state consumer contract', () => {
	it.each(optionalConsumers)('%s uses explicit optional display state', file => {
		expect(source(file)).toContain("useAdminAuth({ mode: 'optional' })")
	})

	it('keeps the public blog-index helper off strict /api/auth/me', () => {
		const blogIndex = source('src/hooks/use-blog-index.ts')
		expect(blogIndex).toContain("import { useAdminAuth } from '@/hooks/use-admin-auth'")
		expect(blogIndex).toContain("useAdminAuth({ mode: 'optional' })")
		expect(blogIndex).not.toContain('admin-auth-check')
		expect(blogIndex).not.toContain('/api/auth/me')
	})

	it('does not load folder management data for a public sidebar', () => {
		const sidebar = source('src/app/notes/components/knowledge-sidebar.tsx')
		const notes = source('src/app/notes/page.tsx')
		expect(sidebar).toContain('if (!canManage)')
		expect(notes).toContain('if (!isAdmin)')
	})
})
