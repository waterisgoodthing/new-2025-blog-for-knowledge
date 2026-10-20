/**
 * Shared overlay portal host.
 *
 * Overlays must NOT portal inside the page tree: the public root layout wraps
 * every page in `<main className='relative z-10'>`, which creates a stacking
 * context. A `z-index: 1300` overlay portalled inside it would still paint
 * below sibling chrome such as the legacy `z-40` / `z-50` navigations.
 *
 * The host therefore lives directly under `<body>`, a sibling of the
 * `[data-overlay-background-root]` subtree that `useOverlay` marks `inert`.
 * It is created once and intentionally never removed: dropping it while an
 * overlay is still open would orphan the portalled node.
 */
export const APP_PORTAL_ROOT_ID = 'uiv2-portal-root'

let host: HTMLElement | null = null

/** Returns the shared portal host, creating it under `<body>` on first use. */
export function ensureOverlayPortalHost(): HTMLElement | null {
	if (typeof document === 'undefined') return null
	if (host && host.isConnected) return host

	const existing = document.getElementById(APP_PORTAL_ROOT_ID)
	if (existing) {
		host = existing
		return host
	}

	const created = document.createElement('div')
	created.id = APP_PORTAL_ROOT_ID
	created.setAttribute('data-uiv2-portal-root', '')
	document.body.appendChild(created)
	host = created
	return host
}

/** Portal target for Modal / Drawer / ContextMenu. */
export function getOverlayPortalRoot(): HTMLElement {
	return ensureOverlayPortalHost() ?? document.body
}
