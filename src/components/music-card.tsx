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
import { getPlaylist, type MusicItem } from '@/lib/api/music'

const FALLBACK_TRACK: MusicItem = {
	id: 0,
	title: 'Close To You',
	artist: null,
	artwork: null,
	apple_music_url: '',
	preview_url: null,
	track_id: null,
	sort_order: 0,
	is_active: true,
	created_at: '',
}

export default function MusicCard() {
	const pathname = usePathname()
	const center = useCenterStore()
	const { cardStyles, siteContent } = useConfigStore()
	const styles = cardStyles.musicCard
	const hiCardStyles = cardStyles.hiCard
	const clockCardStyles = cardStyles.clockCard
	const calendarCardStyles = cardStyles.calendarCard

	const [playlist, setPlaylist] = useState<MusicItem[]>([])
	const [currentIndex, setCurrentIndex] = useState(0)
	const [isPlaying, setIsPlaying] = useState(false)
	const [progress, setProgress] = useState(0)
	const audioRef = useRef<HTMLAudioElement | null>(null)
	const currentIndexRef = useRef(0)

	const isHomePage = pathname === '/'

	useEffect(() => {
		getPlaylist()
			.then((items) => {
				if (items.length > 0) setPlaylist(items)
			})
			.catch(() => {
				setPlaylist([FALLBACK_TRACK])
			})
	}, [])

	const currentTrack = playlist.length > 0 ? playlist[currentIndex % playlist.length] : FALLBACK_TRACK
	const displayTitle = currentTrack.title || 'Close To You'
	const displayArtist = currentTrack.artist

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
			if (playlist.length > 1) {
				const nextIndex = (currentIndexRef.current + 1) % playlist.length
				currentIndexRef.current = nextIndex
				setCurrentIndex(nextIndex)
			}
			setProgress(0)
		}

		audio.addEventListener('timeupdate', updateProgress)
		audio.addEventListener('ended', handleEnded)
		audio.addEventListener('loadedmetadata', updateProgress)

		return () => {
			audio.removeEventListener('timeupdate', updateProgress)
			audio.removeEventListener('ended', handleEnded)
			audio.removeEventListener('loadedmetadata', updateProgress)
		}
	}, [playlist.length])

	useEffect(() => {
		currentIndexRef.current = currentIndex
		if (audioRef.current && currentTrack.preview_url) {
			const wasPlaying = !audioRef.current.paused
			audioRef.current.pause()
			audioRef.current.src = currentTrack.preview_url
			audioRef.current.loop = false
			setProgress(0)

			if (wasPlaying) {
				audioRef.current.play().catch(console.error)
			}
		}
	}, [currentIndex, currentTrack.preview_url])

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
		if (currentTrack.preview_url) {
			setIsPlaying(!isPlaying)
		}
	}

	const handleCardClick = () => {
		if (currentTrack.apple_music_url) {
			window.open(currentTrack.apple_music_url, '_blank')
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
					onClick={handleCardClick}
					title={displayArtist ? `${displayTitle} - ${displayArtist}` : displayTitle}
				>
					{currentTrack.artwork ? (
						<img src={currentTrack.artwork} alt={displayTitle} className='h-full w-full object-cover' />
					) : (
						<MusicSVG className='h-8 w-8' />
					)}
				</div>

				<div className='min-w-0 flex-1'>
					<div
						className='text-secondary truncate text-sm'
						onClick={handleCardClick}
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
				aria-label={isPlaying ? '暂停' : '播放'}
				className='flex h-10 w-10 items-center justify-center rounded-full bg-white transition-opacity hover:opacity-80'
			>
				{isPlaying ? <Pause className='text-brand h-4 w-4' /> : <PlaySVG className='text-brand ml-1 h-4 w-4' />}
			</button>
			</Card>
		</HomeDraggableLayer>
	)
}
