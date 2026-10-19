'use client'

/**
 * Shared overlay behaviour (Phase 2 / VSC-03).
 *
 * Composes the four things every overlay needs and none of the three legacy
 * primitives (`dialog-modal.tsx`, `drawer.tsx`, `context-menu.tsx`) do
 * consistently: focus containment + restoration, Escape dismissal, body scroll
 * locking with nesting, and a z-index stack.
 *
 * Deliberately framework-light: it renders nothing, so it is usable by Modal,
 * Drawer, ContextMenu and future primitives without inheriting their markup.
 */

import {
	useCallback,
	useEffect,
	useId,
	useLayoutEffect,
	useRef,
	useState,
	type MouseEvent as ReactMouseEvent,
	type PointerEvent as ReactPointerEvent,
	type RefObject
} from 'react'

/** `useLayoutEffect` warns during SSR; overlays only run it in the browser. */
const useIsomorphicLayoutEffect = typeof window !== 'undefined' ? useLayoutEffect : useEffect

/**
 * Overlay stacking base. App chrome tops out at `z-50` (legacy sticky nav) and
 * the token scale uses 1000-1700 for global surfaces, so overlays start at 1300
 * and step by 10 per nesting level. Depth wins over layer: a Modal opened from a
 * Drawer must sit above it (navigation-overlay-context-actions.md §5.5).
 */
export const OVERLAY_Z_BASE = 1300
export const OVERLAY_Z_STEP = 10

const FOCUSABLE_SELECTOR = [
	'a[href]',
	'button:not([disabled])',
	'input:not([disabled]):not([type="hidden"])',
	'select:not([disabled])',
	'textarea:not([disabled])',
	'[tabindex]:not([tabindex="-1"])',
	'[contenteditable="true"]'
].join(',')

/* -------------------------------------------------------------------------- */
/* Stack                                                                      */
/* -------------------------------------------------------------------------- */

let openStack: string[] = []
const stackSubscribers = new Set<() => void>()

function commitStack(next: string[]) {
	openStack = next
	for (const notify of stackSubscribers) notify()
}

function depthOf(id: string): number {
	return openStack.indexOf(id)
}

/** @internal exported for tests only */
export function getOverlayStack(): readonly string[] {
	return openStack
}

/** @internal exported so tests can isolate cases */
export function resetOverlayState(): void {
	openStack = []
	scrollLockCount = 0
	savedBodyOverflow = ''
	inertCount = 0
	for (const root of inertedRoots) root.removeAttribute('inert')
	inertedRoots.clear()
	if (typeof document !== 'undefined') document.body.style.overflow = ''
}

/* -------------------------------------------------------------------------- */
/* Scroll lock (ref-counted so nested overlays cannot unlock early)            */
/* -------------------------------------------------------------------------- */

let scrollLockCount = 0
let savedBodyOverflow = ''

/* -------------------------------------------------------------------------- */
/* Portal root + background isolation                                          */
/* -------------------------------------------------------------------------- */

const BACKGROUND_ROOT_SELECTOR = '[data-overlay-background-root]'

let inertCount = 0
const inertedRoots = new Set<HTMLElement>()

function applyBackgroundInert() {
	if (typeof document === 'undefined') return
	inertCount += 1
	// Re-scan on every open: a background root that mounted while another
	// overlay was already open must still be isolated.
	for (const root of Array.from(document.querySelectorAll<HTMLElement>(BACKGROUND_ROOT_SELECTOR))) {
		if (inertedRoots.has(root)) continue
		root.setAttribute('inert', '')
		inertedRoots.add(root)
	}
}

function releaseBackgroundInert() {
	if (typeof document === 'undefined') return
	inertCount = Math.max(0, inertCount - 1)
	if (inertCount > 0) return
	for (const root of inertedRoots) root.removeAttribute('inert')
	inertedRoots.clear()
}

function lockBodyScroll() {
	if (typeof document === 'undefined') return
	if (scrollLockCount === 0) {
		savedBodyOverflow = document.body.style.overflow
		document.body.style.overflow = 'hidden'
	}
	scrollLockCount += 1
}

function unlockBodyScroll() {
	if (typeof document === 'undefined') return
	scrollLockCount = Math.max(0, scrollLockCount - 1)
	if (scrollLockCount === 0) document.body.style.overflow = savedBodyOverflow
}

/* -------------------------------------------------------------------------- */
/* Focus helpers                                                              */
/* -------------------------------------------------------------------------- */

/**
 * Visible-and-enabled focus candidates.
 *
 * Note: no `offsetParent`/`getClientRects` filtering on purpose. jsdom reports
 * zero layout for every node, so a layout-based filter would make the trap
 * untestable while adding little: overlays do not render `display:none` content.
 */
export interface FocusableOptions {
	/**
	 * Exclude `tabindex="-1"` candidates. Use this for Tab containment; use the
	 * default (focusable) for programmatic focus such as ARIA menu roving.
	 */
	tabbableOnly?: boolean
}

export function getFocusableElements(root: HTMLElement | null, options: FocusableOptions = {}): HTMLElement[] {
	if (!root) return []
	const { tabbableOnly = false } = options
	return Array.from(root.querySelectorAll<HTMLElement>(FOCUSABLE_SELECTOR)).filter(el => {
		if (el.hasAttribute('hidden')) return false
		if (el.getAttribute('aria-hidden') === 'true') return false
		if (el.closest('[inert]')) return false
		if (tabbableOnly && el.getAttribute('tabindex') === '-1') return false
		// jsdom has no layout engine (and no checkVisibility); browsers do.
		const checkVisibility = (el as HTMLElement & { checkVisibility?: (opts?: { checkVisibilityCSS?: boolean }) => boolean })
			.checkVisibility
		if (typeof checkVisibility === 'function' && !checkVisibility.call(el, { checkVisibilityCSS: true })) return false
		return true
	})
}

export interface UseFocusTrapOptions {
	active: boolean
	containerRef: RefObject<HTMLElement | null>
	/** Element that must receive focus on open; defaults to the first focusable. */
	initialFocusRef?: RefObject<HTMLElement | null>
	/**
	 * Lazy alternative to `initialFocusRef`, evaluated once on open. Lets a
	 * component prefer "first interactive element inside the content region"
	 * over chrome such as the header close button.
	 */
	getInitialFocus?: () => HTMLElement | null
	/** Return focus to whatever was focused before opening. Defaults to true. */
	restoreFocus?: boolean
	/**
	 * Bind the Tab containment listener. Only the topmost overlay may trap, or
	 * stacked overlays (portalled as siblings, so neither contains the other)
	 * would both fight over every Tab press.
	 */
	trapTab?: boolean
}

export interface UseFocusTrapResult {
	focusFirst: () => void
	focusLast: () => void
}

/**
 * Keeps Tab/Shift+Tab inside `containerRef` and restores focus on close.
 */
export function useFocusTrap({ active, containerRef, initialFocusRef, getInitialFocus, restoreFocus = true, trapTab = true }: UseFocusTrapOptions): UseFocusTrapResult {
	const previouslyFocusedRef = useRef<HTMLElement | null>(null)
	// Kept in a ref so a new closure each render cannot re-trigger the effect
	// (and steal focus back on every parent re-render).
	const getInitialFocusRef = useRef(getInitialFocus)
	getInitialFocusRef.current = getInitialFocus

	// Kept in a ref: putting it in the dependency array would re-run the effect
	// (and re-capture `previouslyFocusedRef`) whenever the caller's value flaps,
	// which silently loses the real trigger.
	const restoreFocusRef = useRef(restoreFocus)
	restoreFocusRef.current = restoreFocus

	useEffect(() => {
		if (!active || typeof document === 'undefined') return

		const activeElement = document.activeElement
		previouslyFocusedRef.current = activeElement instanceof HTMLElement ? activeElement : null

		const root = containerRef.current
		const target = initialFocusRef?.current ?? getInitialFocusRef.current?.() ?? getFocusableElements(root)[0] ?? root
		target?.focus()

		return () => {
			if (!restoreFocusRef.current) return
			// Only hand focus back if it is still ours. When a *lower* overlay is
			// closed while a child stays open, focus belongs to the child.
			const current = document.activeElement
			const focusEscaped = current instanceof HTMLElement && current !== document.body && root && !root.contains(current)
			if (focusEscaped) return

			const previous = previouslyFocusedRef.current
			if (previous && typeof previous.focus === 'function' && document.contains(previous)) {
				previous.focus()
			}
		}
	}, [active, containerRef, initialFocusRef])

	const focusFirst = useCallback(() => {
		getFocusableElements(containerRef.current)[0]?.focus()
	}, [containerRef])

	const focusLast = useCallback(() => {
		const items = getFocusableElements(containerRef.current)
		items[items.length - 1]?.focus()
	}, [containerRef])

	useEffect(() => {
		if (!active || !trapTab || typeof document === 'undefined') return

		const handleKeyDown = (event: KeyboardEvent) => {
			if (event.key !== 'Tab') return
			const root = containerRef.current
			if (!root) return
			const items = getFocusableElements(root, { tabbableOnly: true })
			if (items.length === 0) {
				event.preventDefault()
				return
			}

			const first = items[0]
			const last = items[items.length - 1]
			const current = document.activeElement

			if (!root.contains(current as Node | null)) {
				event.preventDefault()
				;(event.shiftKey ? last : first).focus()
				return
			}
			if (event.shiftKey && current === first) {
				event.preventDefault()
				last.focus()
			} else if (!event.shiftKey && current === last) {
				event.preventDefault()
				first.focus()
			}
		}

		document.addEventListener('keydown', handleKeyDown)
		return () => document.removeEventListener('keydown', handleKeyDown)
	}, [active, containerRef, trapTab])

	return { focusFirst, focusLast }
}

/* -------------------------------------------------------------------------- */
/* Reduced motion                                                             */
/* -------------------------------------------------------------------------- */

const REDUCED_MOTION_QUERY = '(prefers-reduced-motion: reduce)'

export function usePrefersReducedMotion(): boolean {
	const [reduced, setReduced] = useState(false)

	useEffect(() => {
		if (typeof window === 'undefined' || typeof window.matchMedia !== 'function') return
		const query = window.matchMedia(REDUCED_MOTION_QUERY)
		setReduced(query.matches)
		const handleChange = (event: MediaQueryListEvent) => setReduced(event.matches)
		query.addEventListener?.('change', handleChange)
		return () => query.removeEventListener?.('change', handleChange)
	}, [])

	return reduced
}

/* -------------------------------------------------------------------------- */
/* Stack position                                                             */
/* -------------------------------------------------------------------------- */

export interface UseZIndexResult {
	depth: number
	zIndex: number
	backdropZIndex: number
	isTopmost: boolean
}

export function useZIndex(id: string, active: boolean): UseZIndexResult {
	const [depth, setDepth] = useState(-1)
	// `isTopmost` must be state: after a nested overlay closes, this overlay's
	// depth is unchanged, so a render-time derivation would never refresh it.
	const [topmost, setTopmost] = useState(false)

	// Must run before paint: a passive effect lets the first frame paint a Modal
	// backdrop below an open Drawer surface.
	useIsomorphicLayoutEffect(() => {
		if (!active || typeof window === 'undefined') {
			setDepth(-1)
			setTopmost(false)
			return
		}

		const sync = () => {
			const nextDepth = depthOf(id)
			setDepth(nextDepth)
			setTopmost(nextDepth >= 0 && nextDepth === openStack.length - 1)
		}

		commitStack([...openStack.filter(entry => entry !== id), id])
		sync()
		stackSubscribers.add(sync)

		return () => {
			stackSubscribers.delete(sync)
			commitStack(openStack.filter(entry => entry !== id))
			setDepth(-1)
			setTopmost(false)
		}
	}, [active, id])

	const safeDepth = depth < 0 ? 0 : depth

	return {
		depth,
		zIndex: OVERLAY_Z_BASE + safeDepth * OVERLAY_Z_STEP,
		backdropZIndex: OVERLAY_Z_BASE + safeDepth * OVERLAY_Z_STEP - 1,
		isTopmost: topmost
	}
}

/* -------------------------------------------------------------------------- */
/* useOverlay                                                                 */
/* -------------------------------------------------------------------------- */

export interface UseOverlayOptions {
	open: boolean
	onClose: () => void
	/** Escape dismisses the topmost overlay. Defaults to true. */
	closeOnEscape?: boolean
	/** Backdrop click dismisses. Defaults to true (forms with unsaved work pass false). */
	closeOnBackdropClick?: boolean
	/** Body scroll locking. Defaults to true. */
	lockScroll?: boolean
	/**
	 * Mark the AppShell background root `inert` while open. Defaults to true;
	 * non-modal surfaces such as a context menu pass false.
	 */
	isolateBackground?: boolean
	restoreFocus?: boolean
	initialFocusRef?: RefObject<HTMLElement | null>
	getInitialFocus?: () => HTMLElement | null
}

export interface UseOverlayResult {
	/** Attach to the overlay content element (the dialog/menu surface itself). */
	containerRef: RefObject<HTMLDivElement | null>
	zIndex: number
	backdropZIndex: number
	depth: number
	isTopmost: boolean
	prefersReducedMotion: boolean
	/** Stable ids for `aria-labelledby` / `aria-describedby`. */
	titleId: string
	descriptionId: string
	/** Attach to the backdrop (pointerdown) so drag-out releases cannot dismiss. */
	handleBackdropPointerDown: (event: ReactPointerEvent<HTMLElement>) => void
	/** Attach to the backdrop; closes only on a backdrop-originated click. */
	handleBackdropClick: (event: ReactMouseEvent<HTMLElement>) => void
	requestClose: () => void
}

export function useOverlay({
	open,
	onClose,
	closeOnEscape = true,
	closeOnBackdropClick = true,
	lockScroll = true,
	isolateBackground = true,
	restoreFocus = true,
	initialFocusRef,
	getInitialFocus
}: UseOverlayOptions): UseOverlayResult {
	const generatedId = useId()
	const overlayId = `overlay-${generatedId}`.replace(/[^a-zA-Z0-9_-]/g, '')
	const containerRef = useRef<HTMLDivElement | null>(null)

	const { zIndex, backdropZIndex, depth, isTopmost } = useZIndex(overlayId, open)
	const prefersReducedMotion = usePrefersReducedMotion()

	// Declared BEFORE the focus trap on purpose: on close, effect cleanups run in
	// declaration order, so the background `inert` must be released before focus
	// is restored. Otherwise `previous.focus()` is a no-op inside an inert
	// subtree and focus falls back to <body>.
	useEffect(() => {
		if (!open || !lockScroll) return
		lockBodyScroll()
		return () => unlockBodyScroll()
	}, [open, lockScroll])

	useEffect(() => {
		if (!open || !isolateBackground) return
		applyBackgroundInert()
		return () => releaseBackgroundInert()
	}, [open, isolateBackground])

	// Only the innermost overlay owns Tab containment (see `trapTab`); focus
	// restoration guards against non-LIFO closes inside `useFocusTrap`.
	useFocusTrap({ active: open, containerRef, initialFocusRef, getInitialFocus, restoreFocus, trapTab: isTopmost })

	const requestClose = useCallback(() => onClose(), [onClose])

	useEffect(() => {
		if (!open || !closeOnEscape || typeof document === 'undefined') return
		// Only the innermost overlay reacts, so stacked overlays close one at a time.
		if (!isTopmost) return
		const handleKeyDown = (event: KeyboardEvent) => {
			if (event.key !== 'Escape') return
			event.stopPropagation()
			onClose()
		}
		document.addEventListener('keydown', handleKeyDown)
		return () => document.removeEventListener('keydown', handleKeyDown)
	}, [open, closeOnEscape, isTopmost, onClose])

	// A press that starts inside the dialog and releases on the backdrop
	// produces a click on the backdrop (common ancestor). Arming on pointerdown
	// stops that from discarding unsaved form input.
	const backdropArmedRef = useRef(true)

	useEffect(() => {
		if (open) backdropArmedRef.current = true
	}, [open])

	const handleBackdropPointerDown = useCallback((event: ReactPointerEvent<HTMLElement>) => {
		backdropArmedRef.current = event.target === event.currentTarget
	}, [])

	const handleBackdropClick = useCallback(
		(event: ReactMouseEvent<HTMLElement>) => {
			// Bubbling from content must never dismiss.
			if (event.target !== event.currentTarget) return
			if (!backdropArmedRef.current) {
				backdropArmedRef.current = true
				return
			}
			if (!closeOnBackdropClick) return
			onClose()
		},
		[closeOnBackdropClick, onClose]
	)

	return {
		containerRef,
		zIndex,
		backdropZIndex,
		depth,
		isTopmost,
		prefersReducedMotion,
		titleId: `${overlayId}-title`,
		descriptionId: `${overlayId}-description`,
		handleBackdropPointerDown,
		handleBackdropClick,
		requestClose
	}
}
