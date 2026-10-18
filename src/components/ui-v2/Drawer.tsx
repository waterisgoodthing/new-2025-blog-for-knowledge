'use client'

import { useEffect, useRef, useState, type ReactNode, type RefObject } from 'react'
import { createPortal } from 'react-dom'
import { AnimatePresence, motion } from 'motion/react'
import { X } from 'lucide-react'

import { cn } from '@/lib/utils'
import { getFocusableElements, useOverlay } from '@/hooks/use-overlay'

export type Uiv2DrawerSide = 'left' | 'right' | 'bottom'

export interface Uiv2DrawerProps {
	open: boolean
	onClose: () => void
	/** Accessible name; rendered as the drawer header. */
	title: string
	description?: string
	children?: ReactNode
	/** Fixed action row; the body scrolls between header and footer. */
	footer?: ReactNode
	/** left = navigation, right = settings/filters/detail, bottom = mobile sheet. */
	side?: Uiv2DrawerSide
	/** Width for left/right, height for bottom. Defaults to 440px / 70vh. */
	size?: string
	closeOnBackdropClick?: boolean
	closeOnEscape?: boolean
	initialFocusRef?: RefObject<HTMLElement | null>
	className?: string
}

const SAFE_AREA: Record<Uiv2DrawerSide, Record<string, string>> = {
	left: { paddingLeft: 'env(safe-area-inset-left, 0px)', paddingBottom: 'env(safe-area-inset-bottom, 0px)' },
	right: { paddingRight: 'env(safe-area-inset-right, 0px)', paddingBottom: 'env(safe-area-inset-bottom, 0px)' },
	bottom: { paddingBottom: 'env(safe-area-inset-bottom, 0px)' }
}

const SURFACE_POSITION: Record<Uiv2DrawerSide, Record<string, string | number>> = {
	left: { top: 0, left: 0, bottom: 0 },
	right: { top: 0, right: 0, bottom: 0 },
	bottom: { left: 0, right: 0, bottom: 0 }
}

/**
 * Drawer: navigation (left), settings/filters/supporting detail (right), or a
 * mobile sheet (bottom). Behaviour comes from `useOverlay`.
 */
export function Uiv2Drawer({
	open,
	onClose,
	title,
	description,
	children,
	footer,
	side = 'right',
	size,
	closeOnBackdropClick = true,
	closeOnEscape = true,
	initialFocusRef,
	className
}: Uiv2DrawerProps) {
	const [mounted, setMounted] = useState(false)
	useEffect(() => setMounted(true), [])
	const bodyRef = useRef<HTMLDivElement | null>(null)

	// `mounted` gates the portal, so the overlay must only become active once the
	// surface ref exists — otherwise the focus-trap effect runs against null and
	// never re-runs (deps unchanged).
	const overlay = useOverlay({
		open: open && mounted,
		onClose,
		closeOnBackdropClick,
		closeOnEscape,
		initialFocusRef,
		// Prefer the first interactive element of the body over the header close button.
		getInitialFocus: () => getFocusableElements(bodyRef.current)[0] ?? null
	})

	if (!mounted) return null

	const isBottom = side === 'bottom'
	const resolvedSize = size ?? (isBottom ? '70vh' : '440px')
	const hiddenTransform = side === 'left' ? { x: '-100%' } : side === 'right' ? { x: '100%' } : { y: '100%' }
	const duration = overlay.prefersReducedMotion ? 0 : 0.2

	return createPortal(
		<AnimatePresence>
			{open && (
				<motion.div
					key='uiv2-drawer-backdrop'
					initial={{ opacity: 0 }}
					animate={{ opacity: 1 }}
					exit={{ opacity: 0 }}
					transition={{ duration: overlay.prefersReducedMotion ? 0 : 0.15 }}
					onPointerDown={overlay.handleBackdropPointerDown}
					onClick={overlay.handleBackdropClick}
					data-testid='uiv2-drawer-backdrop'
					style={{
						position: 'fixed',
						inset: 0,
						zIndex: overlay.backdropZIndex,
						background: 'rgba(26, 19, 17, 0.32)',
						backdropFilter: 'blur(4px)',
						WebkitBackdropFilter: 'blur(4px)'
					}}>
					<motion.div
						ref={overlay.containerRef}
						role='dialog'
						aria-modal='true'
						aria-labelledby={overlay.titleId}
						aria-describedby={description ? overlay.descriptionId : undefined}
						data-testid='uiv2-drawer'
						data-side={side}
						data-reduced-motion={String(overlay.prefersReducedMotion)}
						initial={overlay.prefersReducedMotion ? false : hiddenTransform}
						animate={isBottom ? { y: 0 } : { x: 0 }}
						exit={overlay.prefersReducedMotion ? undefined : hiddenTransform}
						transition={{ duration, ease: [0.4, 0, 0.2, 1] }}
						className={cn('flex min-w-0 flex-col overflow-hidden', className)}
						style={{
							position: 'fixed',
							...SURFACE_POSITION[side],
							...SAFE_AREA[side],
							zIndex: overlay.zIndex,
							[isBottom ? 'height' : 'width']: resolvedSize,
							[isBottom ? 'width' : 'maxWidth']: isBottom ? undefined : '100vw',
							borderTopLeftRadius: isBottom ? 'var(--ui-radius-xl, 24px)' : undefined,
							borderTopRightRadius: isBottom ? 'var(--ui-radius-xl, 24px)' : undefined,
							borderLeft: side === 'right' ? '1px solid var(--admin-border, rgba(45, 62, 60, 0.12))' : undefined,
							borderRight: side === 'left' ? '1px solid var(--admin-border, rgba(45, 62, 60, 0.12))' : undefined,
							borderTop: isBottom ? '1px solid var(--admin-border, rgba(45, 62, 60, 0.12))' : undefined,
							background: 'var(--admin-surface, #ffffff)',
							color: 'var(--admin-text-primary, #2d3e3c)',
							boxShadow: 'var(--ui-shadow-lg, 0 12px 32px rgba(0, 0, 0, 0.12))'
						}}>
						<header
							className='flex shrink-0 items-start justify-between gap-3 border-b px-5 py-4'
							style={{ borderColor: 'var(--admin-divider, rgba(45, 62, 60, 0.08))' }}>
							<div className='min-w-0'>
								<h2 id={overlay.titleId} className='text-base font-semibold tracking-tight break-words'>
									{title}
								</h2>
								{description ? (
									<p id={overlay.descriptionId} className='mt-1 text-xs break-words' style={{ color: 'var(--admin-text-secondary, #6b7b79)' }}>
										{description}
									</p>
								) : null}
							</div>
							<button
								type='button'
								onClick={overlay.requestClose}
								aria-label='关闭'
								className='shrink-0 rounded-lg p-1.5 transition-colors focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--brand,#3db8a8)]'
								style={{ color: 'var(--admin-text-tertiary, #9eadab)' }}>
								<X size={18} aria-hidden='true' />
							</button>
						</header>

						<div ref={bodyRef} className='min-h-0 flex-1 overflow-y-auto px-5 py-4 text-sm'>
							{children}
						</div>

						{footer ? (
							<footer
								className='flex shrink-0 flex-wrap items-center justify-end gap-2 border-t px-5 py-3'
								style={{ borderColor: 'var(--admin-divider, rgba(45, 62, 60, 0.08))' }}>
								{footer}
							</footer>
						) : null}
					</motion.div>
				</motion.div>
			)}
		</AnimatePresence>,
		document.body
	)
}
