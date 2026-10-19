import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import type { ReactNode } from 'react'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import { Home, NotebookPen } from 'lucide-react'

import { resetOverlayState } from '@/hooks/use-overlay'
import { Uiv2AppShell } from './AppShell'
import { APP_PORTAL_ROOT_ID } from './portal-root'
import { MOBILE_DRAWER_ID, MobileDrawer } from './MobileDrawer'
import type { Uiv2NavGroup } from './nav-model'

vi.mock('next/link', () => ({
	default: ({ href, children, ...rest }: { href: string; children: ReactNode } & Record<string, unknown>) => (
		<a href={href} {...rest}>
			{children}
		</a>
	)
}))

const GROUPS: Uiv2NavGroup[] = [
	{
		title: '学习空间',
		items: [{ href: '/manage/dashboard', label: '概览', icon: Home, match: (p: string) => p === '/manage/dashboard' }]
	},
	{
		title: '内容管理',
		items: [{ href: '/manage/notes', label: '笔记写作', icon: NotebookPen, match: (p: string) => p.startsWith('/manage/notes') }]
	}
]

beforeEach(() => {
	resetOverlayState()
})

describe('MobileDrawer — trigger and topbar', () => {
	it('renders a hamburger trigger linked to the drawer and the current destination', () => {
		render(<MobileDrawer groups={GROUPS} currentPath='/manage/notes/42' />)

		const trigger = screen.getByRole('button', { name: '打开导航菜单' })
		expect(trigger).toHaveAttribute('aria-expanded', 'false')
		expect(trigger).toHaveAttribute('aria-haspopup', 'dialog')
		expect(trigger).toHaveAttribute('aria-controls', MOBILE_DRAWER_ID)
		expect(screen.getByText('笔记写作')).toBeInTheDocument()
	})

	it('renders a trailing action slot without stealing the primary label', () => {
		render(<MobileDrawer groups={GROUPS} currentPath='/manage/dashboard' action={<a href='/'>首页</a>} />)
		expect(screen.getByRole('link', { name: '首页' })).toHaveAttribute('href', '/')
		expect(screen.getByText('概览')).toBeInTheDocument()
	})
})

describe('MobileDrawer — open, close, route change', () => {
	it('opens the shared drawer from the right with a nav list', async () => {
		render(<MobileDrawer groups={GROUPS} currentPath='/manage/dashboard' />)

		fireEvent.click(screen.getByRole('button', { name: '打开导航菜单' }))
		expect(screen.getByRole('button', { name: '打开导航菜单' })).toHaveAttribute('aria-expanded', 'true')

		const dialog = await screen.findByRole('dialog', { name: '导航' })
		expect(dialog).toHaveAttribute('data-side', 'right')
		expect(dialog).toHaveAttribute('id', MOBILE_DRAWER_ID)

		const nav = screen.getByRole('navigation', { name: '导航菜单' })
		expect(nav).toBeInTheDocument()
		expect(screen.getByRole('link', { name: '概览' })).toHaveAttribute('aria-current', 'page')
		expect(screen.getByRole('link', { name: '笔记写作' })).not.toHaveAttribute('aria-current')
	})

	it('closes on Escape and restores focus to the hamburger', async () => {
		render(<MobileDrawer groups={GROUPS} currentPath='/manage/dashboard' />)
		const trigger = screen.getByRole('button', { name: '打开导航菜单' })
		// Browsers focus a button on mousedown; jsdom's click does not.
		trigger.focus()
		fireEvent.click(trigger)

		await screen.findByRole('dialog', { name: '导航' })
		fireEvent.keyDown(document, { key: 'Escape' })

		await waitFor(() => expect(trigger).toHaveAttribute('aria-expanded', 'false'))
		await waitFor(() => expect(trigger).toHaveFocus())
	})

	it('closes itself when the route changes', async () => {
		const { rerender } = render(<MobileDrawer groups={GROUPS} currentPath='/manage/dashboard' />)
		const trigger = screen.getByRole('button', { name: '打开导航菜单' })

		fireEvent.click(trigger)
		expect(trigger).toHaveAttribute('aria-expanded', 'true')

		rerender(<MobileDrawer groups={GROUPS} currentPath='/manage/notes' />)
		await waitFor(() => expect(screen.getByRole('button', { name: '打开导航菜单' })).toHaveAttribute('aria-expanded', 'false'))
	})

	it('closes from the footer close button', async () => {
		render(<MobileDrawer groups={GROUPS} currentPath='/manage/dashboard' />)
		fireEvent.click(screen.getByRole('button', { name: '打开导航菜单' }))
		await screen.findByRole('dialog', { name: '导航' })

		fireEvent.click(screen.getByRole('button', { name: '关闭导航' }))
		await waitFor(() => expect(screen.getByRole('button', { name: '打开导航菜单' })).toHaveAttribute('aria-expanded', 'false'))
	})
})

describe('MobileDrawer inside Uiv2AppShell', () => {
	it('restores focus to the trigger even though the shell is inert while open', async () => {
		render(
			<Uiv2AppShell
				currentPath='/manage/dashboard'
				variant='admin'
				mobileNav={<MobileDrawer groups={GROUPS} currentPath='/manage/dashboard' />}>
				<p>body</p>
			</Uiv2AppShell>
		)

		const background = document.querySelector('[data-overlay-background-root]')
		const trigger = screen.getByRole('button', { name: '打开导航菜单' })
		trigger.focus()
		fireEvent.click(trigger)

		await screen.findByRole('dialog', { name: '导航' })
		await waitFor(() => expect(background).toHaveAttribute('inert'))

		fireEvent.keyDown(document, { key: 'Escape' })

		// The background must be released *before* focus is restored, otherwise
		// focusing an inert element silently fails and focus drops to <body>.
		await waitFor(() => expect(background).not.toHaveAttribute('inert'))
		await waitFor(() => expect(trigger).toHaveFocus())
	})
})

describe('MobileDrawer — portal placement', () => {
	it('portals the dialog into the body-level host, not into the shell subtree', async () => {
		const { container } = render(
			<Uiv2AppShell
				currentPath='/manage/dashboard'
				variant='admin'
				mobileNav={<MobileDrawer groups={GROUPS} currentPath='/manage/dashboard' />}>
				<p>body</p>
			</Uiv2AppShell>
		)

		fireEvent.click(screen.getByRole('button', { name: '打开导航菜单' }))
		const dialog = await screen.findByRole('dialog', { name: '导航' })

		const host = document.getElementById(APP_PORTAL_ROOT_ID)
		expect(host).not.toBeNull()
		expect(host?.contains(dialog)).toBe(true)
		expect(container.contains(dialog)).toBe(false)
	})
})
