'use client'

import { useState, useEffect, useCallback } from 'react'
import { ExternalLink } from 'lucide-react'
import { EmptyState } from '@/components/empty-state'
import { getPlaylist, deleteMusicItem, updateMusicItem, type MusicItem } from '@/lib/api/music'
import { MusicFormModal } from './music-form-modal'
import { toast } from 'sonner'

export function MusicTab() {
  const [items, setItems] = useState<MusicItem[]>([])
  const [loading, setLoading] = useState(true)
  const [modalOpen, setModalOpen] = useState(false)
  const [editing, setEditing] = useState<MusicItem | null>(null)

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const data = await getPlaylist()
      setItems(data)
    } catch {
      // ignore
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    load()
  }, [load])

  const handleDelete = async (item: MusicItem) => {
    if (!confirm(`确定删除「${item.title}」？`)) return
    try {
      await deleteMusicItem(item.id)
      load()
    } catch (e: any) {
      toast.error('删除失败: ' + e.message)
    }
  }

  const handleToggleActive = async (item: MusicItem) => {
    try {
      await updateMusicItem(item.id, { is_active: !item.is_active })
      load()
    } catch (e: any) {
      toast.error('更新失败: ' + e.message)
    }
  }

  const handleSortChange = async (item: MusicItem, value: string) => {
    const num = parseInt(value)
    if (isNaN(num)) return
    try {
      await updateMusicItem(item.id, { sort_order: num })
      load()
    } catch (e: any) {
      toast.error('更新失败: ' + e.message)
    }
  }

  const openAdd = () => {
    setEditing(null)
    setModalOpen(true)
  }

  const openEdit = (item: MusicItem) => {
    setEditing(item)
    setModalOpen(true)
  }

  return (
    <div>
      <div className='mb-4 flex items-center justify-between'>
        <p className='text-secondary text-sm'>管理首页音乐卡片的曲目列表</p>
        <button
          onClick={openAdd}
          className='rounded-xl bg-[var(--color-brand)] px-4 py-2 text-sm text-white transition-transform hover:scale-105 active:scale-95'
        >
          添加音乐
        </button>
      </div>

      {loading ? (
        <div className='py-20 text-center text-gray-400'>加载中...</div>
      ) : items.length === 0 ? (
        <div className='py-20'><EmptyState variant='no-content' title='暂无音乐' description='点击"添加音乐"开始添加' /></div>
      ) : (
        <div className='overflow-x-auto rounded-xl border border-white/40 bg-white/60 backdrop-blur-sm'>
          <table className='w-full text-sm'>
            <thead>
              <tr className='border-b border-white/20 text-left text-xs text-gray-500'>
                <th className='p-3'>封面</th>
                <th className='p-3'>标题</th>
                <th className='p-3'>艺术家</th>
                <th className='p-3'>链接</th>
                <th className='p-3'>排序</th>
                <th className='p-3'>状态</th>
                <th className='p-3'>操作</th>
              </tr>
            </thead>
            <tbody>
              {items.map((item) => (
                <tr key={item.id} className='border-b border-white/10 hover:bg-white/40'>
                  <td className='p-3'>
                    <div className='h-10 w-10 overflow-hidden rounded-lg bg-white/60'>
                      {item.artwork ? (
                        <img src={item.artwork} alt={item.title} className='h-full w-full object-cover' />
                      ) : (
                        <div className='flex h-full w-full items-center justify-center text-xs text-gray-400'>♪</div>
                      )}
                    </div>
                  </td>
                  <td className='max-w-[200px] truncate p-3 font-medium'>{item.title}</td>
                  <td className='max-w-[150px] truncate p-3 text-gray-500'>{item.artist || '-'}</td>
                  <td className='p-3'>
                    <a
                      href={item.apple_music_url}
                      target='_blank'
                      rel='noopener noreferrer'
                      className='inline-flex items-center gap-1 text-[var(--color-brand)] hover:underline'
                    >
                      <ExternalLink className='h-3.5 w-3.5' />
                    </a>
                  </td>
                  <td className='p-3'>
                    <input
                      type='number'
                      value={item.sort_order}
                      onChange={(e) => handleSortChange(item, e.target.value)}
                      className='w-16 rounded-lg border border-white/40 bg-white/60 px-2 py-1 text-xs backdrop-blur-sm outline-none focus:border-[var(--color-brand)]'
                    />
                  </td>
                  <td className='p-3'>
                    <button
                      onClick={() => handleToggleActive(item)}
                      className={`relative h-5 w-9 rounded-full transition-colors ${
                        item.is_active ? 'bg-[var(--color-brand)]' : 'bg-gray-300'
                      }`}
                    >
                      <span
                        className={`absolute top-0.5 h-4 w-4 rounded-full bg-white shadow transition-transform ${
                          item.is_active ? 'left-[18px]' : 'left-0.5'
                        }`}
                      />
                    </button>
                  </td>
                  <td className='p-3'>
                    <div className='flex gap-2'>
                      <button
                        onClick={() => openEdit(item)}
                        className='rounded bg-white/60 px-2 py-1 text-xs hover:bg-white/80'
                      >
                        编辑
                      </button>
                      <button
                        onClick={() => handleDelete(item)}
                        className='rounded bg-red-500/10 px-2 py-1 text-xs text-red-500 hover:bg-red-500/20'
                      >
                        删除
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <MusicFormModal open={modalOpen} onClose={() => setModalOpen(false)} onSuccess={load} editingItem={editing} />
    </div>
  )
}
