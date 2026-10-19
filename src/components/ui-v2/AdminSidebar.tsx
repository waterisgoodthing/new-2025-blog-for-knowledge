'use client'

import Link from 'next/link'
import { useEffect, useState } from 'react'
import { PanelLeftClose, PanelLeftOpen } from 'lucide-react'

import { cn } from '@/lib/utils'
import { usePrefersReducedMotion } from '@/hooks/use-overlay'
import type { Uiv2NavGroup } from './nav-model'

export const SIDEBAR_WIDTH_EXPANDED = 232
export const SIDEBAR_WIDTH_COLLAPSED = 64

export interface AdminSidebarProps {
	groups: Uiv2NavGroup[]
	currentPath: string
	/** localStorage key for the collapsed preference. */
	storageKey?: string
	/** Preference used before localStorage is read (and when storage is unavailable). */
	defaultCollapsed?: boolean
	className?: string
}

/**
 * Administrator desktop sidebar (VSC-10).
 *
 * Click-collapsible 232px ↔ 64px. Collapsed links keep an accessible name via
 * `aria-label` and expose the label as a native tooltip. Collapse is a button,
 * never pointer hover, and the preference is memoised in localStorage.
 */
export function AdminSidebar({
	groups,
	currentPath,
	storageKey = 'uiv2.admin-sidebar.collapsed',
	defaultCollapsed = false,
	className
}: AdminSidebarProps) {
	const [collapsed, setCollapsed] = useState(defaultCollapsed)
	const [hydrated, setHydrated] = useState(false)
	const prefersReducedMotion = usePrefersReducedMotion()
	const navId = 'uiv2-admin-sidebar-nav'

	// Read the stored preference after mount (SSR has no storage, and a
	// throwing/blocked localStorage must not break navigation).
	useEffect(() => {
		try {
			const stored = window.localStorage.getItem(storageKey)
			if (stored === 'true' || stored === 'false') setCollapsed(stored === 'true')
		} catch {
			// Ignore: private mode, disabled storage, quota errors.
		}
		setHydrated(true)
	}, [storageKey])

	const toggle = () => {
		setCollapsed(previous => {
			const next = !previous
			try {
				window.localStorage.setItem(storageKey, String(next))
			} catch {
				// Persisting is best-effort only.
			}
			return next
		})
	}

	const width = collapsed ? SIDEBAR_WIDTH_COLLAPSED : SIDEBAR_WIDTH_EXPANDED

	return (
		<aside
			aria-label='学习管理导航'
			data-collapsed={String(collapsed)}
			data-hydrated={String(hydrated)}
			className={cn(
				'hidden min-w-0 shrink-0 flex-col overflow-hidden rounded-[24px] border backdrop-blur-xl md:flex md:min-h-[calc(100svh-3rem)]',
				className
			)}
			style={{
				width,
				borderColor: 'var(--admin-border, rgba(45, 62, 60, 0.12))',
				background: 'var(--admin-surface, #ffffff)',
				boxShadow: 'var(--ui-shadow-md, 0 4px 16px rgba(0, 0, 0, 0.08))',
				// Suppress the first transition: a restored collapsed preference must
				// not animate 232 -> 64 on every mount.
				transition: prefersReducedMotion || !hydrated ? 'none' : 'width 300ms var(--ease-out, cubic-bezier(0, 0, 0.2, 1))'
			}}>
			<div className='flex items-center justify-between gap-2 px-3 py-3'>
				<span
					className={cn('truncate text-xs font-medium tracking-wide', collapsed && 'sr-only')}
					style={{ color: 'var(--admin-text-tertiary, #9eadab)' }}>
					学习管理
				</span>
				<button
					type='button'
					onClick={toggle}
					aria-expanded={!collapsed}
					aria-controls={navId}
					aria-label={collapsed ? '展开导航' : '折叠导航'}
					title={collapsed ? '展开导航' : '折叠导航'}
					className='inline-flex h-8 w-8 shrink-0 items-center justify-center rounded-lg transition-colors focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--brand)]'
					style={{ color: 'var(--admin-text-secondary, #6b7b79)' }}>
					{collapsed ? <PanelLeftOpen size={16} aria-hidden='true' /> : <PanelLeftClose size={16} aria-hidden='true' />}
				</button>
			</div>

			<nav id={navId} aria-label='导航（桌面端分组）' className='flex min-h-0 flex-1 flex-col gap-4 overflow-y-auto px-2 pb-4'>
				{groups.map(group => (
					<div key={group.title} className='flex flex-col gap-1'>
						{/* Kept in the DOM when collapsed (visually hidden) so the grouping is
						    not lost to assistive technology. */}
						<p
							className={cn('px-2 text-[11px] font-medium tracking-wide', collapsed && 'sr-only')}
							style={{ color: 'var(--admin-text-tertiary, #9eadab)' }}>
							{group.title}
						</p>

						{group.items.map(item => {
							const active = item.match(currentPath)
							const Icon = item.icon
							return (
								<Link
									key={item.href}
									href={item.href}
									aria-current={active ? 'page' : undefined}
									aria-label={collapsed ? item.label : undefined}
									title={collapsed ? item.label : undefined}
									className={cn(
										'group flex items-center gap-2 rounded-xl py-2.5 text-sm transition-colors focus-visible:outline-2 focus-visible:outline-offset-[-2px] focus-visible:outline-[var(--brand)]',
										collapsed ? 'justify-center px-0' : 'px-2'
									)}
									style={{
										background: active ? 'var(--nav-active-bg, rgba(61, 184, 168, 0.12))' : 'transparent',
										color: active ? 'var(--brand-ink, #1f7a6e)' : 'var(--admin-text-secondary, #6b7b79)',
										borderLeft: active ? '4px solid var(--brand, #3db8a8)' : '4px solid transparent'
									}}>
									<Icon className='h-4 w-4 shrink-0' aria-hidden='true' />
									<span className={cn('min-w-0 flex-1 truncate', collapsed && 'sr-only')}>{item.label}</span>
									{item.status === 'deferred' && !collapsed ? (
										<span className='text-[10px]' style={{ color: 'var(--admin-text-tertiary, #9eadab)' }}>
											后续
										</span>
									) : null}
								</Link>
							)
						})}
					</div>
				))}
			</nav>
		</aside>
	)
}
