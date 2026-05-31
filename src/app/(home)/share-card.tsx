'use client'

import { useEffect, useState } from 'react'
import Card from '@/components/card'
import { useCenterStore } from '@/hooks/use-center'
import { useConfigStore } from './stores/config-store'
import { CARD_SPACING } from '@/consts'
import shareList from '@/app/share/list.json'
import Link from 'next/link'
import { HomeDraggableLayer } from './home-draggable-layer'
import { getTodayRecommendation, type DailyRecommendation } from '@/lib/api/recommendations'

type ShareItem = {
	name: string
	url: string
	logo: string
	description: string
	tags: string[]
	stars: number
}

const TYPE_LABELS: Record<string, string> = {
	note: '笔记',
	mistake: '错题',
	review: '复习',
	resource: '资源',
	music: '音乐',
	podcast: '播客',
}

export default function ShareCard() {
	const center = useCenterStore()
	const { cardStyles, siteContent } = useConfigStore()
	const [recommendation, setRecommendation] = useState<DailyRecommendation | null>(null)
	const [randomItem, setRandomItem] = useState<ShareItem | null>(null)
	const styles = cardStyles.shareCard
	const hiCardStyles = cardStyles.hiCard
	const socialButtonsStyles = cardStyles.socialButtons

	useEffect(() => {
		getTodayRecommendation()
			.then((rec) => {
				setRecommendation(rec)
			})
			.catch(() => {
				const randomIndex = Math.floor(Math.random() * shareList.length)
				setRandomItem(shareList[randomIndex])
			})
	}, [])

	const showRecommendation = recommendation !== null
	const displayItem = showRecommendation
		? null
		: randomItem

	if (!showRecommendation && !displayItem) {
		return null
	}

	const x = styles.offsetX !== null ? center.x + styles.offsetX : center.x + hiCardStyles.width / 2 - socialButtonsStyles.width
	const y = styles.offsetY !== null ? center.y + styles.offsetY : center.y + hiCardStyles.height / 2 + CARD_SPACING + socialButtonsStyles.height + CARD_SPACING

	return (
		<HomeDraggableLayer cardKey='shareCard' x={x} y={y} width={styles.width} height={styles.height}>
			<Card order={styles.order} width={styles.width} height={styles.height} x={x} y={y}>
				{siteContent.enableChristmas && (
					<>
						<img
							src='/images/christmas/snow-12.webp'
							alt='Christmas decoration'
							className='pointer-events-none absolute'
							style={{ width: 120, left: -12, top: -12, opacity: 0.8 }}
						/>
					</>
				)}

				<h2 className='text-secondary text-sm'>
					{showRecommendation ? '今日推荐' : '随机推荐'}
				</h2>

				{showRecommendation ? (
					<Link
						href={recommendation.target || '/notes'}
						className='mt-2 block space-y-2'
					>
						<div className='flex items-center gap-2'>
							<span className='bg-brand/10 text-brand inline-block rounded-full px-2 py-0.5 text-xs'>
								{TYPE_LABELS[recommendation.type] || recommendation.type}
							</span>
							<h3 className='truncate text-sm font-medium'>{recommendation.title}</h3>
						</div>

						<p className='text-secondary line-clamp-3 text-xs'>{recommendation.reason}</p>

						{recommendation.action_label && (
							<span className='text-brand text-xs'>{recommendation.action_label} →</span>
						)}
					</Link>
				) : displayItem ? (
					<Link href='/share' className='mt-2 block space-y-2'>
						<div className='flex items-center'>
							<div className='relative mr-3 h-12 w-12 shrink-0 overflow-hidden rounded-xl'>
								<img src={displayItem.logo} alt={displayItem.name} className='h-full w-full object-contain' />
							</div>
							<h3 className='truncate text-sm font-medium'>{displayItem.name}</h3>
						</div>

						<p className='text-secondary line-clamp-3 text-xs'>{displayItem.description}</p>
					</Link>
				) : null}
			</Card>
		</HomeDraggableLayer>
	)
}
