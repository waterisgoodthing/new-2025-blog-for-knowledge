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
import { Home, PenLine, Compass, MessageSquare } from 'lucide-react'

type NavItem = { icon: React.ElementType; iconActive: React.ElementType; label: string; href: string }

const publicContentItems: NavItem[] = [
	{ icon: ScrollOutlineSVG, iconActive: ScrollFilledSVG, label: '博客', href: '/blog' },
	{ icon: PenLine, iconActive: PenLine, label: '笔记', href: '/notes' },
	{ icon: ProjectsOutlineSVG, iconActive: ProjectsFilledSVG, label: '错题', href: '/mistakes' },
]

const interactionItems: NavItem[] = [
	{ icon: Compass, iconActive: Compass, label: '发现', href: '/discover' },
	{ icon: MessageSquare, iconActive: MessageSquare, label: '留言', href: '/guestbook' },
	{ icon: AboutOutlineSVG, iconActive: AboutFilledSVG, label: '关于', href: '/about' },
]

const allNavItems = [...publicContentItems, ...interactionItems]

export default function VerticalNav() {
	const pathname = usePathname()
	const [expanded, setExpanded] = useState(false)
	const { siteContent } = useConfigStore()

	const activeHref = useMemo(() => {
		if (pathname === '/') return '/'
		const match = allNavItems.find(item => pathname.startsWith(item.href))
		return match?.href ?? null
	}, [pathname])
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
							src={siteContent.avatarUrl || '/images/avatar.png'}
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

				<nav className='flex-1 overflow-y-auto px-2 py-1'>
					<NavGroup
						label='公开内容'
						items={publicContentItems}
						activeHref={activeHref}
						expanded={expanded}
					/>

					<div className='mx-1 my-1.5 border-t border-white/20' />

					<NavGroup
						label='互动探索'
						items={interactionItems}
						activeHref={activeHref}
						expanded={expanded}
					/>
				</nav>
			</div>
		</motion.nav>
	)
}

function NavGroup({
	label,
	items,
	activeHref,
	expanded,
}: {
	label: string
	items: NavItem[]
	activeHref: string | null
	expanded: boolean
}) {
	return (
		<div className='py-0.5'>
			<AnimatePresence>
				{expanded && (
					<motion.div
						className='px-2 pb-1 pt-1 text-[10px] font-medium tracking-wider text-gray-400 uppercase'
						initial={{ opacity: 0, x: -8 }}
						animate={{ opacity: 1, x: 0 }}
						exit={{ opacity: 0, x: -8 }}
						transition={{ duration: 0.15 }}>
						{label}
					</motion.div>
				)}
			</AnimatePresence>
			{items.map(item => {
				const isActive = activeHref === item.href
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
		</div>
	)
}
