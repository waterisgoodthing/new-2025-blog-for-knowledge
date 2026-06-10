'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useMemo, useState } from 'react'
import { cn } from '@/lib/utils'
import { motion, AnimatePresence } from 'motion/react'
import ScrollOutlineSVG from '@/svgs/scroll-outline.svg'
import ScrollFilledSVG from '@/svgs/scroll-filled.svg'
import ProjectsFilledSVG from '@/svgs/projects-filled.svg'
import ProjectsOutlineSVG from '@/svgs/projects-outline.svg'
import AboutFilledSVG from '@/svgs/about-filled.svg'
import AboutOutlineSVG from '@/svgs/about-outline.svg'
import { Home, Menu, PenLine, Settings, Compass, MessageSquare } from 'lucide-react'

const primaryItems = [
	{ icon: Home, iconActive: Home, label: '首页', href: '/' },
	{ icon: ScrollOutlineSVG, iconActive: ScrollFilledSVG, label: '博客', href: '/blog' },
	{ icon: PenLine, iconActive: PenLine, label: '笔记', href: '/notes' },
	{ icon: ProjectsOutlineSVG, iconActive: ProjectsFilledSVG, label: '错题', href: '/mistakes' }
]

const interactionItems = [
	{ icon: Compass, iconActive: Compass, label: '发现', href: '/discover' },
	{ icon: MessageSquare, iconActive: MessageSquare, label: '留言', href: '/guestbook' },
	{ icon: AboutOutlineSVG, iconActive: AboutFilledSVG, label: '关于', href: '/about' },
]

const manageItem = { icon: Settings, iconActive: Settings, label: '管理', href: '/manage' }

const allMoreItems = [...interactionItems, manageItem]

export default function MobileNav() {
	const pathname = usePathname()
	const [moreOpen, setMoreOpen] = useState(false)

	const activeHref = useMemo(() => {
		if (pathname === '/') return '/'
		const all = [...primaryItems, ...allMoreItems]
		const match = all.find(item => item.href !== '/' && pathname.startsWith(item.href))
		return match?.href ?? null
	}, [pathname])

	return (
		<>
			<nav className='mobile-nav fixed inset-x-0 bottom-0 z-50 border-t border-white/40 bg-white/80 pb-[env(safe-area-inset-bottom)] backdrop-blur-xl sm:hidden'>
				<div className='flex items-center justify-around py-1.5'>
					{primaryItems.map(item => {
						const isActive = activeHref === item.href
						const Icon = isActive ? item.iconActive : item.icon
						return (
							<Link
								key={item.href}
								href={item.href}
								aria-label={item.label}
								title={item.label}
								className={cn(
									'flex flex-col items-center gap-0.5 rounded-lg px-3 py-1 transition-colors',
									isActive ? 'text-[var(--color-brand)]' : 'text-gray-400'
								)}>
								<Icon className='h-5 w-5' />
								<span className='text-[10px]'>{item.label}</span>
							</Link>
						)
					})}
					<button
						type='button'
						onClick={() => setMoreOpen(!moreOpen)}
						aria-label='更多导航'
						title='更多导航'
						className={cn(
							'flex flex-col items-center gap-0.5 rounded-lg px-3 py-1 transition-colors',
							moreOpen ? 'text-[var(--color-brand)]' : 'text-gray-400'
						)}>
						<Menu className='h-5 w-5' />
						<span className='text-[10px]'>更多</span>
					</button>
				</div>
			</nav>

			<AnimatePresence>
				{moreOpen && (
					<>
						<motion.div
							initial={{ opacity: 0 }}
							animate={{ opacity: 1 }}
							exit={{ opacity: 0 }}
							className='fixed inset-0 z-40 bg-black/20 sm:hidden'
							onClick={() => setMoreOpen(false)}
						/>
						<motion.div
							initial={{ y: '100%' }}
							animate={{ y: 0 }}
							exit={{ y: '100%' }}
							transition={{ type: 'spring', damping: 25, stiffness: 300 }}
							className='fixed inset-x-0 bottom-0 z-50 rounded-t-2xl border-t border-white/40 bg-white/95 pb-[env(safe-area-inset-bottom)] backdrop-blur-xl sm:hidden'>
							<div className='mx-auto my-2 h-1 w-10 rounded-full bg-gray-300' />
							<div className='flex flex-col gap-1 px-4 pb-4'>
								<div className='px-2 pb-1 pt-1 text-[10px] font-medium tracking-wider text-gray-400 uppercase'>
									互动探索
								</div>
								{interactionItems.map(item => {
									const isActive = activeHref === item.href
									const Icon = isActive ? item.iconActive : item.icon
									return (
										<Link
											key={item.href}
											href={item.href}
											onClick={() => setMoreOpen(false)}
											aria-label={item.label}
											title={item.label}
											className={cn(
												'flex items-center gap-3 rounded-xl px-4 py-3 transition-colors',
												isActive ? 'bg-[var(--color-brand)]/10 font-medium text-[var(--color-brand)]' : 'text-gray-600 hover:bg-white/60'
											)}>
											<Icon className='h-5 w-5' />
											<span className='text-sm'>{item.label}</span>
										</Link>
									)
								})}
								<div className='mx-2 my-1.5 border-t border-gray-200/60' />
								{(() => {
									const isActive = activeHref === manageItem.href
									const Icon = isActive ? manageItem.iconActive : manageItem.icon
									return (
										<Link
											key={manageItem.href}
											href={manageItem.href}
											onClick={() => setMoreOpen(false)}
											aria-label={manageItem.label}
											title={manageItem.label}
											className={cn(
												'flex items-center gap-3 rounded-xl px-4 py-3 transition-colors',
												isActive ? 'bg-[var(--color-brand)]/10 font-medium text-[var(--color-brand)]' : 'text-gray-400 hover:bg-white/60'
											)}>
											<Icon className='h-5 w-5' />
											<span className='text-sm'>{manageItem.label}</span>
										</Link>
									)
								})()}
							</div>
						</motion.div>
					</>
				)}
			</AnimatePresence>
		</>
	)
}
