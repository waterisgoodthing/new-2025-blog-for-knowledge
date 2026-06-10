'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useMemo, useState, useCallback } from 'react'
import { motion, AnimatePresence } from 'motion/react'
import Image from 'next/image'
import { cn } from '@/lib/utils'
import { useConfigStore } from '@/app/(home)/stores/config-store'
import ScrollOutlineSVG from '@/svgs/scroll-outline.svg'
import ScrollFilledSVG from '@/svgs/scroll-filled.svg'
import ProjectsFilledSVG from '@/svgs/projects-filled.svg'
import ProjectsOutlineSVG from '@/svgs/projects-outline.svg'
import AboutFilledSVG from '@/svgs/about-filled.svg'
import AboutOutlineSVG from '@/svgs/about-outline.svg'
import ShareFilledSVG from '@/svgs/share-filled.svg'
import ShareOutlineSVG from '@/svgs/share-outline.svg'
import WebsiteFilledSVG from '@/svgs/website-filled.svg'
import WebsiteOutlineSVG from '@/svgs/website-outline.svg'
import { Home, PenLine, Settings } from 'lucide-react'

const navItems = [
	{ icon: Home, iconActive: Home, label: '首页', href: '/' },
	{ icon: ScrollOutlineSVG, iconActive: ScrollFilledSVG, label: '近期文章', href: '/blog' },
	{ icon: PenLine, iconActive: PenLine, label: '笔记', href: '/notes' },
	{ icon: ProjectsOutlineSVG, iconActive: ProjectsFilledSVG, label: '错题集', href: '/mistakes' },
	{ icon: AboutOutlineSVG, iconActive: AboutFilledSVG, label: '关于网站', href: '/about' },
	{ icon: ShareOutlineSVG, iconActive: ShareFilledSVG, label: '推荐分享', href: '/share' },
	{ icon: WebsiteOutlineSVG, iconActive: WebsiteFilledSVG, label: '优秀博客', href: '/bloggers' }
]

export default function VerticalNav() {
	const pathname = usePathname()
	const [expanded, setExpanded] = useState(false)
	const { siteContent } = useConfigStore()

	const activeIndex = useMemo(() => {
		if (pathname === '/') return 0
		const index = navItems.findIndex(item => item.href !== '/' && pathname.startsWith(item.href))
		return index >= 0 ? index : -1
	}, [pathname])
	const isManageActive = pathname.startsWith('/manage')

	const handleMouseEnter = useCallback(() => setExpanded(true), [])
	const handleMouseLeave = useCallback(() => setExpanded(false), [])

	return (
		<motion.nav
			className='vertical-nav fixed top-1/2 left-2 z-40 -translate-y-1/2'
			onMouseEnter={handleMouseEnter}
			onMouseLeave={handleMouseLeave}
			animate={{ width: expanded ? 180 : 56 }}
			transition={{ type: 'spring', stiffness: 400, damping: 30 }}>
			<div className='flex max-h-[calc(100vh-32px)] flex-col rounded-r-2xl border border-l-0 border-white/40 bg-white/70 shadow-lg backdrop-blur-xl'>
				<div className='shrink-0 px-2 pt-3 pb-2'>
					<Link
						href='/'
						aria-label='返回首页'
						title='返回首页'
						className={cn(
							'flex w-full items-center gap-2.5 rounded-xl px-2 py-1.5 transition-colors',
							pathname === '/' ? 'bg-[var(--color-brand)]/10' : 'hover:bg-white/60'
						)}>
						<Image
							src='/images/avatar.png'
							alt='avatar'
							width={28}
							height={28}
							className='shrink-0 rounded-full'
							style={{ boxShadow: '0 4px 12px -2px #E2D9CE' }}
						/>
						<AnimatePresence>
							{expanded && (
								<motion.span
									className='font-averia truncate text-sm font-medium'
									initial={{ opacity: 0, x: -8 }}
									animate={{ opacity: 1, x: 0 }}
									exit={{ opacity: 0, x: -8 }}
									transition={{ duration: 0.15 }}>
									{siteContent.meta.title}
								</motion.span>
							)}
						</AnimatePresence>
					</Link>
				</div>

				<div className='mx-2 border-t border-white/30' />

				<Link
					href='/manage'
					aria-label='管理面板'
					title='管理面板'
					className={cn(
						'mx-2 my-1 flex shrink-0 rounded-xl transition-colors',
						expanded ? 'items-center gap-2.5 px-2 py-2' : 'flex-col items-center gap-0.5 px-1 py-1.5',
						isManageActive ? 'bg-[var(--color-brand)]/15 font-medium text-[var(--color-brand)]' : 'text-gray-500 hover:bg-white/60 hover:text-gray-700'
					)}>
					<div className='flex h-7 w-7 shrink-0 items-center justify-center'>
						<Settings className='h-[18px] w-[18px]' />
					</div>
					<AnimatePresence>
						{expanded ? (
							<motion.span
								className='relative z-10 truncate text-[13px]'
								initial={{ opacity: 0, x: -8 }}
								animate={{ opacity: 1, x: 0 }}
								exit={{ opacity: 0, x: -8 }}
								transition={{ duration: 0.15 }}>
								管理面板
							</motion.span>
						) : (
							<motion.span
								className='text-[10px] leading-none'
								initial={{ opacity: 0 }}
								animate={{ opacity: 1 }}
								exit={{ opacity: 0 }}
								transition={{ duration: 0.15 }}>
								管理
							</motion.span>
						)}
					</AnimatePresence>
				</Link>

				<div className='mx-2 border-t border-white/30' />

				<nav className='flex-1 overflow-y-auto px-2 py-1'>
					{navItems.slice(1).map((item, i) => {
						const index = i + 1
						const isActive = index === activeIndex
						const Icon = isActive ? item.iconActive : item.icon

						return (
							<Link
								key={item.href}
								href={item.href}
								aria-label={item.label}
								title={item.label}
								className={cn(
									'group relative z-10 flex w-full items-center gap-2.5 rounded-xl px-2 py-2 transition-colors',
									isActive ? 'bg-[var(--color-brand)]/15 font-medium text-[var(--color-brand)]' : 'text-gray-500 hover:bg-white/60 hover:text-gray-700'
								)}>
								{isActive && (
									<motion.div
										layoutId='vertical-nav-active'
										className='pointer-events-none absolute inset-0 rounded-xl bg-[var(--color-brand)]/15'
										transition={{ type: 'spring', stiffness: 400, damping: 30 }}
									/>
								)}
								<div className='relative z-10 flex h-7 w-7 shrink-0 items-center justify-center'>
									<Icon className={cn('h-[18px] w-[18px]', isActive ? 'text-[var(--color-brand)]' : 'text-gray-500 group-hover:text-gray-700')} />
								</div>
								<AnimatePresence>
									{expanded && (
										<motion.span
											className='relative z-10 truncate text-[13px]'
											initial={{ opacity: 0, x: -8 }}
											animate={{ opacity: 1, x: 0 }}
											exit={{ opacity: 0, x: -8 }}
											transition={{ duration: 0.15 }}>
											{item.label}
										</motion.span>
									)}
								</AnimatePresence>
							</Link>
						)
					})}
				</nav>
			</div>
		</motion.nav>
	)
}
