import { render, screen, waitFor } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import { resetOverlayState } from '@/hooks/use-overlay'
import { APP_PORTAL_ROOT_ID } from './portal-root'
import { Uiv2Modal } from './Modal'

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
			<Uiv2AppShell currentPath="/manage/dashboard" variant="admin">
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

describe('Uiv2AppShell — variant and slots', () => {
	it('renders the public variant without the administrator sidebar', () => {
		render(
			<Uiv2AppShell currentPath='/' variant='public'>
				<p>public body</p>
			</Uiv2AppShell>,
		)
		expect(screen.queryByRole('navigation', { name: '学习系统导航' })).not.toBeInTheDocument()
		expect(screen.getByRole('main')).toHaveTextContent('public body')
		expect(screen.getByRole('navigation', { name: '面包屑' })).toBeInTheDocument()
	})

	it('accepts custom navigation slots instead of the default ones', () => {
		render(
			<Uiv2AppShell
				currentPath='/manage/dashboard'
				variant='admin'
				sidebar={<aside aria-label='自定义侧栏'>custom sidebar</aside>}
				mobileNav={<nav aria-label='自定义移动导航'>custom mobile</nav>}
				header={<header>custom header</header>}>
				<p>admin body</p>
			</Uiv2AppShell>,
		)

		expect(screen.getByRole('complementary', { name: '自定义侧栏' })).toBeInTheDocument()
		expect(screen.getByRole('navigation', { name: '自定义移动导航' })).toBeInTheDocument()
		expect(screen.getByText('custom header')).toBeInTheDocument()
		expect(screen.queryByRole('navigation', { name: '学习系统导航' })).not.toBeInTheDocument()
	})

	it('mounts the overlay portal host directly under <body>, outside any stacking context', () => {
		const { container } = render(
			<Uiv2AppShell currentPath='/manage/dashboard' variant='admin'>
				<p>body</p>
			</Uiv2AppShell>,
		)

		const portalRoot = document.getElementById(APP_PORTAL_ROOT_ID)
		const backgroundRoot = container.querySelector('[data-overlay-background-root]')

		expect(portalRoot).not.toBeNull()
		expect(portalRoot?.parentElement).toBe(document.body)
		expect(backgroundRoot).not.toBeNull()
		expect(backgroundRoot?.contains(portalRoot as Node)).toBe(false)
		// It must not be nested inside the shell (which the public layout wraps
		// in `main.relative.z-10`, capping every descendant z-index).
		expect(container.contains(portalRoot as Node)).toBe(false)
	})

	it('does not render administrator chrome when the variant is public', () => {
		render(
			<Uiv2AppShell currentPath='/manage/dashboard' variant='public'>
				<p>body</p>
			</Uiv2AppShell>,
		)
		expect(screen.queryByRole('navigation', { name: '学习系统导航' })).not.toBeInTheDocument()
	})
})

describe('Uiv2AppShell — overlay background isolation', () => {
	beforeEach(() => {
		resetOverlayState()
	})

	it('marks the background root inert while a modal is open and clears it after close', async () => {
		const { container, rerender } = render(
			<Uiv2AppShell currentPath='/manage/dashboard' variant='admin'>
				<p>body</p>
			</Uiv2AppShell>,
		)
		expect(container.querySelector('[data-overlay-background-root]')).not.toHaveAttribute('inert')

		rerender(
			<Uiv2AppShell currentPath='/manage/dashboard' variant='admin'>
				<p>body</p>
				<Uiv2Modal open onClose={vi.fn()} title='确认' />
			</Uiv2AppShell>,
		)

		await waitFor(() => expect(container.querySelector('[data-overlay-background-root]')).toHaveAttribute('inert'))

		rerender(
			<Uiv2AppShell currentPath='/manage/dashboard' variant='admin'>
				<p>body</p>
				<Uiv2Modal open={false} onClose={vi.fn()} title='确认' />
			</Uiv2AppShell>,
		)

		await waitFor(() => expect(container.querySelector('[data-overlay-background-root]')).not.toHaveAttribute('inert'))
	})

	it('keeps the background inert until every nested overlay closes', async () => {
		const shell = (innerOpen: boolean, outerOpen: boolean) => (
			<Uiv2AppShell currentPath='/manage/dashboard' variant='admin'>
				<p>body</p>
				<Uiv2Modal open={outerOpen} onClose={vi.fn()} title='外层' />
				<Uiv2Modal open={innerOpen} onClose={vi.fn()} title='内层' />
			</Uiv2AppShell>
		)

		const { container, rerender } = render(shell(true, true))
		const background = () => container.querySelector('[data-overlay-background-root]')
		await waitFor(() => expect(background()).toHaveAttribute('inert'))

		rerender(shell(false, true))
		await waitFor(() => expect(background()).toHaveAttribute('inert'))

		rerender(shell(false, false))
		await waitFor(() => expect(background()).not.toHaveAttribute('inert'))
	})
})
