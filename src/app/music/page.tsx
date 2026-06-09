'use client'

import { useState, useEffect, useCallback, useRef } from 'react'
import { motion, AnimatePresence } from 'motion/react'
import { Play, Pause, ExternalLink, Music, ChevronDown } from 'lucide-react'
import { getPublicDailySong, getPublicSongHistory, type DailySongItem } from '@/lib/api/music-manage'
import dayjs from 'dayjs'

export default function MusicPage() {
  const [today, setToday] = useState<DailySongItem | null>(null)
  const [history, setHistory] = useState<DailySongItem[]>([])
  const [loading, setLoading] = useState(true)
  const [playing, setPlaying] = useState(false)
  const [hoveredSong, setHoveredSong] = useState<DailySongItem | null>(null)
  const [hoverPos, setHoverPos] = useState({ x: 0, y: 0 })
  const audioRef = useRef<HTMLAudioElement | null>(null)
  const hoverTimerRef = useRef<NodeJS.Timeout | null>(null)

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const [t, h] = await Promise.all([
        getPublicDailySong().catch(() => null),
        getPublicSongHistory(30).catch(() => []),
      ])
      setToday(t)
      setHistory(h)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    load()
  }, [load])

  const handlePlay = (song: DailySongItem) => {
    if (!song.preview_url) return
    if (audioRef.current) {
      audioRef.current.pause()
    }
    const audio = new Audio(song.preview_url)
    audioRef.current = audio
    audio.play()
    setPlaying(true)
    audio.onended = () => setPlaying(false)
  }

  const handlePause = () => {
    if (audioRef.current) {
      audioRef.current.pause()
      setPlaying(false)
    }
  }

  const handleHoverStart = (song: DailySongItem, e: React.MouseEvent) => {
    setHoverPos({ x: e.clientX, y: e.clientY })
    hoverTimerRef.current = setTimeout(() => {
      setHoveredSong(song)
    }, 500)
  }

  const handleHoverEnd = () => {
    if (hoverTimerRef.current) {
      clearTimeout(hoverTimerRef.current)
    }
    setHoveredSong(null)
  }

  if (loading) {
    return (
      <div className='mx-auto max-w-4xl px-4 py-20 text-center text-gray-400'>
        加载中...
      </div>
    )
  }

  return (
    <div className='mx-auto max-w-4xl px-4 py-8'>
      <motion.h1
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className='mb-8 text-2xl font-bold'
      >
        每日音乐
      </motion.h1>

      {today ? (
        <div className='mb-10 rounded-2xl border border-white/40 bg-white/60 p-6 backdrop-blur-sm'>
          <div className='mb-2 text-xs text-gray-400'>今日推荐 · {today.date}</div>
          <div className='flex items-start gap-6'>
            <div className='group relative h-40 w-40 shrink-0 overflow-hidden rounded-xl bg-white/60 shadow-sm'>
              {today.artwork_url ? (
                <img src={today.artwork_url} alt={today.title} className='h-full w-full object-cover' />
              ) : (
                <div className='flex h-full w-full items-center justify-center text-5xl text-gray-300'>♪</div>
              )}
              {today.preview_url && (
                <button
                  onClick={() => playing ? handlePause() : handlePlay(today)}
                  className='absolute inset-0 flex items-center justify-center bg-black/30 opacity-0 transition-opacity group-hover:opacity-100'
                  aria-label={playing ? '暂停' : '播放'}
                >
                  {playing ? (
                    <Pause className='h-10 w-10 text-white' />
                  ) : (
                    <Play className='h-10 w-10 text-white' />
                  )}
                </button>
              )}
            </div>
            <div className='min-w-0 flex-1'>
              <h2 className='text-xl font-bold'>{today.title}</h2>
              <p className='text-gray-500'>{today.artist}{today.album ? ` · ${today.album}` : ''}</p>
              {today.recommendation_reason && (
                <p className='mt-3 rounded-lg bg-blue-50/60 p-3 text-sm text-blue-700'>
                  {today.recommendation_reason}
                </p>
              )}
              <div className='mt-4 flex gap-2'>
                {today.preview_url && (
                  <button
                    onClick={() => playing ? handlePause() : handlePlay(today)}
                    className='inline-flex items-center gap-2 rounded-xl bg-[var(--color-brand)] px-4 py-2 text-sm text-white'
                  >
                    {playing ? <Pause size={14} /> : <Play size={14} />}
                    {playing ? '暂停' : '试听'}
                  </button>
                )}
                {today.netease_url && (
                  <a
                    href={today.netease_url}
                    target='_blank'
                    rel='noopener noreferrer'
                    className='inline-flex items-center gap-2 rounded-xl bg-white/60 px-4 py-2 text-sm text-gray-600 hover:bg-white/80'
                  >
                    <ExternalLink size={14} />
                    在网易云音乐打开
                  </a>
                )}
              </div>
            </div>
          </div>
        </div>
      ) : (
        <div className='mb-10 rounded-2xl border border-white/40 bg-white/60 p-10 text-center backdrop-blur-sm'>
          <Music className='mx-auto mb-3 h-12 w-12 text-gray-300' />
          <p className='text-gray-400'>今日歌曲尚未生成</p>
        </div>
      )}

      {history.length > 0 && (
        <div>
          <h2 className='mb-4 text-lg font-medium'>历史歌曲</h2>
          <div className='space-y-2'>
            {history.map((song, i) => (
              <motion.div
                key={song.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.03 }}
                className='group flex items-center gap-4 rounded-xl border border-white/40 bg-white/60 p-4 backdrop-blur-sm transition-all hover:bg-white/80'
                onMouseEnter={e => handleHoverStart(song, e)}
                onMouseLeave={handleHoverEnd}
              >
                <div className='relative h-12 w-12 shrink-0 overflow-hidden rounded-lg bg-white/60'>
                  {song.artwork_url ? (
                    <img src={song.artwork_url} alt='' className='h-full w-full object-cover' />
                  ) : (
                    <div className='flex h-full w-full items-center justify-center text-xl text-gray-300'>♪</div>
                  )}
                  {song.preview_url && (
                    <button
                      onClick={() => handlePlay(song)}
                      className='absolute inset-0 flex items-center justify-center bg-black/30 opacity-0 transition-opacity group-hover:opacity-100'
                      aria-label='播放'
                    >
                      <Play className='h-5 w-5 text-white' />
                    </button>
                  )}
                </div>
                <div className='min-w-0 flex-1'>
                  <div className='truncate font-medium'>{song.title}</div>
                  <div className='text-sm text-gray-500'>{song.artist}</div>
                </div>
                <div className='text-xs text-gray-400'>{song.date}</div>
                {song.netease_url && (
                  <a
                    href={song.netease_url}
                    target='_blank'
                    rel='noopener noreferrer'
                    className='text-gray-400 hover:text-[var(--color-brand)]'
                  >
                    <ExternalLink size={14} />
                  </a>
                )}
              </motion.div>
            ))}
          </div>
        </div>
      )}

      <AnimatePresence>
        {hoveredSong && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            className='fixed z-50 w-72 rounded-xl border border-white/40 bg-white/95 p-4 shadow-xl backdrop-blur-xl'
            style={{ left: hoverPos.x + 10, top: hoverPos.y - 80 }}
          >
            <div className='flex items-start gap-3'>
              <div className='h-16 w-16 overflow-hidden rounded-lg bg-white/60'>
                {hoveredSong.artwork_url ? (
                  <img src={hoveredSong.artwork_url} alt='' className='h-full w-full object-cover' />
                ) : (
                  <div className='flex h-full w-full items-center justify-center text-2xl text-gray-300'>♪</div>
                )}
              </div>
              <div>
                <div className='font-medium'>{hoveredSong.title}</div>
                <div className='text-sm text-gray-500'>{hoveredSong.artist}</div>
                {hoveredSong.album && <div className='text-xs text-gray-400'>{hoveredSong.album}</div>}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
