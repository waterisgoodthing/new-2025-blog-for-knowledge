'use client'

import { useState, useEffect, useCallback } from 'react'
import { ExternalLink, RefreshCw, Music, Play, Pause } from 'lucide-react'
import { EmptyState } from '@/components/empty-state'
import { getPlaylist, deleteMusicItem, updateMusicItem, type MusicItem } from '@/lib/api/music'
import {
  getNetEaseConfig,
  checkNetEaseHealth,
  getSourceRules,
  syncAllCandidates,
  getManageDailySong,
  getSongHistory,
  getCandidates,
  type DailySongItem,
  type SourceRule,
  type MusicCandidateItem,
} from '@/lib/api/music-manage'
import { MusicFormModal } from './music-form-modal'
import { toast } from 'sonner'
import dayjs from 'dayjs'

type MusicSubTab = 'legacy' | 'daily' | 'candidates' | 'config'

export function MusicTab() {
  const [subTab, setSubTab] = useState<MusicSubTab>('daily')
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

  const subTabs: { id: MusicSubTab; label: string }[] = [
    { id: 'daily', label: '每日歌曲' },
    { id: 'candidates', label: '候选池' },
    { id: 'legacy', label: '手动列表' },
    { id: 'config', label: 'NetEase 配置' },
  ]

  return (
    <div>
      <div className='mb-4 flex gap-1 border-b border-white/20'>
        {subTabs.map(t => (
          <button
            key={t.id}
            onClick={() => setSubTab(t.id)}
            className={`px-3 py-2 text-sm transition-colors ${
              subTab === t.id ? 'border-b-2 border-[var(--color-brand)] text-[var(--color-brand)]' : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {subTab === 'daily' && <DailySongSection />}
      {subTab === 'candidates' && <CandidatesSection />}
      {subTab === 'legacy' && (
        <LegacyMusicSection
          items={items}
          loading={loading}
          onDelete={handleDelete}
          onToggleActive={handleToggleActive}
          onAdd={() => { setEditing(null); setModalOpen(true) }}
          onEdit={(item) => { setEditing(item); setModalOpen(true) }}
        />
      )}
      {subTab === 'config' && <NetEaseConfigSection />}

      <MusicFormModal open={modalOpen} onClose={() => setModalOpen(false)} onSuccess={load} editingItem={editing} />
    </div>
  )
}

function DailySongSection() {
  const [today, setToday] = useState<DailySongItem | null>(null)
  const [history, setHistory] = useState<DailySongItem[]>([])
  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState(false)

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const [t, h] = await Promise.all([
        getManageDailySong().catch(() => null),
        getSongHistory(30).catch(() => []),
      ])
      setToday(t)
      setHistory(h)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { load() }, [load])

  const handleGenerate = async () => {
    setGenerating(true)
    try {
      await fetch('/api/music/manage/generate-song', { method: 'POST', credentials: 'include' })
      await load()
      toast.success('今日歌曲已生成')
    } catch (e: any) {
      toast.error('生成失败: ' + (e.message || '无候选歌曲'))
    } finally {
      setGenerating(false)
    }
  }

  if (loading) return <div className='py-10 text-center text-gray-400'>加载中...</div>

  return (
    <div className='space-y-6'>
      <div className='rounded-xl border border-white/40 bg-white/60 p-5 backdrop-blur-sm'>
        <div className='mb-3 flex items-center justify-between'>
          <h3 className='font-medium'>今日歌曲</h3>
          <button
            onClick={handleGenerate}
            disabled={generating}
            className='inline-flex items-center gap-1.5 rounded-lg bg-[var(--color-brand)] px-3 py-1.5 text-sm text-white disabled:opacity-50'
          >
            <RefreshCw className={`h-3.5 w-3.5 ${generating ? 'animate-spin' : ''}`} />
            {generating ? '生成中...' : '生成今日歌曲'}
          </button>
        </div>
        {today ? (
          <div className='flex items-center gap-4'>
            <div className='h-16 w-16 overflow-hidden rounded-lg bg-white/60'>
              {today.artwork_url ? (
                <img src={today.artwork_url} alt={today.title} className='h-full w-full object-cover' />
              ) : (
                <div className='flex h-full w-full items-center justify-center text-2xl text-gray-400'>♪</div>
              )}
            </div>
            <div>
              <div className='font-medium'>{today.title}</div>
              <div className='text-sm text-gray-500'>{today.artist} · {today.album}</div>
              <div className='text-xs text-gray-400'>{today.date}</div>
              {today.recommendation_reason && (
                <div className='mt-1 text-xs text-blue-600'>{today.recommendation_reason}</div>
              )}
            </div>
            {today.netease_url && (
              <a href={today.netease_url} target='_blank' rel='noopener noreferrer' className='ml-auto text-[var(--color-brand)]'>
                <ExternalLink size={16} />
              </a>
            )}
          </div>
        ) : (
          <p className='text-sm text-gray-400'>今日歌曲尚未生成，点击上方按钮生成。</p>
        )}
      </div>

      {history.length > 0 && (
        <div className='rounded-xl border border-white/40 bg-white/60 p-5 backdrop-blur-sm'>
          <h3 className='mb-3 font-medium'>历史歌曲</h3>
          <div className='space-y-2'>
            {history.map(song => (
              <div key={song.id} className='flex items-center gap-3 rounded-lg bg-white/40 p-3'>
                <div className='h-10 w-10 overflow-hidden rounded bg-white/60'>
                  {song.artwork_url ? (
                    <img src={song.artwork_url} alt='' className='h-full w-full object-cover' />
                  ) : (
                    <div className='flex h-full w-full items-center justify-center text-gray-400'>♪</div>
                  )}
                </div>
                <div className='min-w-0 flex-1'>
                  <div className='truncate text-sm font-medium'>{song.title}</div>
                  <div className='text-xs text-gray-500'>{song.artist}</div>
                </div>
                <div className='text-xs text-gray-400'>{song.date}</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

function CandidatesSection() {
  const [candidates, setCandidates] = useState<MusicCandidateItem[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [syncing, setSyncing] = useState(false)
  const [page, setPage] = useState(1)

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const data = await getCandidates(page)
      setCandidates(data.items)
      setTotal(data.total)
    } catch {
      // ignore
    } finally {
      setLoading(false)
    }
  }, [page])

  useEffect(() => { load() }, [load])

  const handleSync = async () => {
    setSyncing(true)
    try {
      const result = await syncAllCandidates()
      toast.success(`同步完成: ${result.total_synced} 首歌曲`)
      await load()
    } catch (e: any) {
      toast.error('同步失败: ' + e.message)
    } finally {
      setSyncing(false)
    }
  }

  return (
    <div>
      <div className='mb-4 flex items-center justify-between'>
        <p className='text-sm text-gray-500'>候选池共 {total} 首歌曲</p>
        <button
          onClick={handleSync}
          disabled={syncing}
          className='inline-flex items-center gap-1.5 rounded-lg bg-[var(--color-brand)] px-3 py-1.5 text-sm text-white disabled:opacity-50'
        >
          <RefreshCw className={`h-3.5 w-3.5 ${syncing ? 'animate-spin' : ''}`} />
          {syncing ? '同步中...' : '同步候选池'}
        </button>
      </div>

      {loading ? (
        <div className='py-10 text-center text-gray-400'>加载中...</div>
      ) : candidates.length === 0 ? (
        <div className='py-10'>
          <EmptyState variant='no-content' title='候选池为空' description='点击"同步候选池"从 NetEase 获取歌曲' />
        </div>
      ) : (
        <div className='overflow-x-auto rounded-xl border border-white/40 bg-white/60 backdrop-blur-sm'>
          <table className='w-full text-sm'>
            <thead>
              <tr className='border-b border-white/20 text-left text-xs text-gray-500'>
                <th className='p-3'>封面</th>
                <th className='p-3'>标题</th>
                <th className='p-3'>艺术家</th>
                <th className='p-3'>专辑</th>
                <th className='p-3'>链接</th>
              </tr>
            </thead>
            <tbody>
              {candidates.map(c => (
                <tr key={c.id} className='border-b border-white/10 hover:bg-white/40'>
                  <td className='p-3'>
                    <div className='h-10 w-10 overflow-hidden rounded-lg bg-white/60'>
                      {c.artwork_url ? (
                        <img src={c.artwork_url} alt='' className='h-full w-full object-cover' />
                      ) : (
                        <div className='flex h-full w-full items-center justify-center text-xs text-gray-400'>♪</div>
                      )}
                    </div>
                  </td>
                  <td className='max-w-[200px] truncate p-3 font-medium'>{c.title}</td>
                  <td className='max-w-[150px] truncate p-3 text-gray-500'>{c.artist || '-'}</td>
                  <td className='max-w-[150px] truncate p-3 text-gray-500'>{c.album || '-'}</td>
                  <td className='p-3'>
                    {c.netease_url && (
                      <a href={c.netease_url} target='_blank' rel='noopener noreferrer' className='text-[var(--color-brand)]'>
                        <ExternalLink size={14} />
                      </a>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}

function LegacyMusicSection({ items, loading, onDelete, onToggleActive, onAdd, onEdit }: {
  items: MusicItem[]
  loading: boolean
  onDelete: (item: MusicItem) => void
  onToggleActive: (item: MusicItem) => void
  onAdd: () => void
  onEdit: (item: MusicItem) => void
}) {
  return (
    <div>
      <div className='mb-4 flex items-center justify-between'>
        <p className='text-sm text-gray-500'>手动管理音乐列表（旧版）</p>
        <button onClick={onAdd} className='rounded-xl bg-[var(--color-brand)] px-4 py-2 text-sm text-white'>
          添加音乐
        </button>
      </div>

      {loading ? (
        <div className='py-10 text-center text-gray-400'>加载中...</div>
      ) : items.length === 0 ? (
        <div className='py-10'><EmptyState variant='no-content' title='暂无音乐' description='点击"添加音乐"开始添加' /></div>
      ) : (
        <div className='overflow-x-auto rounded-xl border border-white/40 bg-white/60 backdrop-blur-sm'>
          <table className='w-full text-sm'>
            <thead>
              <tr className='border-b border-white/20 text-left text-xs text-gray-500'>
                <th className='p-3'>封面</th>
                <th className='p-3'>标题</th>
                <th className='p-3'>艺术家</th>
                <th className='p-3'>状态</th>
                <th className='p-3'>操作</th>
              </tr>
            </thead>
            <tbody>
              {items.map(item => (
                <tr key={item.id} className='border-b border-white/10 hover:bg-white/40'>
                  <td className='p-3'>
                    <div className='h-10 w-10 overflow-hidden rounded-lg bg-white/60'>
                      {item.artwork ? <img src={item.artwork} alt={item.title} className='h-full w-full object-cover' /> : <div className='flex h-full w-full items-center justify-center text-gray-400'>♪</div>}
                    </div>
                  </td>
                  <td className='max-w-[200px] truncate p-3 font-medium'>{item.title}</td>
                  <td className='p-3 text-gray-500'>{item.artist || '-'}</td>
                  <td className='p-3'>
                    <button onClick={() => onToggleActive(item)} className={`h-5 w-9 rounded-full ${item.is_active ? 'bg-[var(--color-brand)]' : 'bg-gray-300'}`}>
                      <span className={`block h-4 w-4 rounded-full bg-white shadow ${item.is_active ? 'ml-[18px]' : 'ml-0.5'}`} />
                    </button>
                  </td>
                  <td className='p-3'>
                    <div className='flex gap-2'>
                      <button onClick={() => onEdit(item)} className='rounded bg-white/60 px-2 py-1 text-xs hover:bg-white/80'>编辑</button>
                      <button onClick={() => onDelete(item)} className='rounded bg-red-500/10 px-2 py-1 text-xs text-red-500 hover:bg-red-500/20'>删除</button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
         </table>
        </div>
      )}
    </div>
  )
}

function NetEaseConfigSection() {
  const [health, setHealth] = useState<{ status: string } | null>(null)
  const [checking, setChecking] = useState(false)

  const handleCheck = async () => {
    setChecking(true)
    try {
      const result = await checkNetEaseHealth()
      setHealth(result)
    } catch (e: any) {
      setHealth({ status: 'error' })
    } finally {
      setChecking(false)
    }
  }

  return (
    <div className='space-y-4'>
      <div className='rounded-xl border border-white/40 bg-white/60 p-5 backdrop-blur-sm'>
        <h3 className='mb-3 font-medium'>NetEase API 状态</h3>
        <div className='flex items-center gap-3'>
          <button
            onClick={handleCheck}
            disabled={checking}
            className='rounded-lg bg-[var(--color-brand)] px-4 py-2 text-sm text-white disabled:opacity-50'
          >
            {checking ? '检查中...' : '检查连接'}
          </button>
          {health && (
            <span className={`rounded-full px-3 py-1 text-xs ${
              health.status === 'ok' ? 'bg-green-500/10 text-green-600' : 'bg-red-500/10 text-red-600'
            }`}>
              {health.status === 'ok' ? '连接正常' : '连接失败'}
            </span>
          )}
        </div>
      </div>

      <div className='rounded-xl border border-white/40 bg-white/60 p-5 backdrop-blur-sm'>
        <h3 className='mb-3 font-medium'>数据源规则</h3>
        <SourceRulesList />
      </div>
    </div>
  )
}

function SourceRulesList() {
  const [rules, setRules] = useState<SourceRule[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getSourceRules().then(setRules).catch(() => {}).finally(() => setLoading(false))
  }, [])

  if (loading) return <div className='text-sm text-gray-400'>加载中...</div>

  return (
    <div className='space-y-2'>
      {rules.map(rule => (
        <div key={rule.id} className='flex items-center justify-between rounded-lg bg-white/40 px-3 py-2'>
          <div className='flex items-center gap-2'>
            <span className='rounded bg-purple-500/10 px-2 py-0.5 text-xs text-purple-600'>{rule.source_type}</span>
            <span className='text-sm font-medium'>{rule.source_value}</span>
          </div>
          <span className={`text-xs ${rule.enabled ? 'text-green-600' : 'text-gray-400'}`}>
            {rule.enabled ? '启用' : '禁用'}
          </span>
        </div>
      ))}
    </div>
  )
}
