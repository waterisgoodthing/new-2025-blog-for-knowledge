import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { THEME_STORAGE_KEY, ThemeToggle, resolveInitialTheme } from './ThemeToggle'

/** This jsdom environment does not expose localStorage; install a minimal shim. */
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

function installMatchMedia(prefersDark: boolean) {
	vi.stubGlobal(
		'matchMedia',
		vi.fn().mockImplementation((query: string) => ({
			matches: prefersDark && query.includes('dark'),
			media: query,
			onchange: null,
			addEventListener: vi.fn(),
			removeEventListener: vi.fn(),
			addListener: vi.fn(),
			removeListener: vi.fn(),
			dispatchEvent: vi.fn()
		}))
	)
}

beforeEach(() => {
	installStorage()
	installMatchMedia(false)
	document.documentElement.removeAttribute('data-theme')
})

afterEach(() => {
	vi.unstubAllGlobals()
	vi.restoreAllMocks()
	document.documentElement.removeAttribute('data-theme')
})

describe('ThemeToggle — initial state', () => {
	it('restores a stored dark preference on mount', async () => {
		window.localStorage.setItem(THEME_STORAGE_KEY, 'dark')
		render(<ThemeToggle />)

		await waitFor(() => expect(document.documentElement.dataset.theme).toBe('dark'))
		expect(screen.getByRole('button', { name: '切换到浅色模式' })).toHaveAttribute('aria-pressed', 'true')
	})

	it('follows prefers-color-scheme when nothing is stored', async () => {
		installMatchMedia(true)
		render(<ThemeToggle />)

		await waitFor(() => expect(document.documentElement.dataset.theme).toBe('dark'))
	})

	it('defaults to light when the OS has no dark preference', async () => {
		render(<ThemeToggle />)
		await waitFor(() => expect(document.documentElement.dataset.theme).toBe('light'))
	})

	it('resolves the initial mode synchronously for callers', () => {
		window.localStorage.setItem(THEME_STORAGE_KEY, 'dark')
		expect(resolveInitialTheme()).toBe('dark')
	})
})

describe('ThemeToggle — switching', () => {
	it('toggles the document attribute and persists the choice', async () => {
		render(<ThemeToggle />)
		await waitFor(() => expect(document.documentElement.dataset.theme).toBe('light'))

		fireEvent.click(screen.getByRole('button', { name: '切换到深色模式' }))
		expect(document.documentElement.dataset.theme).toBe('dark')
		expect(window.localStorage.getItem(THEME_STORAGE_KEY)).toBe('dark')

		fireEvent.click(screen.getByRole('button', { name: '切换到浅色模式' }))
		expect(document.documentElement.dataset.theme).toBe('light')
		expect(window.localStorage.getItem(THEME_STORAGE_KEY)).toBe('light')
	})

	it('keeps working when localStorage throws', async () => {
		// The shim is a plain object, so Storage.prototype spies would not
		// intercept it. Override the installed instance instead.
		const storage = installStorage()
		storage.getItem = () => {
			throw new Error('blocked')
		}
		storage.setItem = () => {
			throw new Error('blocked')
		}

		render(<ThemeToggle />)
		await waitFor(() => expect(document.documentElement.dataset.theme).toBe('light'))

		fireEvent.click(screen.getByRole('button', { name: '切换到深色模式' }))
		expect(document.documentElement.dataset.theme).toBe('dark')
		expect(screen.getByRole('button', { name: '切换到浅色模式' })).toHaveAttribute('data-hydrated', 'true')
	})

	it('ignores a corrupted stored value and falls back to the media query', async () => {
		window.localStorage.setItem(THEME_STORAGE_KEY, 'sepia')
		installMatchMedia(true)
		render(<ThemeToggle />)

		await waitFor(() => expect(document.documentElement.dataset.theme).toBe('dark'))
	})
})

describe('ThemeToggle — system preference changes', () => {
	it('follows the OS change while the user has not chosen explicitly', async () => {
		let changeHandler: ((event: MediaQueryListEvent) => void) | null = null
		vi.stubGlobal(
			'matchMedia',
			vi.fn().mockImplementation((query: string) => ({
				matches: false,
				media: query,
				onchange: null,
				addEventListener: (_: string, handler: (event: MediaQueryListEvent) => void) => {
					changeHandler = handler
				},
				removeEventListener: vi.fn(),
				addListener: vi.fn(),
				removeListener: vi.fn(),
				dispatchEvent: vi.fn()
			}))
		)

		render(<ThemeToggle />)
		await waitFor(() => expect(document.documentElement.dataset.theme).toBe('light'))

		changeHandler?.({ matches: true } as MediaQueryListEvent)
		await waitFor(() => expect(document.documentElement.dataset.theme).toBe('dark'))
	})

	it('ignores OS changes once the user has chosen explicitly', async () => {
		let changeHandler: ((event: MediaQueryListEvent) => void) | null = null
		vi.stubGlobal(
			'matchMedia',
			vi.fn().mockImplementation((query: string) => ({
				matches: false,
				media: query,
				onchange: null,
				addEventListener: (_: string, handler: (event: MediaQueryListEvent) => void) => {
					changeHandler = handler
				},
				removeEventListener: vi.fn(),
				addListener: vi.fn(),
				removeListener: vi.fn(),
				dispatchEvent: vi.fn()
			}))
		)

		render(<ThemeToggle />)
		await waitFor(() => expect(document.documentElement.dataset.theme).toBe('light'))
		fireEvent.click(screen.getByRole('button', { name: '切换到深色模式' }))
		expect(window.localStorage.getItem(THEME_STORAGE_KEY)).toBe('dark')

		changeHandler?.({ matches: false } as MediaQueryListEvent)
		expect(document.documentElement.dataset.theme).toBe('dark')
	})

	it('defaults to light when matchMedia is unavailable', async () => {
		vi.stubGlobal('matchMedia', undefined)
		window.localStorage.removeItem(THEME_STORAGE_KEY)
		render(<ThemeToggle />)
		await waitFor(() => expect(document.documentElement.dataset.theme).toBe('light'))
	})
})
