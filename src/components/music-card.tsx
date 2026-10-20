'use client'

import { useState, useRef, useEffect, useMemo } from 'react'
import Card from '@/components/card'
import { useCenterStore } from '@/hooks/use-center'
import { useConfigStore } from '../app/(home)/stores/config-store'
import { CARD_SPACING } from '@/consts'
import MusicSVG from '@/svgs/music.svg'
import PlaySVG from '@/svgs/play.svg'
import { HomeDraggableLayer } from '../app/(home)/home-draggable-layer'
import { Pause } from 'lucide-react'
import { usePathname } from 'next/navigation'
import clsx from 'clsx'
import { getPublicDailySong, type DailySongItem } from '@/lib/api/music-manage'

export default function MusicCard() {
	const pathname = usePathname()
	const center = useCenterStore()
	const { cardStyles, siteContent } = useConfigStore()
	const styles = cardStyles.musicCard
	const hiCardStyles = cardStyles.hiCard
	const clockCardStyles = cardStyles.clockCard
	const calendarCardStyles = cardStyles.calendarCard

	const [track, setTrack] = useState<DailySongItem | null>(null)
	const [isPlaying, setIsPlaying] = useState(false)
	const [progress, setProgress] = useState(0)
	const audioRef = useRef<HTMLAudioElement | null>(null)

	const isHomePage = pathname === '/'

	useEffect(() => {
		getPublicDailySong()
			.then(setTrack)
			.catch(() => setTrack(null))
	}, [])

	const displayTitle = track?.title || '暂无本地音乐'
	const displayArtist = track?.artist
	const canPlay = Boolean(track?.preview_url)

	const position = useMemo(() => {
		if (!isHomePage) {
			return {
				x: center.width - styles.width - 16,
				y: center.height - styles.height - 16
			}
		}

		return {
			x: styles.offsetX !== null ? center.x + styles.offsetX : center.x + CARD_SPACING + hiCardStyles.width / 2 - styles.offset,
			y: styles.offsetY !== null ? center.y + styles.offsetY : center.y - clockCardStyles.offset + CARD_SPACING + calendarCardStyles.height + CARD_SPACING
		}
	}, [isHomePage, center, styles, hiCardStyles, clockCardStyles, calendarCardStyles])

	const { x, y } = position

	useEffect(() => {
		if (!audioRef.current) {
			audioRef.current = new Audio()
		}

		const audio = audioRef.current

		const updateProgress = () => {
			if (audio.duration) {
				setProgress((audio.currentTime / audio.duration) * 100)
			}
		}

		const handleEnded = () => {
			setIsPlaying(false)
			setProgress(0)
		}

		const handleError = () => {
			setIsPlaying(false)
			setProgress(0)
		}

		audio.addEventListener('timeupdate', updateProgress)
		audio.addEventListener('ended', handleEnded)
		audio.addEventListener('loadedmetadata', updateProgress)
		audio.addEventListener('error', handleError)

		return () => {
			audio.removeEventListener('timeupdate', updateProgress)
			audio.removeEventListener('ended', handleEnded)
			audio.removeEventListener('loadedmetadata', updateProgress)
			audio.removeEventListener('error', handleError)
		}
	}, [])

	useEffect(() => {
		if (!audioRef.current) return

		const audio = audioRef.current
		audio.pause()
		setIsPlaying(false)
		setProgress(0)

		if (track?.preview_url) {
			audio.src = track.preview_url
			audio.loop = false
		} else {
			audio.removeAttribute('src')
		}
	}, [track?.preview_url])

	useEffect(() => {
		if (!audioRef.current) return

		if (isPlaying) {
			audioRef.current.play().catch(console.error)
		} else {
			audioRef.current.pause()
		}
	}, [isPlaying])

	useEffect(() => {
		return () => {
			if (audioRef.current) {
				audioRef.current.pause()
				audioRef.current.src = ''
			}
		}
	}, [])

	const togglePlayPause = () => {
		if (canPlay) {
			setIsPlaying(!isPlaying)
		}
	}

	if (!isHomePage && !isPlaying) {
		return null
	}

	return (
		<HomeDraggableLayer cardKey='musicCard' x={x} y={y} width={styles.width} height={styles.height}>
			<Card order={styles.order} width={styles.width} height={styles.height} x={x} y={y} className={clsx('flex items-center gap-3', !isHomePage && 'fixed')}>
				{siteContent.enableChristmas && (
					<>
						<img
							src='/images/christmas/snow-10.webp'
							alt='Christmas decoration'
							className='pointer-events-none absolute'
							style={{ width: 120, left: -8, top: -12, opacity: 0.8 }}
						/>
						<img
							src='/images/christmas/snow-11.webp'
							alt='Christmas decoration'
							className='pointer-events-none absolute'
							style={{ width: 80, right: -10, top: -12, opacity: 0.8 }}
						/>
					</>
				)}

				<div
					className='flex h-8 w-8 shrink-0 cursor-pointer items-center justify-center overflow-hidden rounded-lg'
					title={displayArtist ? `${displayTitle} - ${displayArtist}` : displayTitle}
				>
					{track?.artwork_url ? (
						<img src={track.artwork_url} alt={displayTitle} className='h-full w-full object-cover' />
					) : (
						<MusicSVG className='h-8 w-8' />
					)}
				</div>

				<div className='min-w-0 flex-1'>
					<div
						className='text-secondary truncate text-sm'
						title={displayArtist ? `${displayTitle} - ${displayArtist}` : displayTitle}
					>
						{displayTitle}
						{displayArtist && <span className='text-xs'> · {displayArtist}</span>}
					</div>

					<div className='mt-1 h-2 rounded-full bg-white/60'>
						<div className='bg-linear h-full rounded-full transition-all duration-300' style={{ width: `${progress}%` }} />
					</div>
				</div>

			<button
				onClick={togglePlayPause}
				disabled={!canPlay}
				aria-label={isPlaying ? '暂停' : '播放'}
				className='flex h-10 w-10 items-center justify-center rounded-full bg-white transition-opacity hover:opacity-80 disabled:cursor-not-allowed disabled:opacity-50'
			>
				{isPlaying ? <Pause className='text-brand h-4 w-4' /> : <PlaySVG className='text-brand ml-1 h-4 w-4' />}
			</button>
			</Card>
		</HomeDraggableLayer>
	)
}
