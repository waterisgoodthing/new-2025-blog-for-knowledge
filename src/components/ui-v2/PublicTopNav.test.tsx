import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import type { ReactNode } from 'react'
import { afterEach, describe, expect, it, vi } from 'vitest'

import { PUBLIC_TOP_NAV, type Uiv2TopNavEntry } from './nav-model'
import { PublicTopNav, STICKY_ENTER_PX, STICKY_EXIT_PX } from './PublicTopNav'

vi.mock('next/link', () => ({
	default: ({ href, children, ...rest }: { href: string; children: ReactNode } & Record<string, unknown>) => (
		<a href={href} {...rest}>
			{children}
		</a>
	)
}))

const ENTRIES: Uiv2TopNavEntry[] = PUBLIC_TOP_NAV

function setScrollY(value: number) {
	Object.defineProperty(window, 'scrollY', { value, configurable: true, writable: true })
	fireEvent.scroll(window)
}

afterEach(() => {
	Object.defineProperty(window, 'scrollY', { value: 0, configurable: true, writable: true })
	vi.restoreAllMocks()
})

describe('PublicTopNav — structure', () => {
	it('renders a labelled primary navigation with direct and disclosure entries', () => {
		render(<PublicTopNav entries={ENTRIES} currentPath='/blog' />)

		expect(screen.getByRole('navigation', { name: '主导航' })).toBeInTheDocument()
		expect(screen.getByRole('link', { name: '首页' })).toHaveAttribute('href', '/')
		expect(screen.getByRole('button', { name: /内容/ })).toHaveAttribute('aria-expanded', 'false')
		// A disclosure of links is not an ARIA menu, so it must not claim aria-haspopup.
		expect(screen.getByRole('button', { name: /探索/ })).not.toHaveAttribute('aria-haspopup')
	})

	it('links each trigger to its menu with aria-controls', () => {
		render(<PublicTopNav entries={ENTRIES} currentPath='/' />)
		const trigger = screen.getByRole('button', { name: /内容/ })
		expect(trigger).toHaveAttribute('aria-controls', 'public-top-nav-menu-content')

		fireEvent.click(trigger)
		expect(screen.getByRole('list', { name: '内容' })).toHaveAttribute('id', 'public-top-nav-menu-content')
	})

	it('marks the active destination with aria-current="page"', () => {
		render(<PublicTopNav entries={ENTRIES} currentPath='/notes/welcome' />)

		// Child routes are inside the disclosure, so open it first.
		fireEvent.click(screen.getByRole('button', { name: /内容/ }))
		expect(screen.getByRole('link', { name: '笔记' })).toHaveAttribute('aria-current', 'page')
		expect(screen.getByRole('link', { name: '博客' })).not.toHaveAttribute('aria-current')
	})

	it('never renders an administrator entry', () => {
		render(<PublicTopNav entries={ENTRIES} currentPath='/' />)
		expect(screen.queryByText('管理')).not.toBeInTheDocument()
		expect(document.querySelector('a[href="/manage/dashboard"]')).toBeNull()
	})
})

describe('PublicTopNav — floating to sticky', () => {
	it('starts in the floating state', () => {
		render(<PublicTopNav entries={ENTRIES} currentPath='/' />)
		expect(screen.getByRole('navigation', { name: '主导航' })).toHaveAttribute('data-state', 'top')
	})

	it('switches to the stuck state after the enter threshold', () => {
		render(<PublicTopNav entries={ENTRIES} currentPath='/' />)
		setScrollY(STICKY_ENTER_PX + 10)
		expect(screen.getByRole('navigation', { name: '主导航' })).toHaveAttribute('data-state', 'stuck')
	})

	it('keeps the stuck state inside the hysteresis band and releases below the exit threshold', () => {
		render(<PublicTopNav entries={ENTRIES} currentPath='/' />)

		setScrollY(STICKY_ENTER_PX + 20)
		expect(screen.getByRole('navigation', { name: '主导航' })).toHaveAttribute('data-state', 'stuck')

		// Between exit and enter: must not flip back (anti-flicker).
		setScrollY(STICKY_EXIT_PX + 4)
		expect(screen.getByRole('navigation', { name: '主导航' })).toHaveAttribute('data-state', 'stuck')

		setScrollY(STICKY_EXIT_PX - 4)
		expect(screen.getByRole('navigation', { name: '主导航' })).toHaveAttribute('data-state', 'top')
	})
})

describe('PublicTopNav — dropdown behaviour', () => {
	it('opens on click and closes on a second click', () => {
		render(<PublicTopNav entries={ENTRIES} currentPath='/' />)
		const trigger = screen.getByRole('button', { name: /内容/ })

		fireEvent.click(trigger)
		expect(trigger).toHaveAttribute('aria-expanded', 'true')
		expect(screen.getByRole('link', { name: '博客' })).toBeInTheDocument()

		fireEvent.click(trigger)
		expect(trigger).toHaveAttribute('aria-expanded', 'false')
		expect(screen.queryByRole('link', { name: '博客' })).not.toBeInTheDocument()
	})

	it.each([
		['Enter', 'Enter'],
		['Space', ' '],
		['ArrowDown', 'ArrowDown']
	])('opens with %s and moves focus into the menu', async (_label, key) => {
		render(<PublicTopNav entries={ENTRIES} currentPath='/' />)
		const trigger = screen.getByRole('button', { name: /内容/ })

		fireEvent.keyDown(trigger, { key })
		expect(trigger).toHaveAttribute('aria-expanded', 'true')

		await waitFor(() => expect(screen.getByRole('link', { name: '博客' })).toHaveFocus())
	})

	it('moves through items with ArrowDown / ArrowUp and Home / End', async () => {
		render(<PublicTopNav entries={ENTRIES} currentPath='/' />)
		fireEvent.keyDown(screen.getByRole('button', { name: /内容/ }), { key: 'Enter' })

		const blog = screen.getByRole('link', { name: '博客' })
		const notes = screen.getByRole('link', { name: '笔记' })
		const mistakes = screen.getByRole('link', { name: '错题' })
		await waitFor(() => expect(blog).toHaveFocus())

		fireEvent.keyDown(blog, { key: 'ArrowDown' })
		expect(notes).toHaveFocus()

		fireEvent.keyDown(notes, { key: 'ArrowUp' })
		expect(blog).toHaveFocus()

		fireEvent.keyDown(blog, { key: 'End' })
		expect(mistakes).toHaveFocus()

		fireEvent.keyDown(mistakes, { key: 'Home' })
		expect(blog).toHaveFocus()
	})

	it('closes on Escape and returns focus to the trigger', async () => {
		render(<PublicTopNav entries={ENTRIES} currentPath='/' />)
		const trigger = screen.getByRole('button', { name: /内容/ })

		fireEvent.keyDown(trigger, { key: 'Enter' })
		const blog = screen.getByRole('link', { name: '博客' })
		await waitFor(() => expect(blog).toHaveFocus())

		fireEvent.keyDown(document, { key: 'Escape' })
		expect(screen.queryByRole('link', { name: '博客' })).not.toBeInTheDocument()
		await waitFor(() => expect(trigger).toHaveFocus())
	})

	it('closes on an outside pointer interaction', () => {
		render(<PublicTopNav entries={ENTRIES} currentPath='/' />)
		fireEvent.click(screen.getByRole('button', { name: /内容/ }))
		expect(screen.getByRole('link', { name: '博客' })).toBeInTheDocument()

		fireEvent.mouseDown(document.body)
		expect(screen.queryByRole('link', { name: '博客' })).not.toBeInTheDocument()
	})

	it('keeps only one disclosure open at a time', () => {
		render(<PublicTopNav entries={ENTRIES} currentPath='/' />)
		fireEvent.click(screen.getByRole('button', { name: /内容/ }))
		expect(screen.getByRole('link', { name: '博客' })).toBeInTheDocument()

		fireEvent.click(screen.getByRole('button', { name: /探索/ }))
		expect(screen.queryByRole('link', { name: '博客' })).not.toBeInTheDocument()
		expect(screen.getByRole('link', { name: '发现' })).toBeInTheDocument()
	})
})

describe('PublicTopNav — dismissal without stranding focus', () => {
	it('closes when a menu destination is activated', () => {
		render(<PublicTopNav entries={ENTRIES} currentPath='/' />)
		fireEvent.click(screen.getByRole('button', { name: /内容/ }))
		fireEvent.click(screen.getByRole('link', { name: '博客' }))
		expect(screen.queryByRole('link', { name: '博客' })).not.toBeInTheDocument()
	})

	it('closes when focus leaves the disclosure, without dropping focus to <body>', async () => {
		render(
			<div>
				<PublicTopNav entries={ENTRIES} currentPath='/' />
				<button type='button'>after nav</button>
			</div>
		)
		const trigger = screen.getByRole('button', { name: /内容/ })
		trigger.focus()
		fireEvent.keyDown(trigger, { key: 'Enter' })

		const blog = screen.getByRole('link', { name: '博客' })
		await waitFor(() => expect(blog).toHaveFocus())

		const outside = screen.getByRole('button', { name: 'after nav' })
		outside.focus()
		fireEvent.focusOut(blog.closest('li') as HTMLElement, { relatedTarget: outside })

		expect(screen.queryByRole('link', { name: '博客' })).not.toBeInTheDocument()
		expect(outside).toHaveFocus()
	})

	it('marks reduced-motion users for the transition switch', () => {
		render(<PublicTopNav entries={ENTRIES} currentPath='/' />)
		expect(screen.getByRole('navigation', { name: '主导航' })).toHaveAttribute('data-reduced-motion', 'false')
	})
})
