'use client'
import { PropsWithChildren, useEffect } from 'react'
import { useCenterInit } from '@/hooks/use-center'
import BlurredBubblesBackground from './backgrounds/blurred-bubbles'
import NavCard from '@/components/nav-card'
import VerticalNav from '@/components/vertical-nav'
import MobileNav from '@/components/mobile-nav'
import { Toaster } from 'sonner'
import { CircleCheckIcon, InfoIcon, Loader2Icon, OctagonXIcon, TriangleAlertIcon } from 'lucide-react'
import { useSize, useSizeInit } from '@/hooks/use-size'
import { useConfigStore } from '@/app/(home)/stores/config-store'
import { ScrollTopButton } from '@/components/scroll-top-button'
import MusicCard from '@/components/music-card'
import { SiteSettingsLoader } from '@/components/site-settings-loader'
import { usePathname, useRouter } from 'next/navigation'

export default function Layout({ children }: PropsWithChildren) {
	useCenterInit()
	useSizeInit()
	const { cardStyles, siteContent, regenerateKey } = useConfigStore()
	const { maxSM, init } = useSize()
	const pathname = usePathname()
	const router = useRouter()

	const isHome = pathname === '/'
	const isWrite = pathname.startsWith('/write')
	const isInnerPage = !isHome && !isWrite

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

			{!maxSM && isInnerPage && <VerticalNav />}

			<main className={`relative z-10 h-full ${maxSM && !isWrite ? 'pb-14' : ''}`}>
				{children}
				<NavCard />

				{!maxSM && cardStyles.musicCard?.enabled !== false && <MusicCard />}
			</main>

			{maxSM && !isWrite && <MobileNav />}
			{maxSM && init && <ScrollTopButton className={`bg-brand/20 fixed z-50 shadow-md ${maxSM && !isWrite ? 'right-4 bottom-16' : 'right-6 bottom-8'}`} />}
		</>
	)
}
