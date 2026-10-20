'use client'

import { useCallback, useEffect, useLayoutEffect, useMemo, useRef, useState, type KeyboardEvent as ReactKeyboardEvent, type ReactNode } from 'react'
import { createPortal } from 'react-dom'
import { motion } from 'motion/react'

import { cn } from '@/lib/utils'
import { getOverlayPortalRoot } from './portal-root'
import { getFocusableElements, useOverlay } from '@/hooks/use-overlay'

/** Domain-neutral command description (navigation-overlay §6.8). */
export interface Uiv2ContextAction {
	id: string
	label: string
	/** Optional leading icon (parity with the legacy context menu). */
	icon?: ReactNode
	/** Ordering/substitution group; a divider is drawn between groups. */
	group?: 'open' | 'edit' | 'organize' | 'danger'
	disabled?: boolean
	/** Shown via `title` so a disabled item still explains itself. */
	disabledReason?: string
	variant?: 'default' | 'danger'
	run: () => void
}

export interface MenuAnchorPoint {
	x: number
	y: number
}

export interface MenuPlacement {
	x: number
	y: number
	flippedX: boolean
	flippedY: boolean
}

/**
 * Anchor-aware placement: flip away from the viewport edge, then clamp so the
 * menu never leaves the viewport (navigation-overlay §6.4).
 */
export function computeMenuPlacement(
	anchor: MenuAnchorPoint,
	menu: { width: number; height: number },
	viewport: { width: number; height: number },
	gap = 8
): MenuPlacement {
	let x = anchor.x
	let y = anchor.y
	let flippedX = false
	let flippedY = false

	if (x + menu.width > viewport.width - gap) {
		x = anchor.x - menu.width
		flippedX = true
	}
	if (y + menu.height > viewport.height - gap) {
		y = anchor.y - menu.height
		flippedY = true
	}

	x = Math.min(Math.max(gap, x), Math.max(gap, viewport.width - menu.width - gap))
	y = Math.min(Math.max(gap, y), Math.max(gap, viewport.height - menu.height - gap))

	return { x, y, flippedX, flippedY }
}

/**
 * Native menus stay authoritative on text, links, inputs, code and images
 * (navigation-overlay §6.1). Consumers must not call `preventDefault` for these.
 */
export function shouldUseNativeContextMenu(target: EventTarget | null): boolean {
	if (!(target instanceof Element)) return false
	return Boolean(
		target.closest(
			'a[href], input, textarea, select, option, code, pre, kbd, img, video, audio, [contenteditable="true"], [data-native-context-menu]'
		)
	)
}

const GROUP_ORDER: Array<NonNullable<Uiv2ContextAction['group']>> = ['open', 'edit', 'organize', 'danger']

/** `useLayoutEffect` warns during SSR; this component portals in the browser. */
const useIsomorphicLayoutEffect = typeof window !== 'undefined' ? useLayoutEffect : useEffect

function groupActions(actions: Uiv2ContextAction[]) {
	const buckets = new Map<string, Uiv2ContextAction[]>()
	// A destructive action must never render first just because `group` was omitted.
	const resolveGroup = (action: Uiv2ContextAction) => action.group ?? (action.variant === 'danger' ? 'danger' : 'open')
	for (const action of actions) buckets.set(resolveGroup(action), [...(buckets.get(resolveGroup(action)) ?? []), action])
	return GROUP_ORDER.map(group => buckets.get(group)).filter((items): items is Uiv2ContextAction[] => Boolean(items && items.length))
}

export interface Uiv2ContextMenuProps {
	open: boolean
	onClose: () => void
	actions: Uiv2ContextAction[]
	/** Pointer coordinates (right-click). */
	position?: MenuAnchorPoint | null
	/** Element anchor for keyboard / more-button activation. */
	anchor?: HTMLElement | null
	/** Accessible name of the menu. */
	label?: string
}

/**
 * Desktop object-scoped command menu. Right-click is only one entry point —
 * `useContextMenuTrigger` also exposes a "more" button and Shift+F10 / Menu key.
 */
export function Uiv2ContextMenu({ open, onClose, actions, position, anchor, label = '对象操作' }: Uiv2ContextMenuProps) {
	const [mounted, setMounted] = useState(false)
	useEffect(() => setMounted(true), [])

	const [placement, setPlacement] = useState<MenuPlacement>({ x: position?.x ?? 0, y: position?.y ?? 0, flippedX: false, flippedY: false })
	const [activeIndex, setActiveIndex] = useState(0)
	const menuRef = useRef<HTMLDivElement | null>(null)

	const groups = useMemo(() => groupActions(actions), [actions])
	const flatActions = useMemo(() => groups.flat(), [groups])

	const overlay = useOverlay({
		open: open && mounted,
		onClose,
		lockScroll: false,
		isolateBackground: false,
		// WAI-ARIA menu pattern: focus lands on the first enabled item.
		getInitialFocus: () => getFocusableElements(menuRef.current)[0] ?? menuRef.current
	})

	// Reset the roving index only when the menu opens. Callers build `actions`
	// inline, so depending on the array identity would reset the highlight (and
	// make Enter run the wrong item) on any unrelated parent re-render.
	useEffect(() => {
		if (!open) return
		const flattened = groupActions(actions).flat()
		const firstEnabled = flattened.findIndex(action => !action.disabled)
		setActiveIndex(firstEnabled < 0 ? 0 : firstEnabled)
		// eslint-disable-next-line react-hooks/exhaustive-deps
	}, [open])

	// Outside dismissal mirrors the legacy document listeners: a left click still
	// activates whatever is under the cursor, and a right click elsewhere closes
	// this menu while letting the native/contextmenu flow proceed.
	useEffect(() => {
		if (!open) return
		const handleDocumentClick = (event: MouseEvent) => {
			if (menuRef.current?.contains(event.target as Node)) return
			onClose()
		}
		const handleDocumentContextMenu = () => onClose()
		document.addEventListener('click', handleDocumentClick)
		document.addEventListener('contextmenu', handleDocumentContextMenu)
		return () => {
			document.removeEventListener('click', handleDocumentClick)
			document.removeEventListener('contextmenu', handleDocumentContextMenu)
		}
	}, [open, onClose])

	useIsomorphicLayoutEffect(() => {
		if (!open || !mounted) return
		const menu = menuRef.current
		if (!menu) return
		const rect = menu.getBoundingClientRect()
		const viewport = { width: window.innerWidth, height: window.innerHeight }
		// An explicit pointer position always wins over the element anchor.
		const anchorPoint =
			position ??
			(anchor
				? (() => {
						const box = anchor.getBoundingClientRect()
						return { x: box.left, y: box.bottom }
					})()
				: { x: 0, y: 0 })

		setPlacement(computeMenuPlacement(anchorPoint, { width: rect.width, height: rect.height }, viewport))
	}, [open, mounted, anchor, position, flatActions.length])

	// Focus by action id: the focusable list is dense while `flatActions` keeps
	// disabled entries, so positional indexing silently desyncs.
	const focusAction = useCallback((actionId: string) => {
		const escape = typeof CSS !== 'undefined' && typeof CSS.escape === 'function' ? CSS.escape(actionId) : actionId.replace(/["\\]/g, '\\$&')
		const node = menuRef.current?.querySelector<HTMLElement>(`[data-action-id="${escape}"]`)
		node?.focus()
	}, [])

	const move = useCallback(
		(direction: 1 | -1 | 'first' | 'last') => {
			if (flatActions.length === 0) return
			const enabled = flatActions.map((action, index) => ({ action, index })).filter(entry => !entry.action.disabled)
			if (enabled.length === 0) return

			if (direction === 'first') {
				setActiveIndex(enabled[0].index)
				focusAction(enabled[0].action.id)
				return
			}
			if (direction === 'last') {
				const last = enabled[enabled.length - 1]
				setActiveIndex(last.index)
				focusAction(last.action.id)
				return
			}

			const current = enabled.findIndex(entry => entry.index === activeIndex)
			const next = (current + direction + enabled.length) % enabled.length
			setActiveIndex(enabled[next].index)
			focusAction(enabled[next].action.id)
		},
		[activeIndex, flatActions, focusAction]
	)

	const runAction = useCallback(
		(action: Uiv2ContextAction) => {
			if (action.disabled) return
			// Run first, then close: the legacy menu behaved this way and some
			// actions open another surface.
			action.run()
			onClose()
		},
		[onClose]
	)

	const handleKeyDown = useCallback(
		(event: ReactKeyboardEvent<HTMLDivElement>) => {
			switch (event.key) {
				case 'ArrowDown':
					event.preventDefault()
					move(1)
					break
				case 'ArrowUp':
					event.preventDefault()
					move(-1)
					break
				case 'Home':
					event.preventDefault()
					move('first')
					break
				case 'End':
					event.preventDefault()
					move('last')
					break
				case 'Enter':
				case ' ':
					event.preventDefault()
					if (flatActions[activeIndex]) runAction(flatActions[activeIndex])
					break
				case 'Tab':
					event.preventDefault()
					onClose()
					break
				default:
					break
			}
		},
		[activeIndex, flatActions, move, onClose, runAction]
	)

	if (!mounted) return null

	if (flatActions.length === 0) return null

	let cursor = -1

	return createPortal(
		<>
			{open && (
				<>
					<motion.div
						ref={node => {
							menuRef.current = node
							overlay.containerRef.current = node
						}}
						role='menu'
						aria-label={label}
						data-testid='uiv2-context-menu'
						data-flipped-x={String(placement.flippedX)}
						data-flipped-y={String(placement.flippedY)}
						onKeyDown={handleKeyDown}
						initial={overlay.prefersReducedMotion ? false : { opacity: 0, scale: 0.97 }}
						animate={{ opacity: 1, scale: 1 }}
						transition={{ duration: overlay.prefersReducedMotion ? 0 : 0.12 }}
						className={cn('fixed min-w-0 overflow-hidden')}
						style={{
							top: placement.y,
							left: placement.x,
							zIndex: overlay.zIndex,
							width: '232px',
							maxHeight: 'min(70vh, 420px)',
							overflowY: 'auto',
							padding: '4px',
							borderRadius: 'var(--ui-radius-md, 12px)',
							border: '1px solid var(--admin-border, rgba(45, 62, 60, 0.12))',
							background: 'var(--admin-surface, #ffffff)',
							color: 'var(--admin-text-primary, #2d3e3c)',
							boxShadow: 'var(--ui-shadow-lg, 0 12px 32px rgba(0, 0, 0, 0.12))'
						}}>
						{groups.map((items, groupIndex) => (
							<div key={items[0]?.group ?? groupIndex}>
								{groupIndex > 0 ? (
									<div role='separator' style={{ height: 1, margin: '4px 0', background: 'var(--admin-divider, rgba(45, 62, 60, 0.08))' }} />
								) : null}
								{items.map(action => {
									cursor += 1
									const index = cursor
									const isDanger = action.variant === 'danger' || action.group === 'danger'
									return (
										<button
											key={action.id}
											type='button'
											role='menuitem'
											disabled={action.disabled}
											title={action.disabled ? action.disabledReason : undefined}
											tabIndex={-1}
											data-action-id={action.id}
											data-active={String(index === activeIndex)}
											onClick={() => runAction(action)}
											onMouseEnter={() => setActiveIndex(index)}
											className='flex w-full items-center gap-2 rounded-lg px-3 text-left text-[13px] transition-colors disabled:cursor-not-allowed disabled:opacity-40 focus-visible:outline-2 focus-visible:outline-offset-[-2px] focus-visible:outline-[var(--brand,#3db8a8)]'
											style={{
												height: '38px',
												color: isDanger ? '#c0392b' : 'var(--admin-text-primary, #2d3e3c)',
												background: index === activeIndex ? 'var(--nav-active-bg, rgba(61, 184, 168, 0.12))' : 'transparent'
											}}>
											{action.icon ? <span className='shrink-0 opacity-70'>{action.icon}</span> : null}
											{action.label}
										</button>
									)
								})}
							</div>
						))}
					</motion.div>
				</>
			)}
		</>,
		getOverlayPortalRoot()
	)
}

export interface UseContextMenuTriggerOptions {
	actions: Uiv2ContextAction[]
	disabled?: boolean
}

export interface UseContextMenuTriggerResult {
	open: boolean
	triggerProps: {
		onContextMenu: (event: React.MouseEvent<HTMLElement>) => void
		onKeyDown: (event: ReactKeyboardEvent<HTMLElement>) => void
	}
	moreButtonProps: {
		type: 'button'
		onClick: (event: React.MouseEvent<HTMLElement>) => void
		'aria-haspopup': 'menu'
		'aria-expanded': boolean
		disabled: boolean
	}
	menuProps: Uiv2ContextMenuProps
}

/**
 * Wires the three entry points required by the spec: pointer right-click,
 * Shift+F10 / Menu key on the focused object, and a visible "more" button.
 * Returns props only — the consumer decides layout and markup ownership.
 */
export function useContextMenuTrigger({ actions, disabled = false }: UseContextMenuTriggerOptions): UseContextMenuTriggerResult {
	const [state, setState] = useState<{ open: boolean; position: MenuAnchorPoint | null; anchor: HTMLElement | null }>({
		open: false,
		position: null,
		anchor: null
	})

	const close = useCallback(() => setState(previous => ({ ...previous, open: false })), [])

	const openAtPointer = useCallback((event: React.MouseEvent<HTMLElement>) => {
		if (disabled) return
		if (shouldUseNativeContextMenu(event.target)) return
		event.preventDefault()
		setState({ open: true, position: { x: event.clientX, y: event.clientY }, anchor: null })
	}, [disabled])

	const openAtAnchor = useCallback((element: HTMLElement) => {
		if (disabled) return
		setState({ open: true, position: null, anchor: element })
	}, [disabled])

	return {
		open: state.open,
		triggerProps: {
			onContextMenu: openAtPointer,
			onKeyDown: event => {
				// Shift+F10 and the dedicated Menu key open at the focused object.
				if (event.key === 'ContextMenu' || (event.shiftKey && event.key === 'F10')) {
					event.preventDefault()
					openAtAnchor(event.currentTarget)
				}
			}
		},
		moreButtonProps: {
			type: 'button',
			onClick: event => openAtAnchor(event.currentTarget.parentElement ?? event.currentTarget),
			'aria-haspopup': 'menu',
			'aria-expanded': state.open,
			disabled
		},
		menuProps: {
			open: state.open,
			onClose: close,
			actions,
			position: state.position,
			anchor: state.anchor
		}
	}
}
