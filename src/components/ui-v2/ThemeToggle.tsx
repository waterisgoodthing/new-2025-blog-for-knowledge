'use client'

import { useEffect, useState } from 'react'
import { Moon, Sun } from 'lucide-react'

import { cn } from '@/lib/utils'

export type ThemeMode = 'light' | 'dark'

export const THEME_STORAGE_KEY = 'uiv2.theme'
export const DARK_MEDIA_QUERY = '(prefers-color-scheme: dark)'

/** Writes the token selector used by `tokens.css` (`[data-theme='dark']`). */
export function applyTheme(mode: ThemeMode): void {
	if (typeof document === 'undefined') return
	document.documentElement.dataset.theme = mode
}

/**
 * Stored preference wins; otherwise follow the OS at mount time.
 * Storage access is best-effort (private mode, disabled storage, quota).
 */
export function resolveInitialTheme(): ThemeMode {
	try {
		const stored = window.localStorage.getItem(THEME_STORAGE_KEY)
		if (stored === 'light' || stored === 'dark') return stored
	} catch {
		// fall through to the media query
	}

	if (typeof window !== 'undefined' && typeof window.matchMedia === 'function') {
		return window.matchMedia(DARK_MEDIA_QUERY).matches ? 'dark' : 'light'
	}

	return 'light'
}

function readStoredTheme(): ThemeMode | null {
	try {
		const stored = window.localStorage.getItem(THEME_STORAGE_KEY)
		return stored === 'light' || stored === 'dark' ? stored : null
	} catch {
		return null
	}
}

export interface ThemeToggleProps {
	className?: string
}

/**
 * Light/dark switch for the dual-surface token system.
 *
 * The tokens are defined with `[data-theme='dark']` (an attribute selector, not
 * `prefers-color-scheme`), so switching means setting
 * `document.documentElement.dataset.theme`.
 */
export function ThemeToggle({ className }: ThemeToggleProps) {
	const [theme, setTheme] = useState<ThemeMode>('light')
	const [hydrated, setHydrated] = useState(false)

	useEffect(() => {
		const initial = resolveInitialTheme()
		setTheme(initial)
		applyTheme(initial)
		setHydrated(true)

		if (typeof window === 'undefined' || typeof window.matchMedia !== 'function') return
		// Follow the OS only while the user has not chosen explicitly.
		const query = window.matchMedia(DARK_MEDIA_QUERY)
		const handleChange = (event: MediaQueryListEvent) => {
			if (readStoredTheme()) return
			const next: ThemeMode = event.matches ? 'dark' : 'light'
			setTheme(next)
			applyTheme(next)
		}
		query.addEventListener?.('change', handleChange)
		return () => query.removeEventListener?.('change', handleChange)
	}, [])

	const toggle = () => {
		const next: ThemeMode = theme === 'dark' ? 'light' : 'dark'
		setTheme(next)
		applyTheme(next)
		try {
			window.localStorage.setItem(THEME_STORAGE_KEY, next)
		} catch {
			// Persisting is best-effort; the visual switch already happened.
		}
	}

	const isDark = theme === 'dark'

	return (
		<button
			type='button'
			onClick={toggle}
			aria-pressed={isDark}
			aria-label={isDark ? '切换到浅色模式' : '切换到深色模式'}
			title={isDark ? '切换到浅色模式' : '切换到深色模式'}
			data-theme-mode={theme}
			data-hydrated={String(hydrated)}
			className={cn(
				'inline-flex items-center justify-center rounded-lg border transition-colors focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--brand)]',
				className
			)}
			style={{
				minHeight: 44,
				minWidth: 44,
				borderColor: 'var(--admin-border, rgba(45, 62, 60, 0.12))',
				background: 'var(--admin-surface-subtle, #fafcfc)',
				color: 'var(--admin-text-secondary, #6b7b79)'
			}}>
			{isDark ? <Sun size={16} aria-hidden='true' /> : <Moon size={16} aria-hidden='true' />}
		</button>
	)
}
