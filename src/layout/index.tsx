'use client'
import { PropsWithChildren, useEffect, useMemo, useState } from 'react'
import { useCenterInit } from '@/hooks/use-center'
import BlurredBubblesBackground from './backgrounds/blurred-bubbles'
import NavCard from '@/components/nav-card'
import { Toaster } from 'sonner'
import { CircleCheckIcon, InfoIcon, Loader2Icon, LayoutDashboard, OctagonXIcon, TriangleAlertIcon } from 'lucide-react'
import { useSize, useSizeInit } from '@/hooks/use-size'
import { useConfigStore } from '@/app/(home)/stores/config-store'
import { ScrollTopButton } from '@/components/scroll-top-button'
import MusicCard from '@/components/music-card'
import { SiteSettingsLoader } from '@/components/site-settings-loader'
import { usePathname, useRouter } from 'next/navigation'
import { useAdminAuth } from '@/hooks/use-admin-auth'
import {
	MobileDrawer,
	PUBLIC_NAV_GROUPS,
	PUBLIC_TOP_NAV,
	PublicTopNav,
	type Uiv2NavGroup,
	type Uiv2NavItem,
	type Uiv2TopNavEntry
} from '@/components/ui-v2'

/**
 * Administrator destination is appended only after the optional session
 * resolves to `is_admin`. `PublicTopNav` / `MobileDrawer` stay presentational;
 * the layout owns this decision so anonymous visitors never see the entry and
 * never produce a 401 (`useAdminAuth` optional mode uses `/api/auth/session-state`).
 */
const ADMIN_NAV_ITEM: Uiv2NavItem = {
	href: '/manage',
	label: '管理后台',
	icon: LayoutDashboard,
	match: (pathname: string) => pathname === '/manage' || pathname.startsWith('/manage/')
}
const ADMIN_TOP_ENTRY: Uiv2TopNavEntry = { key: 'admin', label: '管理后台', items: [ADMIN_NAV_ITEM] }
const ADMIN_GROUP: Uiv2NavGroup = { title: '管理', items: [ADMIN_NAV_ITEM] }

export default function Layout({ children }: PropsWithChildren) {
	useCenterInit()
	useSizeInit()
	const { cardStyles, siteContent, regenerateKey } = useConfigStore()
	const { maxSM, init } = useSize()
	const pathname = usePathname()
	const router = useRouter()
	const { isAdmin } = useAdminAuth({ mode: 'optional' })

	const isHome = pathname === '/'
	const isWrite = pathname.startsWith('/write')
	// /manage* renders its own AppShell (admin sidebar + mobile drawer); stacking
	// the public bar on top would duplicate chrome and hamburgers.
	const isManageRoute = pathname === '/manage' || pathname.startsWith('/manage/')
	// Phase 6: the home page now carries the same glass navigation as inner pages.
	const isInnerPage = !isHome && !isWrite && !isManageRoute
	const showPublicChrome = !isWrite && !isManageRoute

	// Phase 6: every public route (home + inner pages) carries the glass bar.
	const showTopNav = !maxSM && showPublicChrome

	// The home scene is a viewport-sized composition and the bar overlays it, so
	// its original document height is preserved. On short viewports the topmost
	// card would sit under the bar; nudge <main> down by the missing amount. The
	// shift lives on <main> (not the page) so every home card — including the
	// layout-owned NavCard — moves together.
	const [homeShift, setHomeShift] = useState(0)
	useEffect(() => {
		if (!isHome || maxSM) {
			setHomeShift(0)
			return
		}
		const measure = () => {
			setHomeShift(previous => {
				const cards = Array.from(document.querySelectorAll('main .card'))
				if (cards.length === 0) return 0
				const rawMin = Math.min(...cards.map(card => card.getBoundingClientRect().top)) - previous
				return Math.max(0, Math.round(80 - rawMin))
			})
		}
		const frame = requestAnimationFrame(measure)
		const timer = window.setTimeout(measure, 700)
		window.addEventListener('resize', measure)
		return () => {
			cancelAnimationFrame(frame)
			window.clearTimeout(timer)
			window.removeEventListener('resize', measure)
		}
	}, [isHome, maxSM])
	const showMobileNav = maxSM && !isWrite

	const topNavEntries = useMemo(() => (isAdmin ? [...PUBLIC_TOP_NAV, ADMIN_TOP_ENTRY] : PUBLIC_TOP_NAV), [isAdmin])
	const mobileGroups = useMemo(() => (isAdmin ? [...PUBLIC_NAV_GROUPS, ADMIN_GROUP] : PUBLIC_NAV_GROUPS), [isAdmin])

	useEffect(() => {
		const handleKeyDown = (e: KeyboardEvent) => {
			if ((e.ctrlKey || e.metaKey) && (e.key === 'l' || e.key === ',')) {
				e.preventDefault()
				router.push('/manage?tab=settings')
			}
		}
		window.addEventListener('keydown', handleKeyDown)
		return () => window.removeEventListener('keydown', handleKeyDown)
	}, [router])

	const backgroundImages = (siteContent.backgroundImages ?? []) as Array<{ id: string; url: string }>
	const currentBackgroundImageId = siteContent.currentBackgroundImageId
	const currentBackgroundImage =
		currentBackgroundImageId && currentBackgroundImageId.trim() ? backgroundImages.find(item => item.id === currentBackgroundImageId) : null

	return (
		<>
			<SiteSettingsLoader />
			<Toaster
				position={maxSM && isInnerPage ? 'top-center' : 'bottom-right'}
				richColors
				icons={{
					success: <CircleCheckIcon className='size-4' />,
					info: <InfoIcon className='size-4' />,
					warning: <TriangleAlertIcon className='size-4' />,
					error: <OctagonXIcon className='size-4' />,
					loading: <Loader2Icon className='size-4 animate-spin' />
				}}
				style={
					{
						'--border-radius': '12px'
					} as React.CSSProperties
				}
			/>
			{currentBackgroundImage && (
				<div
					className='fixed inset-0 z-0 overflow-hidden'
					style={{
						backgroundImage: `url(${currentBackgroundImage.url})`,
						backgroundSize: 'cover',
						backgroundPosition: 'center',
						backgroundRepeat: 'no-repeat'
					}}
				/>
			)}
			<BlurredBubblesBackground colors={siteContent.backgroundColors} regenerateKey={regenerateKey} />

			<div className='relative min-h-dvh'>
			{showTopNav && (
				<PublicTopNav
					entries={topNavEntries}
					currentPath={pathname}
					brandLabel={siteContent.meta?.title ?? 'My Blog'}
					// Inner pages are in flow. The home scene is a viewport-sized composition:
					// an overlay bar keeps its document height unchanged (no clipped bottom
					// card); <main> is nudged down only when a card would sit under it.
					position={isHome ? 'fixed' : 'sticky'}
				/>
			)}

			{showMobileNav && <MobileDrawer groups={mobileGroups} currentPath={pathname} />}

			<main className='relative z-10 h-full' style={isHome ? { top: homeShift } : undefined}>
				{children}
				<NavCard />

				{!maxSM && cardStyles.musicCard?.enabled !== false && <MusicCard />}
			</main>
			</div>

			{maxSM && init && <ScrollTopButton className={`bg-brand/20 fixed z-50 shadow-md ${maxSM && !isWrite ? 'right-4 bottom-6' : 'right-6 bottom-8'}`} />}
		</>
	)
}
