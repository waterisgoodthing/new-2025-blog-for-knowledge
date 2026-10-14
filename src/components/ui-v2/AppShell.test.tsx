import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import {
	Uiv2AppHeader,
	Uiv2AppShell,
	Uiv2AppSidebar,
	Uiv2Breadcrumb,
	Uiv2MobileNav,
	Uiv2PageLayout,
} from './AppShell'
import { UIV2_NAV_SECTIONS, findNavEntry } from './navigation'

describe('navigation config', () => {
	it('covers every workspace route with a real href (no invented routes)', () => {
		const hrefs = UIV2_NAV_SECTIONS.flatMap(s => s.items.map(i => i.href))
		for (const href of [
			'/manage/dashboard',
			'/manage/questions',
			'/manage/mistakes',
			'/manage/review',
			'/manage/subjects',
			'/manage/knowledge-points',
			'/manage/notes',
			'/manage/drafts',
			'/manage/analytics',
			'/manage/search',
			'/manage/attachments',
			'/manage/capture',
			'/manage/ai',
			'/manage/jobs',
			'/manage/settings',
		]) {
			expect(hrefs).toContain(href)
		}
	})

	it('resolves review to the learn section with a Week2 note', () => {
		const entry = findNavEntry('/manage/review')
		expect(entry?.section.id).toBe('learn')
		expect(entry?.item.status).toBe('MIGRATE_LATER')
	})

	it('returns null for unknown paths', () => {
		expect(findNavEntry('/manage/does-not-exist')).toBeNull()
	})
})

describe('Uiv2AppSidebar', () => {
	it('marks the current entry with aria-current and keeps anchors keyboard-native', () => {
		render(<Uiv2AppSidebar currentPath="/manage/questions" />)
		const active = screen.getByRole('link', { name: '题库' })
		expect(active).toHaveAttribute('aria-current', 'page')

		const inactive = screen.getByRole('link', { name: '错题' })
		expect(inactive).not.toHaveAttribute('aria-current')
	})

	it('groups entries under labelled sections', () => {
		render(<Uiv2AppSidebar currentPath="/" />)
		expect(screen.getByRole('navigation', { name: '学习系统导航' })).toBeInTheDocument()
		expect(screen.getByText('学习')).toBeInTheDocument()
		expect(screen.getByText('知识')).toBeInTheDocument()
	})
})

describe('Uiv2MobileNav', () => {
	it('renders a compact nav with the active entry marked', () => {
		render(<Uiv2MobileNav currentPath="/manage/review" />)
		expect(screen.getByRole('navigation', { name: '移动导航' })).toBeInTheDocument()
		expect(screen.getByRole('link', { name: '复习' })).toHaveAttribute('aria-current', 'page')
	})
})

describe('Uiv2Breadcrumb', () => {
	it('renders section / item trail for a known path', () => {
		render(<Uiv2Breadcrumb currentPath="/manage/questions" />)
		expect(screen.getByRole('navigation', { name: '面包屑' })).toBeInTheDocument()
		expect(screen.getByText('学习')).toBeInTheDocument()
		expect(screen.getByText('题库')).toBeInTheDocument()
	})

	it('degrades to 首页 only for unknown paths', () => {
		render(<Uiv2Breadcrumb currentPath="/nope" />)
		expect(screen.getByText('首页')).toBeInTheDocument()
		expect(screen.queryByText('学习')).not.toBeInTheDocument()
	})
})

describe('Uiv2AppHeader', () => {
	it('shows location context and an optional primary action', () => {
		render(<Uiv2AppHeader currentPath="/manage/mistakes" action={<button type="button">新建</button>} />)
		expect(screen.getByRole('heading', { name: '错题' })).toBeInTheDocument()
		expect(screen.getByText('学习')).toBeInTheDocument()
		expect(screen.getByRole('button', { name: '新建' })).toBeInTheDocument()
	})

	it('labels unknown locations honestly instead of guessing', () => {
		render(<Uiv2AppHeader currentPath="/nope" />)
		expect(screen.getByRole('heading', { name: '未知位置' })).toBeInTheDocument()
	})
})

describe('Uiv2AppShell + Uiv2PageLayout', () => {
	it('composes sidebar, header, breadcrumb and main landmark', () => {
		render(
			<Uiv2AppShell currentPath="/manage/dashboard">
				<p>shell child</p>
			</Uiv2AppShell>,
		)
		expect(screen.getByRole('navigation', { name: '学习系统导航' })).toBeInTheDocument()
		expect(screen.getByRole('main')).toHaveTextContent('shell child')
		expect(screen.getByRole('navigation', { name: '面包屑' })).toBeInTheDocument()
	})

	it('supports a narrow reading width', () => {
		const { container } = render(
			<Uiv2PageLayout width="narrow">
				<p>narrow</p>
			</Uiv2PageLayout>,
		)
		expect(container.firstElementChild?.className).toContain('max-w-[840px]')
	})
})
