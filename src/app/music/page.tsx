'use client'

import { useCallback, useEffect, useRef, useState } from 'react'
import { motion } from 'motion/react'
import { Music, Pause, Play } from 'lucide-react'
import { getPublicDailySong, type DailySongItem } from '@/lib/api/music-manage'

export default function MusicPage() {
  const [track, setTrack] = useState<DailySongItem | null>(null)
  const [loading, setLoading] = useState(true)
  const [playing, setPlaying] = useState(false)
  const audioRef = useRef<HTMLAudioElement | null>(null)

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const song = await getPublicDailySong().catch(() => null)
      setTrack(song)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    load()
  }, [load])

  const handlePlay = () => {
    if (!track?.preview_url) return
    if (audioRef.current) {
      audioRef.current.pause()
    }
    const audio = new Audio(track.preview_url)
    audioRef.current = audio
    audio.play()
    setPlaying(true)
    audio.onended = () => setPlaying(false)
    audio.onpause = () => setPlaying(false)
  }

  const handlePause = () => {
    if (audioRef.current) {
      audioRef.current.pause()
    }
    setPlaying(false)
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
        本地音乐
      </motion.h1>

      {track ? (
        <div className='rounded-2xl border border-white/40 bg-white/60 p-6 backdrop-blur-sm'>
          <div className='mb-2 text-xs text-gray-400'>本地单曲 · {track.date}</div>
          <div className='flex flex-col gap-6 md:flex-row md:items-start'>
            <div className='group relative h-40 w-40 shrink-0 overflow-hidden rounded-xl bg-white/60 shadow-sm'>
              {track.artwork_url ? (
                <img src={track.artwork_url} alt={track.title} className='h-full w-full object-cover' />
              ) : (
                <div className='flex h-full w-full items-center justify-center text-5xl text-gray-300'>♪</div>
              )}
              {track.preview_url && (
                <button
                  onClick={() => playing ? handlePause() : handlePlay()}
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
              <h2 className='text-xl font-bold'>{track.title}</h2>
              <p className='text-gray-500'>{track.artist || '本地音源'}{track.album ? ` · ${track.album}` : ''}</p>
              {track.recommendation_reason && (
                <p className='mt-3 rounded-lg bg-blue-50/60 p-3 text-sm text-blue-700'>
                  {track.recommendation_reason}
                </p>
              )}
              {track.preview_url && (
                <div className='mt-4 space-y-3'>
                  <button
                    onClick={() => playing ? handlePause() : handlePlay()}
                    className='inline-flex items-center gap-2 rounded-xl bg-[var(--color-brand)] px-4 py-2 text-sm text-white'
                  >
                    {playing ? <Pause size={14} /> : <Play size={14} />}
                    {playing ? '暂停' : '播放'}
                  </button>
                  <audio className='w-full' src={track.preview_url} controls preload='metadata' />
                </div>
              )}
            </div>
          </div>
        </div>
      ) : (
        <div className='rounded-2xl border border-white/40 bg-white/60 p-10 text-center backdrop-blur-sm'>
          <Music className='mx-auto mb-3 h-12 w-12 text-gray-300' />
          <p className='text-gray-400'>未检测到本地音乐文件</p>
        </div>
      )}
    </div>
  )
}
