import { ClipboardCheck, Compass, Home, Info, MessageSquare, NotebookPen, ScrollText } from 'lucide-react'
import type { LucideIcon } from 'lucide-react'

/**
 * Shared, presentational navigation model for the Phase 3 navigation surfaces.
 *
 * The item list is the single source of truth for public destinations; it is
 * derived from the existing `vertical-nav.tsx` / `mobile-nav.tsx` links. No
 * route is added, removed or renamed here.
 */
export interface Uiv2NavItem {
	href: string
	label: string
	icon: LucideIcon
	/** Active-route predicate; mirrors the predicates already used by the legacy nav. */
	match: (pathname: string) => boolean
	/** Optional capability marker (`deferred` renders a "后续" hint). */
	status?: string
}

export interface Uiv2NavGroup {
	title: string
	items: Uiv2NavItem[]
}

/**
 * Top-navigation entry: a single item renders as a direct link, multiple items
 * render as a disclosure dropdown.
 */
export interface Uiv2TopNavEntry {
	key: string
	label: string
	items: Uiv2NavItem[]
}

const exact = (href: string) => (pathname: string) => pathname === href
const under = (href: string) => (pathname: string) => pathname === href || pathname.startsWith(`${href}/`)

export const PUBLIC_NAV_HOME: Uiv2NavItem = { href: '/', label: '首页', icon: Home, match: exact('/') }

export const PUBLIC_NAV_CONTENT: Uiv2NavItem[] = [
	{ href: '/blog', label: '博客', icon: ScrollText, match: under('/blog') },
	{ href: '/notes', label: '笔记', icon: NotebookPen, match: under('/notes') },
	{ href: '/mistakes', label: '错题', icon: ClipboardCheck, match: under('/mistakes') }
]

export const PUBLIC_NAV_EXPLORE: Uiv2NavItem[] = [
	{ href: '/discover', label: '发现', icon: Compass, match: under('/discover') },
	{ href: '/guestbook', label: '留言', icon: MessageSquare, match: under('/guestbook') },
	{ href: '/about', label: '关于', icon: Info, match: under('/about') }
]

export const PUBLIC_TOP_NAV: Uiv2TopNavEntry[] = [
	{ key: 'home', label: '首页', items: [PUBLIC_NAV_HOME] },
	{ key: 'content', label: '内容', items: PUBLIC_NAV_CONTENT },
	{ key: 'explore', label: '探索', items: PUBLIC_NAV_EXPLORE }
]

export const PUBLIC_NAV_GROUPS: Uiv2NavGroup[] = [
	{ title: '首页', items: [PUBLIC_NAV_HOME] },
	{ title: '内容', items: PUBLIC_NAV_CONTENT },
	{ title: '探索', items: PUBLIC_NAV_EXPLORE }
]
