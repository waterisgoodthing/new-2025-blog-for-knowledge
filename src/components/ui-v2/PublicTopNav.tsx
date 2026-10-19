'use client'

import Link from 'next/link'
import { useEffect, useRef, useState, type KeyboardEvent as ReactKeyboardEvent } from 'react'
import { ChevronDown } from 'lucide-react'

import { cn } from '@/lib/utils'
import { usePrefersReducedMotion } from '@/hooks/use-overlay'
import { PUBLIC_TOP_NAV, type Uiv2TopNavEntry } from './nav-model'
import styles from './public-top-nav.module.css'

/** Enter the compact sticky state after this much scroll. */
export const STICKY_ENTER_PX = 48
/** Leave it only below this threshold — the gap is the anti-flicker hysteresis. */
export const STICKY_EXIT_PX = 40

export interface PublicTopNavProps {
	entries?: Uiv2TopNavEntry[]
	currentPath?: string
	brandLabel?: string
}

/**
 * Public desktop top navigation (VSC-09).
 *
 * Three states per the spec: floating at the top, compact sticky glass after
 * ~48px of scroll (with hysteresis), and an explicitly opened dropdown.
 */
export function PublicTopNav({ entries = PUBLIC_TOP_NAV, currentPath = '/', brandLabel = 'My Blog' }: PublicTopNavProps) {
	const [stuck, setStuck] = useState(false)
	const [openKey, setOpenKey] = useState<string | null>(null)
	const prefersReducedMotion = usePrefersReducedMotion()

	const triggerRefs = useRef(new Map<string, HTMLButtonElement>())
	const menuRefs = useRef(new Map<string, HTMLUListElement>())
	const pendingFocusRef = useRef<'first' | 'last' | null>(null)

	useEffect(() => {
		const evaluate = () => {
			const y = window.scrollY || 0
			// Hysteresis: the threshold to become stuck is higher than the one to
			// unstick, so a page resting between 40 and 48px cannot flicker.
			setStuck(previous => (previous ? y > STICKY_EXIT_PX : y > STICKY_ENTER_PX))
		}
		evaluate()
		window.addEventListener('scroll', evaluate, { passive: true })
		return () => window.removeEventListener('scroll', evaluate)
	}, [])

	const menuLinks = (key: string) => Array.from(menuRefs.current.get(key)?.querySelectorAll<HTMLAnchorElement>('a[href]') ?? [])

	const focusItem = (key: string, index: number) => {
		const links = menuLinks(key)
		if (links.length === 0) return
		links[((index % links.length) + links.length) % links.length]?.focus()
	}

	// Focus after the menu actually mounts, not before.
	useEffect(() => {
		if (!openKey) return
		const pending = pendingFocusRef.current
		if (!pending) return
		pendingFocusRef.current = null
		focusItem(openKey, pending === 'first' ? 0 : -1)
	}, [openKey])

	// Outside interaction closes the dropdown.
	useEffect(() => {
		if (!openKey) return
		const handlePointerDown = (event: MouseEvent) => {
			const menu = menuRefs.current.get(openKey)
			const trigger = triggerRefs.current.get(openKey)
			const target = event.target as Node | null
			if (target && (menu?.contains(target) || trigger?.contains(target))) return
			setOpenKey(null)
		}
		document.addEventListener('mousedown', handlePointerDown)
		return () => document.removeEventListener('mousedown', handlePointerDown)
	}, [openKey])

	// Escape closes and returns focus to the trigger that owns the menu.
	useEffect(() => {
		if (!openKey) return
		const handleKeyDown = (event: KeyboardEvent) => {
			if (event.key !== 'Escape') return
			event.stopPropagation()
			const trigger = triggerRefs.current.get(openKey)
			setOpenKey(null)
			trigger?.focus()
		}
		document.addEventListener('keydown', handleKeyDown)
		return () => document.removeEventListener('keydown', handleKeyDown)
	}, [openKey])

	const openMenu = (key: string, focus: 'first' | 'last' | null) => {
		pendingFocusRef.current = focus
		setOpenKey(key)
	}

	const handleTriggerKeyDown = (event: ReactKeyboardEvent<HTMLButtonElement>, key: string) => {
		if (event.key === 'Enter' || event.key === ' ' || event.key === 'ArrowDown') {
			event.preventDefault()
			if (openKey === key) {
				setOpenKey(null)
			} else {
				openMenu(key, 'first')
			}
			return
		}
		if (event.key === 'ArrowUp') {
			event.preventDefault()
			openMenu(key, 'last')
			return
		}
	}

	const handleMenuKeyDown = (event: ReactKeyboardEvent<HTMLUListElement>, key: string) => {
		const links = menuLinks(key)
		const currentIndex = links.findIndex(link => link === document.activeElement)

		if (event.key === 'ArrowDown') {
			event.preventDefault()
			focusItem(key, currentIndex + 1)
		} else if (event.key === 'ArrowUp') {
			event.preventDefault()
			focusItem(key, currentIndex - 1)
		} else if (event.key === 'Home') {
			event.preventDefault()
			focusItem(key, 0)
		} else if (event.key === 'End') {
			event.preventDefault()
			focusItem(key, -1)
		}
	}

	return (
		<nav
			aria-label='主导航'
			data-state={stuck ? 'stuck' : 'top'}
			data-reduced-motion={String(prefersReducedMotion)}
			className={cn(
				'fixed inset-x-0 top-0 z-40 border-b',
				styles.bar,
				stuck ? styles.stuck : styles.top,
				prefersReducedMotion && styles.reducedMotion
			)}
			style={{ height: stuck ? 56 : 72 }}>
			<div className='mx-auto flex h-full max-w-[1120px] items-center justify-between gap-6 px-4 sm:px-6'>
				<Link
					href='/'
					className='rounded-lg text-sm font-semibold tracking-tight focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--brand)]'
					style={{ color: 'var(--editorial-text-primary, #4a3832)' }}>
					{brandLabel}
				</Link>

				<ul className='flex items-center gap-1'>
					{entries.map(entry => {
						const single = entry.items.length === 1 ? entry.items[0] : null

						if (single) {
							const active = single.match(currentPath)
							return (
								<li key={entry.key}>
									<Link
										href={single.href}
										onClick={() => setOpenKey(null)}
										aria-current={active ? 'page' : undefined}
										className='inline-flex min-h-9 items-center rounded-full px-3 text-sm transition-colors focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--brand)]'
										style={{
											background: active ? 'var(--nav-active-bg, rgba(61, 184, 168, 0.12))' : 'transparent',
											color: active ? 'var(--brand-ink, #1f7a6e)' : 'var(--editorial-text-secondary, #8b7667)'
										}}>
										{single.label}
									</Link>
								</li>
							)
						}

						const isOpen = openKey === entry.key
						const active = entry.items.some(item => item.match(currentPath))
						const menuId = `public-top-nav-menu-${entry.key}`

						return (
							<li
								key={entry.key}
								className='relative'
								onBlur={event => {
									if (event.currentTarget.contains(event.relatedTarget as Node | null)) return
									setOpenKey(null)
								}}>
								<button
									ref={node => {
										if (node) triggerRefs.current.set(entry.key, node)
										else triggerRefs.current.delete(entry.key)
									}}
									type='button'
									aria-expanded={isOpen}
									aria-controls={menuId}
									onClick={() => (isOpen ? setOpenKey(null) : openMenu(entry.key, null))}
									onKeyDown={event => handleTriggerKeyDown(event, entry.key)}
									className='inline-flex min-h-9 items-center gap-1 rounded-full px-3 text-sm transition-colors focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--brand)]'
									style={{
										background: isOpen || active ? 'var(--nav-active-bg, rgba(61, 184, 168, 0.12))' : 'transparent',
										color: active ? 'var(--brand-ink, #1f7a6e)' : 'var(--editorial-text-secondary, #8b7667)'
									}}>
									{entry.label}
									<ChevronDown size={14} aria-hidden='true' className={isOpen ? 'rotate-180 transition-transform' : 'transition-transform'} />
								</button>

								{isOpen ? (
									<ul
										id={menuId}
										ref={node => {
											if (node) menuRefs.current.set(entry.key, node)
											else menuRefs.current.delete(entry.key)
										}}
										aria-label={entry.label}
										onKeyDown={event => handleMenuKeyDown(event, entry.key)}
										className='absolute top-full right-0 mt-2 flex w-56 flex-col gap-0.5 rounded-xl border p-1.5'
										style={{
											background: 'var(--admin-surface, #ffffff)',
											borderColor: 'var(--admin-border, rgba(45, 62, 60, 0.12))',
											boxShadow: 'var(--ui-shadow-lg, 0 12px 32px rgba(0, 0, 0, 0.12))'
										}}>
										{entry.items.map(item => {
											const itemActive = item.match(currentPath)
											const Icon = item.icon
											return (
												<li key={item.href}>
													<Link
														href={item.href}
														onClick={() => setOpenKey(null)}
														aria-current={itemActive ? 'page' : undefined}
														className='flex items-center gap-2 rounded-lg px-3 py-2 text-sm transition-colors focus-visible:outline-2 focus-visible:outline-offset-[-2px] focus-visible:outline-[var(--brand)]'
														style={{
															background: itemActive ? 'var(--nav-active-bg, rgba(61, 184, 168, 0.12))' : 'transparent',
															color: itemActive ? 'var(--brand-ink, #1f7a6e)' : 'var(--admin-text-primary, #2d3e3c)'
														}}>
														<Icon className='h-4 w-4 shrink-0' aria-hidden='true' />
														<span className='min-w-0 flex-1'>{item.label}</span>
													</Link>
												</li>
											)
										})}
									</ul>
								) : null}
							</li>
						)
					})}
				</ul>
			</div>
		</nav>
	)
}
