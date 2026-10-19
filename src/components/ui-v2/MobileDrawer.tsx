'use client'

import Link from 'next/link'
import { useEffect, useState, type ReactNode } from 'react'
import { Menu } from 'lucide-react'

import { cn } from '@/lib/utils'
import { Uiv2Drawer } from './Drawer'
import type { Uiv2NavGroup } from './nav-model'

export const MOBILE_DRAWER_ID = 'uiv2-mobile-drawer'
export const MOBILE_TOPBAR_HEIGHT = 56

export interface MobileDrawerProps {
	groups: Uiv2NavGroup[]
	currentPath: string
	/** Topbar centre label override; defaults to the matched destination. */
	title?: string
	/** Accessible name of the drawer. */
	drawerLabel?: string
	/** Trailing topbar slot (e.g. a "首页" link). */
	action?: ReactNode
	className?: string
}

/**
 * Mobile navigation (VSC-11): a 56px topbar with a hamburger that opens the
 * shared Phase 2 `Uiv2Drawer` from the right.
 *
 * All focus trapping, Escape handling, scroll locking and focus restoration is
 * delegated to `Uiv2Drawer` — this component only owns the trigger, the link
 * list and "close on route change".
 */
export function MobileDrawer({ groups, currentPath, title, drawerLabel = '导航菜单', action, className }: MobileDrawerProps) {
	const [open, setOpen] = useState(false)

	// A completed navigation always leaves the drawer closed.
	useEffect(() => {
		setOpen(false)
	}, [currentPath])

	// Growing past the mobile breakpoint hides the trigger but the portalled
	// dialog would otherwise stay open with no way to reach it.
	useEffect(() => {
		if (typeof window === 'undefined' || typeof window.matchMedia !== 'function') return
		const query = window.matchMedia('(min-width: 768px)')
		const handleChange = (event: MediaQueryListEvent) => {
			if (event.matches) setOpen(false)
		}
		query.addEventListener?.('change', handleChange)
		return () => query.removeEventListener?.('change', handleChange)
	}, [])

	const currentLabel = title ?? groups.flatMap(group => group.items).find(item => item.match(currentPath))?.label ?? ''

	return (
		<div className={cn('md:hidden', className)}>
			<header
				className='sticky top-0 z-10 flex items-center justify-between gap-3 rounded-b-xl border-b px-3'
				style={{
					height: MOBILE_TOPBAR_HEIGHT,
					background: 'var(--nav-glass-bg, rgba(255, 255, 255, 0.8))',
					borderColor: 'var(--admin-border, rgba(45, 62, 60, 0.12))',
					backdropFilter: 'var(--nav-blur, blur(20px))',
					WebkitBackdropFilter: 'var(--nav-blur, blur(20px))'
				}}>
				<button
					type='button'
					onClick={() => setOpen(true)}
					aria-expanded={open}
					aria-haspopup='dialog'
					aria-controls={MOBILE_DRAWER_ID}
					aria-label='打开导航菜单'
					className='inline-flex h-9 w-9 shrink-0 items-center justify-center rounded-lg transition-colors focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--brand)]'
					style={{ color: 'var(--admin-text-primary, #2d3e3c)' }}>
					<Menu size={18} aria-hidden='true' />
				</button>

				<p className='min-w-0 flex-1 truncate text-center text-sm font-semibold' style={{ color: 'var(--admin-text-primary, #2d3e3c)' }}>
					{currentLabel}
				</p>

				<div className='flex shrink-0 items-center'>{action}</div>
			</header>

			<Uiv2Drawer
				open={open}
				onClose={() => setOpen(false)}
				id={MOBILE_DRAWER_ID}
				title='导航'
				description={drawerLabel}
				side='right'
				size='min(320px, 86vw)'
				footer={
					<button
						type='button'
						onClick={() => setOpen(false)}
						className='rounded-xl px-4 py-2 text-sm font-medium text-white'
						style={{ background: 'var(--brand, #3db8a8)', minHeight: 40 }}>
						关闭导航
					</button>
				}>
				<nav aria-label={drawerLabel} className='flex flex-col gap-4'>
					{groups.map(group => (
						<div key={group.title} className='flex flex-col gap-1'>
							<p className='px-2 text-[11px] font-medium tracking-wide' style={{ color: 'var(--admin-text-tertiary, #9eadab)' }}>
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
										className='flex items-center gap-2 rounded-xl px-2 py-2.5 text-sm transition-colors focus-visible:outline-2 focus-visible:outline-offset-[-2px] focus-visible:outline-[var(--brand)]'
										style={{
											minHeight: 44,
											background: active ? 'var(--nav-active-bg, rgba(61, 184, 168, 0.12))' : 'transparent',
											color: active ? 'var(--brand-ink, #1f7a6e)' : 'var(--admin-text-secondary, #6b7b79)'
										}}>
										<Icon className='h-4 w-4 shrink-0' aria-hidden='true' />
										<span className='min-w-0 flex-1 truncate'>{item.label}</span>
									</Link>
								)
							})}
						</div>
					))}
				</nav>
			</Uiv2Drawer>
		</div>
	)
}
