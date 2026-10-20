import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import type { ReactNode } from 'react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { Box, Compass, Home } from 'lucide-react'

import { SIDEBAR_WIDTH_COLLAPSED, SIDEBAR_WIDTH_EXPANDED, AdminSidebar } from './AdminSidebar'
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
		items: [
			{ href: '/manage/notes', label: '笔记写作', icon: Box, match: (p: string) => p.startsWith('/manage/notes') },
			{ href: '/manage/search', label: '搜索', icon: Compass, match: (p: string) => p === '/manage/search', status: 'deferred' }
		]
	}
]

const STORAGE_KEY = 'test.admin-sidebar.collapsed'

/**
 * This jsdom environment does not expose localStorage, so install a minimal
 * in-memory Storage. The component must work with the real API and with a
 * throwing one (covered below).
 */
function installStorage(overrides: Partial<Storage> = {}) {
	const memory = new Map<string, string>()
	const storage = {
		getItem: (key: string) => memory.get(key) ?? null,
		setItem: (key: string, value: string) => {
			memory.set(key, value)
		},
		removeItem: (key: string) => {
			memory.delete(key)
		},
		clear: () => memory.clear(),
		key: (index: number) => Array.from(memory.keys())[index] ?? null,
		get length() {
			return memory.size
		},
		...overrides
	} as Storage

	Object.defineProperty(window, 'localStorage', { value: storage, configurable: true, writable: true })
	return storage
}

beforeEach(() => {
	installStorage()
})

afterEach(() => {
	vi.restoreAllMocks()
})

describe('AdminSidebar — structure and active state', () => {
	it('renders grouped destinations with the active route marked', () => {
		render(<AdminSidebar groups={GROUPS} currentPath='/manage/notes/42' storageKey={STORAGE_KEY} />)

		expect(screen.getByRole('complementary', { name: '学习管理导航' })).toBeInTheDocument()
		expect(screen.getByText('学习空间')).toBeInTheDocument()
		expect(screen.getByText('内容管理')).toBeInTheDocument()

		const active = screen.getByRole('link', { name: /笔记写作/ })
		expect(active).toHaveAttribute('href', '/manage/notes')
		expect(active).toHaveAttribute('aria-current', 'page')
		expect(screen.getByRole('link', { name: /概览/ })).not.toHaveAttribute('aria-current')
	})

	it('marks deferred capabilities', () => {
		render(<AdminSidebar groups={GROUPS} currentPath='/manage/dashboard' storageKey={STORAGE_KEY} />)
		expect(screen.getByText('后续')).toBeInTheDocument()
	})
})

describe('AdminSidebar — collapse behaviour', () => {
	it('starts expanded with the documented width and aria-expanded=true', () => {
		render(<AdminSidebar groups={GROUPS} currentPath='/manage/dashboard' storageKey={STORAGE_KEY} />)

		const toggle = screen.getByRole('button', { name: '折叠导航' })
		expect(toggle).toHaveAttribute('aria-expanded', 'true')
		expect(toggle).toHaveAttribute('aria-controls', 'uiv2-admin-sidebar-nav')

		const aside = screen.getByRole('complementary', { name: '学习管理导航' })
		expect(aside).toHaveAttribute('data-collapsed', 'false')
		expect(aside.style.width).toBe(`${SIDEBAR_WIDTH_EXPANDED}px`)
	})

	it('collapses to the compact width, hides group labels and keeps accessible names', async () => {
		render(<AdminSidebar groups={GROUPS} currentPath='/manage/dashboard' storageKey={STORAGE_KEY} />)

		fireEvent.click(screen.getByRole('button', { name: '折叠导航' }))

		const aside = screen.getByRole('complementary', { name: '学习管理导航' })
		expect(aside).toHaveAttribute('data-collapsed', 'true')
		expect(aside.style.width).toBe(`${SIDEBAR_WIDTH_COLLAPSED}px`)
		expect(screen.getByRole('button', { name: '展开导航' })).toHaveAttribute('aria-expanded', 'false')

		// Group labels become visually hidden but stay in the accessibility tree.
		expect(screen.getByText('学习空间')).toHaveClass('sr-only')
		expect(screen.getByText('内容管理')).toHaveClass('sr-only')

		// Every destination keeps an accessible name and a tooltip.
		const overview = screen.getByRole('link', { name: '概览' })
		expect(overview).toHaveAttribute('title', '概览')
		expect(screen.getByRole('link', { name: '笔记写作' })).toHaveAttribute('href', '/manage/notes')
	})

	it('restores the expanded width when toggled back', async () => {
		render(<AdminSidebar groups={GROUPS} currentPath='/manage/dashboard' storageKey={STORAGE_KEY} />)
		const toggle = screen.getByRole('button', { name: '折叠导航' })

		fireEvent.click(toggle)
		fireEvent.click(screen.getByRole('button', { name: '展开导航' }))

		const aside = screen.getByRole('complementary', { name: '学习管理导航' })
		await waitFor(() => expect(aside).toHaveAttribute('data-collapsed', 'false'))
		expect(aside.style.width).toBe(`${SIDEBAR_WIDTH_EXPANDED}px`)
		expect(screen.getByText('学习空间')).toBeInTheDocument()
	})
})

describe('AdminSidebar — persisted preference', () => {
	it('restores a stored collapsed preference after mount', async () => {
		window.localStorage.setItem(STORAGE_KEY, 'true')
		render(<AdminSidebar groups={GROUPS} currentPath='/manage/dashboard' storageKey={STORAGE_KEY} />)

		const aside = screen.getByRole('complementary', { name: '学习管理导航' })
		await waitFor(() => expect(aside).toHaveAttribute('data-collapsed', 'true'))
		await waitFor(() => expect(aside).toHaveAttribute('data-hydrated', 'true'))
	})

	it('writes the preference when toggled', () => {
		render(<AdminSidebar groups={GROUPS} currentPath='/manage/dashboard' storageKey={STORAGE_KEY} />)

		fireEvent.click(screen.getByRole('button', { name: '折叠导航' }))
		expect(window.localStorage.getItem(STORAGE_KEY)).toBe('true')

		fireEvent.click(screen.getByRole('button', { name: '展开导航' }))
		expect(window.localStorage.getItem(STORAGE_KEY)).toBe('false')
	})

	it('still works when localStorage throws', async () => {
		vi.spyOn(Storage.prototype, 'getItem').mockImplementation(() => {
			throw new Error('blocked')
		})
		vi.spyOn(Storage.prototype, 'setItem').mockImplementation(() => {
			throw new Error('blocked')
		})

		render(<AdminSidebar groups={GROUPS} currentPath='/manage/dashboard' storageKey={STORAGE_KEY} />)

		const aside = screen.getByRole('complementary', { name: '学习管理导航' })
		await waitFor(() => expect(aside).toHaveAttribute('data-hydrated', 'true'))
		expect(aside).toHaveAttribute('data-collapsed', 'false')

		// Toggling must not throw either.
		fireEvent.click(screen.getByRole('button', { name: '折叠导航' }))
		expect(aside).toHaveAttribute('data-collapsed', 'true')
	})
})
