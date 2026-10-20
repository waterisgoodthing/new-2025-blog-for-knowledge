'use client'

import { useEffect, useRef, useState, type ReactNode, type RefObject } from 'react'
import { createPortal } from 'react-dom'
import { AnimatePresence, motion } from 'motion/react'
import { X } from 'lucide-react'

import { cn } from '@/lib/utils'
import { getOverlayPortalRoot } from './portal-root'
import { getFocusableElements, useOverlay } from '@/hooks/use-overlay'

export type Uiv2ModalSize = 'confirm' | 'form' | 'preview'

const MODAL_WIDTH: Record<Uiv2ModalSize, string> = {
	confirm: '440px',
	form: '560px',
	preview: '720px'
}

export interface Uiv2ModalProps {
	open: boolean
	onClose: () => void
	/** Accessible name; rendered as the dialog title (required unless `bare`). */
	title?: string
	/** Optional supporting text, wired to `aria-describedby`. */
	description?: string
	children?: ReactNode
	/** Action row rendered after the body. */
	footer?: ReactNode
	/** Width preset: confirmation 440px / short form 560px / immersive preview 720px. */
	size?: Uiv2ModalSize
	/** Forms with unsaved work pass false (navigation-overlay §5.2). */
	closeOnBackdropClick?: boolean
	closeOnEscape?: boolean
	initialFocusRef?: RefObject<HTMLElement | null>
	className?: string
	/** Extra classes for the backdrop (legacy `overlayClassName` parity). */
	overlayClassName?: string
	/**
	 * Renders only the backdrop + caller markup, with no built-in header or close
	 * button. Used to migrate legacy `DialogModal` consumers without changing
	 * their visuals; `ariaLabel` then supplies the dialog name.
	 */
	bare?: boolean
	/** Accessible name for `bare` dialogs (which have no title header). */
	ariaLabel?: string
}

/**
 * Modal: blocking decision, confirmation, short form, or immersive preview.
 * Behaviour (focus, Escape, scroll lock, stacking) comes from `useOverlay`.
 */
export function Uiv2Modal({
	open,
	onClose,
	title,
	description,
	children,
	footer,
	size = 'confirm',
	closeOnBackdropClick = true,
	closeOnEscape = true,
	initialFocusRef,
	className,
	overlayClassName,
	bare = false,
	ariaLabel
}: Uiv2ModalProps) {
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
		// Prefer the first interactive element of the content over the chrome close button.
		getInitialFocus: () => getFocusableElements(bodyRef.current)[0] ?? null
	})

	if (!mounted) return null

	// Legacy-parity mode: keep the caller's own card markup and backdrop exactly
	// as it was, while inheriting the overlay behaviour (focus trap, scroll lock,
	// stacking, Escape, backdrop policy).
	if (bare) {
		return createPortal(
			<AnimatePresence>
				{open && (
					<motion.div
						key='uiv2-modal-bare-backdrop'
						initial={{ opacity: 0 }}
						animate={{ opacity: 1 }}
						exit={{ opacity: 0 }}
						transition={{ duration: overlay.prefersReducedMotion ? 0 : 0.15 }}
						onPointerDown={overlay.handleBackdropPointerDown}
						onClick={overlay.handleBackdropClick}
						data-testid='uiv2-modal-backdrop'
						className={cn('fixed inset-0 flex items-center justify-center bg-card p-4 backdrop-blur-xl', overlayClassName)}
						style={{ zIndex: overlay.backdropZIndex }}>
						<motion.div
							ref={overlay.containerRef}
							role='dialog'
							aria-modal='true'
							aria-label={ariaLabel ?? title}
							tabIndex={-1}
							data-testid='uiv2-modal'
							initial={overlay.prefersReducedMotion ? false : { opacity: 0, scale: 0.8, y: 20 }}
							animate={{ opacity: 1, scale: 1, y: 0 }}
							exit={overlay.prefersReducedMotion ? undefined : { opacity: 0, scale: 0.8, y: 20 }}
							transition={{ duration: overlay.prefersReducedMotion ? 0 : 0.2, ease: [0.4, 0, 0.2, 1] }}
							className={cn('static', className)}
							style={{ zIndex: overlay.zIndex }}>
							{children}
						</motion.div>
					</motion.div>
				)}
			</AnimatePresence>,
			getOverlayPortalRoot()
		)
	}

	return createPortal(
		<AnimatePresence>
			{open && (
				<motion.div
					key='uiv2-modal-backdrop'
					initial={{ opacity: 0 }}
					animate={{ opacity: 1 }}
					exit={{ opacity: 0 }}
					transition={{ duration: overlay.prefersReducedMotion ? 0 : 0.15 }}
					onPointerDown={overlay.handleBackdropPointerDown}
					onClick={overlay.handleBackdropClick}
					data-testid='uiv2-modal-backdrop'
					style={{
						position: 'fixed',
						inset: 0,
						zIndex: overlay.backdropZIndex,
						display: 'flex',
						alignItems: 'center',
						justifyContent: 'center',
						padding: '16px',
						background: 'rgba(26, 19, 17, 0.32)',
						backdropFilter: 'blur(4px)',
						WebkitBackdropFilter: 'blur(4px)'
					}}>
					<motion.div
						ref={overlay.containerRef}
						role='dialog'
						aria-modal='true'
						aria-labelledby={title ? overlay.titleId : undefined}
						aria-label={title ? undefined : ariaLabel}
						aria-describedby={description ? overlay.descriptionId : undefined}
						data-testid='uiv2-modal'
						data-size={size}
						data-reduced-motion={String(overlay.prefersReducedMotion)}
						initial={overlay.prefersReducedMotion ? false : { opacity: 0, scale: 0.96, y: 8 }}
						animate={{ opacity: 1, scale: 1, y: 0 }}
						exit={overlay.prefersReducedMotion ? undefined : { opacity: 0, scale: 0.96, y: 8 }}
						transition={{ duration: overlay.prefersReducedMotion ? 0 : 0.2, ease: [0.4, 0, 0.2, 1] }}
						className={cn('flex max-h-[calc(100vh-32px)] min-w-0 flex-col overflow-hidden', className)}
						style={{
							position: 'relative',
							zIndex: overlay.zIndex,
							width: '100%',
							maxWidth: MODAL_WIDTH[size],
							borderRadius: 'var(--ui-radius-lg, 16px)',
							border: '1px solid var(--admin-border, rgba(45, 62, 60, 0.12))',
							background: 'var(--admin-surface, #ffffff)',
							color: 'var(--admin-text-primary, #2d3e3c)',
							boxShadow: 'var(--ui-shadow-lg, 0 12px 32px rgba(0, 0, 0, 0.12))'
						}}>
						{title ? (
						<header className='min-w-0 px-6 pt-6 pb-2'>
							<h2 id={overlay.titleId} className='text-base font-semibold tracking-tight break-words'>
								{title}
							</h2>
							{description ? (
								<p id={overlay.descriptionId} className='mt-1 text-sm break-words' style={{ color: 'var(--admin-text-secondary, #6b7b79)' }}>
									{description}
								</p>
							) : null}
						</header>
						) : null}

						{children ? (
							<div ref={bodyRef} className='min-w-0 overflow-y-auto px-6 py-3 text-sm'>
								{children}
							</div>
						) : null}

						{footer ? (
							<footer
								className='flex flex-wrap items-center justify-end gap-2 border-t px-6 py-4'
								style={{ borderColor: 'var(--admin-divider, rgba(45, 62, 60, 0.08))' }}>
								{footer}
							</footer>
						) : null}

						{/* Close stays last in DOM so initial focus lands on real content, not "close". */}
						<button
							type='button'
							onClick={overlay.requestClose}
							aria-label='关闭'
							className='absolute top-4 right-4 rounded-lg p-1.5 transition-colors focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--brand,#3db8a8)]'
							style={{ color: 'var(--admin-text-tertiary, #9eadab)' }}>
							<X size={18} aria-hidden='true' />
						</button>
					</motion.div>
				</motion.div>
			)}
		</AnimatePresence>,
		getOverlayPortalRoot()
	)
}
