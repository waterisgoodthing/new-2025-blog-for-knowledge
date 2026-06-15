'use client'

import { useCallback, useEffect, useState } from 'react'
import { AlertCircle, CheckCircle2, Folder, Music, RefreshCw } from 'lucide-react'
import { toast } from 'sonner'
import {
  generateDailySong,
  getManageDailySong,
  getMusicDiagnostics,
  type DailySongItem,
  type MusicDiagnostics,
} from '@/lib/api/music-manage'

export function MusicTab() {
  const [track, setTrack] = useState<DailySongItem | null>(null)
  const [diag, setDiag] = useState<MusicDiagnostics | null>(null)
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const [song, diagnostics] = await Promise.all([
        getManageDailySong().catch(() => null),
        getMusicDiagnostics().catch(() => null),
      ])
      setTrack(song)
      setDiag(diagnostics)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    load()
  }, [load])

  const refreshSource = async () => {
    setRefreshing(true)
    try {
      await generateDailySong()
      await load()
      toast.success('本地音源已读取')
    } catch (e: any) {
      await load()
      toast.error(e.message || '未检测到本地音源')
    } finally {
      setRefreshing(false)
    }
  }

  if (loading) {
    return <div className='py-10 text-center text-gray-400'>加载中...</div>
  }

  const warnings = diag?.warnings || []
  const isReady = Boolean(track?.preview_url)

  return (
    <div className='space-y-5'>
      <div className='rounded-xl border border-white/40 bg-white/60 p-5 backdrop-blur-sm'>
        <div className='mb-4 flex flex-wrap items-center justify-between gap-3'>
          <div>
            <h3 className='font-medium'>本地单曲音源</h3>
            <div className='mt-1 flex items-center gap-1.5 text-xs text-gray-500'>
              <Folder className='h-3.5 w-3.5' />
              <span>{diag?.source_dir || 'public/mymusic'}</span>
            </div>
          </div>
          <button
            onClick={refreshSource}
            disabled={refreshing}
            className='inline-flex items-center gap-1.5 rounded-lg bg-[var(--color-brand)] px-3 py-1.5 text-sm text-white disabled:opacity-50'
          >
            <RefreshCw className={`h-3.5 w-3.5 ${refreshing ? 'animate-spin' : ''}`} />
            {refreshing ? '读取中...' : '重新读取'}
          </button>
        </div>

        <div className='grid gap-3 text-sm md:grid-cols-3'>
          <StatusItem label='音源状态' value={isReady ? '可播放' : '未检测到'} ok={isReady} />
          <StatusItem label='音频文件数' value={String(diag?.local_file_count ?? 0)} ok={(diag?.local_file_count ?? 0) === 1} />
          <StatusItem label='当前文件' value={diag?.selected_file || '-'} ok={isReady} />
        </div>

        {warnings.length > 0 && (
          <div className='mt-4 space-y-2'>
            {warnings.map((warning, index) => (
              <div key={`${warning}-${index}`} className='flex items-start gap-2 rounded-lg bg-amber-50 p-3 text-sm text-amber-700'>
                <AlertCircle className='mt-0.5 h-4 w-4 shrink-0' />
                <span>{warning}</span>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className='rounded-xl border border-white/40 bg-white/60 p-5 backdrop-blur-sm'>
        {track ? (
          <div className='flex flex-col gap-4 md:flex-row md:items-center'>
            <div className='flex h-20 w-20 shrink-0 items-center justify-center rounded-lg bg-white/70 text-gray-400'>
              {track.artwork_url ? (
                <img src={track.artwork_url} alt={track.title} className='h-full w-full rounded-lg object-cover' />
              ) : (
                <Music className='h-8 w-8' />
              )}
            </div>
            <div className='min-w-0 flex-1'>
              <div className='truncate font-medium'>{track.title}</div>
              <div className='text-sm text-gray-500'>{track.artist || '本地音源'}</div>
              {track.preview_url && (
                <audio className='mt-3 w-full' src={track.preview_url} controls preload='metadata' />
              )}
            </div>
          </div>
        ) : (
          <div className='py-10 text-center'>
            <Music className='mx-auto mb-3 h-12 w-12 text-gray-300' />
            <p className='text-sm text-gray-400'>未检测到本地音乐文件</p>
          </div>
        )}
      </div>
    </div>
  )
}

function StatusItem({ label, value, ok }: { label: string; value: string; ok: boolean }) {
  return (
    <div className='rounded-lg bg-white/40 p-3'>
      <div className='flex items-center gap-1.5 text-xs text-gray-500'>
        {ok ? <CheckCircle2 className='h-3.5 w-3.5 text-green-600' /> : <AlertCircle className='h-3.5 w-3.5 text-amber-600' />}
        <span>{label}</span>
      </div>
      <div className={`mt-1 truncate font-medium ${ok ? 'text-green-600' : 'text-amber-700'}`}>{value}</div>
    </div>
  )
}
