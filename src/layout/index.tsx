'use client'
import { PropsWithChildren, useEffect, useMemo } from 'react'
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
	const isInnerPage = !isHome && !isWrite && !isManageRoute

	// Desktop inner pages only; the home page keeps NavCard (Phase 5 scope).
	const showTopNav = !maxSM && isInnerPage
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
					// Sticky keeps the glass states but reserves its own height, so the
					// ~50 existing inner pages do not need per-page top padding.
					position='sticky'
				/>
			)}

			{showMobileNav && <MobileDrawer groups={mobileGroups} currentPath={pathname} />}

			<main className='relative z-10 h-full'>
				{children}
				<NavCard />

				{!maxSM && cardStyles.musicCard?.enabled !== false && <MusicCard />}
			</main>
			</div>

			{maxSM && init && <ScrollTopButton className={`bg-brand/20 fixed z-50 shadow-md ${maxSM && !isWrite ? 'right-4 bottom-6' : 'right-6 bottom-8'}`} />}
		</>
	)
}
