'use client'

import Card from '@/components/card'
import Image from 'next/image'
import Link from 'next/link'
import { useEffect, useMemo, useState } from 'react'
import { motion } from 'motion/react'
import { useCenterStore } from '@/hooks/use-center'
import { CARD_SPACING } from '@/consts'
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
import { usePathname } from 'next/navigation'
import clsx from 'clsx'
import { cn } from '@/lib/utils'
import { useSize } from '@/hooks/use-size'
import { useConfigStore } from '@/app/(home)/stores/config-store'
import { HomeDraggableLayer } from '@/app/(home)/home-draggable-layer'
import { Home, PenLine, Settings } from 'lucide-react'

const list = [
	{
		icon: ScrollOutlineSVG,
		iconActive: ScrollFilledSVG,
		label: '近期文章',
		href: '/blog'
	},
	{
		icon: PenLine,
		iconActive: PenLine,
		label: '笔记',
		href: '/notes'
	},
	{
		icon: ProjectsOutlineSVG,
		iconActive: ProjectsFilledSVG,
		label: '错题集',
		href: '/mistakes'
	},
	{
		icon: AboutOutlineSVG,
		iconActive: AboutFilledSVG,
		label: '关于网站',
		href: '/about'
	},
	{
		icon: ShareOutlineSVG,
		iconActive: ShareFilledSVG,
		label: '推荐分享',
		href: '/share'
	},
	{
		icon: WebsiteOutlineSVG,
		iconActive: WebsiteFilledSVG,
		label: '优秀博客',
		href: '/bloggers'
	}
]

const extraSize = 8

export default function NavCard() {
	const pathname = usePathname()
	const center = useCenterStore()
	const [show, setShow] = useState(false)
	const { maxSM } = useSize()
	const [hoveredIndex, setHoveredIndex] = useState<number>(0)
	const { siteContent, cardStyles } = useConfigStore()
	const styles = cardStyles.navCard
	const hiCardStyles = cardStyles.hiCard

	const activeIndex = useMemo(() => {
		const index = list.findIndex(item => pathname.startsWith(item.href))
		return index >= 0 ? index : undefined
	}, [pathname])

	useEffect(() => {
		setShow(true)
	}, [])

	let form = useMemo(() => {
		if (pathname == '/') return 'full'
		else if (pathname.startsWith('/write')) return 'mini'
		else return 'icons'
	}, [pathname])
	if (maxSM) form = 'icons'

	const itemHeight = form === 'full' ? 36 : 28

	let position = useMemo(() => {
		if (form === 'full') {
			const x = styles.offsetX !== null ? center.x + styles.offsetX : center.x - hiCardStyles.width / 2 - styles.width - CARD_SPACING
			const y = styles.offsetY !== null ? center.y + styles.offsetY : center.y + hiCardStyles.height / 2 - styles.height
			return { x, y }
		}

		return {
			x: 24,
			y: 16
		}
	}, [form, center, styles, hiCardStyles])

	const size = useMemo(() => {
		if (form === 'mini') return { width: 108, height: 64 }
		else if (form === 'icons') return { width: 340, height: 64 }
		else return { width: styles.width, height: styles.height }
	}, [form, styles])

	useEffect(() => {
		if (form === 'icons' && activeIndex !== undefined && hoveredIndex !== activeIndex) {
			const timer = setTimeout(() => {
				setHoveredIndex(activeIndex)
			}, 1500)
			return () => clearTimeout(timer)
		}
	}, [hoveredIndex, activeIndex, form])

	if (maxSM) position = { x: center.x - size.width / 2, y: 16 }

	if (form === 'icons') return null

	if (show)
		return (
			<HomeDraggableLayer cardKey='navCard' x={position.x} y={position.y} width={styles.width} height={styles.height}>
				<Card
					order={styles.order}
					width={size.width}
					height={size.height}
					x={position.x}
					y={position.y}
					className={clsx('overflow-hidden', form === 'mini' && 'p-3', form === 'icons' && 'flex items-center gap-6 p-3')}>
					{form === 'full' && siteContent.enableChristmas && (
						<>
							<img
								src='/images/christmas/snow-4.webp'
								alt='Christmas decoration'
								className='pointer-events-none absolute'
								style={{ width: 160, left: -18, top: -20, opacity: 0.9 }}
							/>
						</>
					)}

					{form === 'mini' && (
						<Link
							className='flex h-full items-center justify-center gap-2 rounded-3xl px-2 transition-colors hover:bg-white/45'
							href='/'
							aria-label='返回首页'
							title='返回首页'>
							<Image src='/images/avatar.png' alt='avatar' width={40} height={40} style={{ boxShadow: ' 0 12px 20px -5px #E2D9CE' }} className='rounded-full' />
							<span className='flex items-center gap-1 text-sm font-medium text-gray-600'>
								<Home className='h-4 w-4' />
								首页
							</span>
						</Link>
					)}

					{form === 'full' && (
						<div className='relative z-10 flex h-full min-h-0 flex-col'>
							<Link
								className='flex shrink-0 items-center gap-3 rounded-2xl px-1 py-0.5 transition-colors hover:bg-white/40'
								href='/'
								aria-label='返回首页'
								title='返回首页'>
								<Image
									src='/images/avatar.png'
									alt='avatar'
									width={36}
									height={36}
									style={{ boxShadow: ' 0 12px 20px -5px #E2D9CE' }}
									className='shrink-0 rounded-full'
								/>
								<span className='font-averia mt-1 min-w-0 truncate text-xl leading-none font-medium'>{siteContent.meta.title}</span>
								<span className='text-brand mt-1.5 shrink-0 text-xs font-medium'>(开发中)</span>
							</Link>

							<div className='mt-2 shrink-0 border-t border-white/30 pt-1.5'>
								<Link
									href='/manage'
									aria-label='管理面板'
									title='管理面板'
									className='text-secondary hover:text-primary flex w-full items-center gap-3 rounded-full px-4 py-1.5 text-sm transition-colors hover:bg-white/55'>
									<div className='flex h-6 w-6 shrink-0 items-center justify-center'>
										<Settings className='h-5 w-5' />
									</div>
									<span className='font-medium'>管理面板</span>
								</Link>
							</div>

							<div className='text-secondary mt-2 shrink-0 text-xs uppercase'>General</div>

							<div className='relative mt-1.5 min-h-0 flex-1 overflow-hidden pr-1'>
								<div className='relative space-y-1 pb-1'>
									<motion.div
										className='pointer-events-none absolute max-w-[230px] rounded-full border'
										layoutId='nav-hover'
										initial={false}
										animate={{ top: hoveredIndex * (itemHeight + 4), left: 0, width: '100%', height: itemHeight }}
										transition={{
											type: 'spring',
											stiffness: 400,
											damping: 30
										}}
										style={{ backgroundImage: 'linear-gradient(to right bottom, var(--color-border) 60%, var(--color-card) 100%)' }}
									/>

									{list.map((item, index) => (
										<Link
											key={item.href}
											href={item.href}
											aria-label={item.label}
											title={item.label}
											className='text-secondary relative z-10 flex items-center gap-3 rounded-full px-4 py-1.5 text-sm'
											onMouseEnter={() => setHoveredIndex(index)}>
											<div className='flex h-6 w-6 shrink-0 items-center justify-center'>
												{hoveredIndex == index ? <item.iconActive className='text-brand absolute h-6 w-6' /> : <item.icon className='absolute h-6 w-6' />}
											</div>
											<span className={clsx(index == hoveredIndex && 'text-primary font-medium')}>{item.label}</span>
										</Link>
									))}
								</div>
							</div>
						</div>
					)}
				</Card>
			</HomeDraggableLayer>
		)
}
