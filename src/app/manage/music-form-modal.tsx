'use client'

import { useState, useEffect } from 'react'
import { DialogModal } from '@/components/dialog-modal'
import { createMusicItem, updateMusicItem, type MusicItem, type MusicItemCreate } from '@/lib/api/music'

interface MusicFormModalProps {
  open: boolean
  onClose: () => void
  onSuccess: () => void
  editingItem?: MusicItem | null
}

function extractTrackId(url: string): number | null {
  const iMatch = url.match(/[?&]i=(\d+)/)
  if (iMatch) return parseInt(iMatch[1], 10)
  const idMatch = url.match(/\/id(\d+)/)
  if (idMatch) return parseInt(idMatch[1], 10)
  return null
}

export function MusicFormModal({ open, onClose, onSuccess, editingItem }: MusicFormModalProps) {
  const [form, setForm] = useState<MusicItemCreate>({
    title: '',
    artist: '',
    apple_music_url: '',
    artwork: '',
    preview_url: '',
    sort_order: 0,
    is_active: true,
  })
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    if (editingItem) {
      setForm({
        title: editingItem.title,
        artist: editingItem.artist || '',
        apple_music_url: editingItem.apple_music_url,
        artwork: editingItem.artwork || '',
        preview_url: editingItem.preview_url || '',
        track_id: editingItem.track_id || undefined,
        sort_order: editingItem.sort_order,
        is_active: editingItem.is_active,
      })
    } else {
      setForm({
        title: '',
        artist: '',
        apple_music_url: '',
        artwork: '',
        preview_url: '',
        sort_order: 0,
        is_active: true,
      })
    }
    setError('')
  }, [editingItem, open])

  const handleUrlChange = (url: string) => {
    setForm((f) => {
      const trackId = extractTrackId(url)
      return { ...f, apple_music_url: url, track_id: trackId || undefined }
    })
  }

  const handleSubmit = async () => {
    if (!form.title.trim()) {
      setError('请输入歌曲标题')
      return
    }
    if (!form.apple_music_url.trim()) {
      setError('请输入 Apple Music URL')
      return
    }

    setSaving(true)
    setError('')
    try {
      if (editingItem) {
        await updateMusicItem(editingItem.id, form)
      } else {
        await createMusicItem(form)
      }
      onSuccess()
      onClose()
    } catch (e: any) {
      setError(e.message || '保存失败')
    } finally {
      setSaving(false)
    }
  }

  return (
    <DialogModal open={open} onClose={onClose} className='card w-[560px] max-w-[90vw] rounded-2xl p-6'>
      <h2 className='mb-5 text-lg font-bold'>{editingItem ? '编辑音乐' : '添加音乐'}</h2>

      <div className='max-h-[60vh] space-y-4 overflow-y-auto pr-1'>
        <div>
          <label className='mb-1.5 block text-sm font-medium'>歌曲标题 *</label>
          <input
            value={form.title}
            onChange={(e) => setForm((f) => ({ ...f, title: e.target.value }))}
            placeholder='Close To You'
            className='w-full rounded-xl border border-white/40 bg-white/60 px-4 py-2.5 text-sm backdrop-blur-sm outline-none focus:border-[var(--color-brand)]'
          />
        </div>

        <div>
          <label className='mb-1.5 block text-sm font-medium'>Apple Music URL *</label>
          <input
            value={form.apple_music_url}
            onChange={(e) => handleUrlChange(e.target.value)}
            placeholder='https://music.apple.com/cn/album/...'
            className='w-full rounded-xl border border-white/40 bg-white/60 px-4 py-2.5 text-sm backdrop-blur-sm outline-none focus:border-[var(--color-brand)]'
          />
          {form.track_id && (
            <p className='mt-1 text-xs text-gray-400'>已解析 track ID: {form.track_id}</p>
          )}
        </div>

        <div>
          <label className='mb-1.5 block text-sm font-medium'>艺术家</label>
          <input
            value={form.artist || ''}
            onChange={(e) => setForm((f) => ({ ...f, artist: e.target.value }))}
            placeholder='Carpenters'
            className='w-full rounded-xl border border-white/40 bg-white/60 px-4 py-2.5 text-sm backdrop-blur-sm outline-none focus:border-[var(--color-brand)]'
          />
        </div>

        <div>
          <label className='mb-1.5 block text-sm font-medium'>封面 URL</label>
          <input
            value={form.artwork || ''}
            onChange={(e) => setForm((f) => ({ ...f, artwork: e.target.value }))}
            placeholder='https://...（可留空，自动抓取）'
            className='w-full rounded-xl border border-white/40 bg-white/60 px-4 py-2.5 text-sm backdrop-blur-sm outline-none focus:border-[var(--color-brand)]'
          />
        </div>

        <div>
          <label className='mb-1.5 block text-sm font-medium'>预览音频 URL</label>
          <input
            value={form.preview_url || ''}
            onChange={(e) => setForm((f) => ({ ...f, preview_url: e.target.value }))}
            placeholder='https://...（可留空，自动抓取）'
            className='w-full rounded-xl border border-white/40 bg-white/60 px-4 py-2.5 text-sm backdrop-blur-sm outline-none focus:border-[var(--color-brand)]'
          />
        </div>

        <div className='flex gap-4'>
          <div className='flex-1'>
            <label className='mb-1.5 block text-sm font-medium'>排序</label>
            <input
              type='number'
              value={form.sort_order ?? 0}
              onChange={(e) => setForm((f) => ({ ...f, sort_order: parseInt(e.target.value) || 0 }))}
              className='w-full rounded-xl border border-white/40 bg-white/60 px-4 py-2.5 text-sm backdrop-blur-sm outline-none focus:border-[var(--color-brand)]'
            />
          </div>
          <div className='flex items-end gap-2 pb-0.5'>
            <input
              type='checkbox'
              id='music-active'
              checked={form.is_active !== false}
              onChange={(e) => setForm((f) => ({ ...f, is_active: e.target.checked }))}
              className='accent-[var(--color-brand)] h-4 w-4 rounded'
            />
            <label htmlFor='music-active' className='text-sm font-medium'>启用</label>
          </div>
        </div>
      </div>

      {error && <p className='mt-3 text-sm text-red-500'>{error}</p>}

      <div className='mt-5 flex justify-end gap-2'>
        <button onClick={onClose} className='rounded-xl bg-white/60 px-4 py-2 text-sm hover:bg-white/80'>
          取消
        </button>
        <button
          onClick={handleSubmit}
          disabled={saving}
          className='rounded-xl bg-[var(--color-brand)] px-4 py-2 text-sm text-white transition-transform hover:scale-105 active:scale-95 disabled:opacity-50'
        >
          {saving ? '保存中...' : '保存'}
        </button>
      </div>
    </DialogModal>
  )
}
