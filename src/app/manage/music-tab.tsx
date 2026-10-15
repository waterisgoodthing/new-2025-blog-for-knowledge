'use client'

import { useCallback, useEffect, useState } from 'react'
import { AlertCircle, CheckCircle2, Folder, Music, RefreshCw } from 'lucide-react'
import { toast } from 'sonner'
import {
  generateDailySong,
  getManageDailySong,
  getMusicDiagnostics,
  updateLocalMusicSelection,
  type DailySongItem,
  type MusicDiagnostics,
} from '@/lib/api/music-manage'

export function MusicTab() {
  const [track, setTrack] = useState<DailySongItem | null>(null)
  const [diag, setDiag] = useState<MusicDiagnostics | null>(null)
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [selecting, setSelecting] = useState<string | null>(null)

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

  const selectFile = async (fileName: string) => {
    setSelecting(fileName)
    try {
      await updateLocalMusicSelection(fileName)
      await load()
      toast.success('当前音源已更新')
    } catch (e: any) {
      toast.error(e.message || '音源选择失败')
    } finally {
      setSelecting(null)
    }
  }

  if (loading) {
    return <div className='py-10 text-center text-gray-400'>加载中...</div>
  }

  const warnings = diag?.warnings || []
  const files = diag?.files || []
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
          <StatusItem label='可部署文件' value={`${diag?.deployable_file_count ?? 0}/${diag?.local_file_count ?? 0}`} ok={(diag?.deployable_file_count ?? 0) > 0} />
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
        <div className='mb-4 flex items-center justify-between gap-3'>
          <h3 className='font-medium'>选择播放文件</h3>
          <span className='text-xs text-gray-400'>单文件需小于 25 MiB</span>
        </div>

        {files.length > 0 ? (
          <div className='space-y-2'>
            {files.map((file) => (
              <div key={file.name} className='flex flex-col gap-3 rounded-lg bg-white/45 p-3 text-sm md:flex-row md:items-center md:justify-between'>
                <div className='min-w-0'>
                  <div className='flex items-center gap-2'>
                    {file.selected ? (
                      <CheckCircle2 className='h-4 w-4 shrink-0 text-green-600' />
                    ) : (
                      <Music className='h-4 w-4 shrink-0 text-gray-400' />
                    )}
                    <span className='truncate font-medium'>{file.name}</span>
                  </div>
                  <div className='mt-1 text-xs text-gray-500'>
                    {formatBytes(file.size_bytes)}
                    {!file.deployable && file.reason ? ` · ${file.reason}` : ''}
                  </div>
                </div>
                <button
                  onClick={() => selectFile(file.name)}
                  disabled={!file.deployable || file.selected || selecting === file.name}
                  className='inline-flex shrink-0 items-center justify-center rounded-lg bg-[var(--color-brand)] px-3 py-1.5 text-sm text-white disabled:cursor-not-allowed disabled:opacity-45'
                >
                  {file.selected ? '当前使用' : selecting === file.name ? '设置中...' : '设为当前'}
                </button>
              </div>
            ))}
          </div>
        ) : (
          <div className='rounded-lg bg-white/40 py-8 text-center text-sm text-gray-400'>未检测到本地音频文件</div>
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

function formatBytes(bytes: number): string {
  if (!Number.isFinite(bytes) || bytes <= 0) return '0 B'
  const units = ['B', 'KiB', 'MiB', 'GiB']
  let value = bytes
  let index = 0
  while (value >= 1024 && index < units.length - 1) {
    value /= 1024
    index += 1
  }
  return `${value.toFixed(index === 0 ? 0 : 1)} ${units[index]}`
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
