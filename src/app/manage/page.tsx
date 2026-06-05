'use client'

import { useState, useEffect, Suspense } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import Link from 'next/link'
import { motion } from 'motion/react'
import { useNoteIndex } from '@/hooks/use-note-index'
import { deleteNote, batchDeleteNotes } from '@/lib/api/notes'
import { login, isLoggedIn, logout, getMe, type User } from '@/lib/api/auth'
import { toast } from 'sonner'
import { cn } from '@/lib/utils'
import { EmptyState } from '@/components/empty-state'
import dayjs from 'dayjs'
import { MusicTab } from './music-tab'
import { RecommendationTab } from './recommendation-tab'
import { LogOut } from 'lucide-react'
import { getContentDetailHref, getContentEditHref } from '@/lib/content-routes'
import { KnowledgeSidebar } from '@/app/notes/components/knowledge-sidebar'
import { SuggestionCard } from '@/app/notes/components/suggestion-card'
import { SiteSettingsPanel } from '@/app/(home)/config-dialog/site-settings-panel'

const typeLabels = { note: '笔记', blog: '博客', mistake: '错题' }
const typeColors = { note: 'bg-blue-500/20 text-blue-600', blog: 'bg-green-500/20 text-green-600', mistake: 'bg-red-500/20 text-red-600' }

type TabType = 'content' | 'music' | 'recommendation' | 'settings'

const tabs: { id: TabType; label: string }[] = [
  { id: 'content', label: '内容管理' },
  { id: 'music', label: '音乐管理' },
  { id: 'recommendation', label: '推荐管理' },
  { id: 'settings', label: '网站设置' },
]

function ContentTab() {
  const [type, setType] = useState('')
  const [q, setQ] = useState('')
  const [page, setPage] = useState(1)
  const [selected, setSelected] = useState<Set<string>>(new Set())
  const [deleting, setDeleting] = useState(false)
  const [activeFilter, setActiveFilter] = useState('all')
  const [activeFolderId, setActiveFolderId] = useState<string | null>(null)
  const [activeTag, setActiveTag] = useState<string | null>(null)

  const handleFilterChange = (filter: string) => {
    setActiveFilter(filter)
    setPage(1)
    clearSelected()
    if (filter === 'all') setType('')
    else if (filter === 'inbox') setType('')
    else if (['note', 'blog', 'mistake'].includes(filter)) setType(filter)
  }

  const { data, isLoading, mutate } = useNoteIndex({
    type: type as any || undefined,
    q: q || undefined,
    tag: activeTag || undefined,
    folder_id: activeFolderId || undefined,
    inbox: activeFilter === 'inbox' ? true : undefined,
    page,
    size: 30,
  })

  const clearSelected = () => setSelected(new Set())

  const toggleSelect = (slug: string) => {
    setSelected(s => {
      const n = new Set(s)
      n.has(slug) ? n.delete(slug) : n.add(slug)
      return n
    })
  }

  const toggleAll = () => {
    if (!data) return
    setSelected(s => s.size === data.items.length ? new Set() : new Set(data.items.map(i => i.slug)))
  }

  const handleDeleteSelected = async () => {
    if (selected.size === 0) return
    const currentPageSlugs = new Set(data?.items.map(i => i.slug) ?? [])
    const staleSlugs = Array.from(selected).filter(s => !currentPageSlugs.has(s))
    if (staleSlugs.length > 0) {
      toast.warning('选中内容已变化，请重新选择')
      clearSelected()
      return
    }
    const selectedItems = data?.items.filter(i => selected.has(i.slug)) ?? []
    const typeCounts = selectedItems.reduce((acc, item) => {
      acc[item.type] = (acc[item.type] || 0) + 1
      return acc
    }, {} as Record<string, number>)
    const typeSummary = Object.entries(typeCounts)
      .map(([type, count]) => `${typeLabels[type as keyof typeof typeLabels]} ${count} 条`)
      .join('、')
    if (!confirm(`确定删除以下内容？\n${typeSummary}\n共 ${selected.size} 条，删除后不可恢复。`)) return
    setDeleting(true)
    try {
      await batchDeleteNotes(Array.from(selected))
      setSelected(new Set())
      mutate()
      toast.success(`已删除 ${selected.size} 条内容`)
    } catch (e: any) {
      toast.error('删除失败: ' + e.message)
    } finally {
      setDeleting(false)
    }
  }

  const handleDeleteOne = async (slug: string, type: string) => {
    const label = typeLabels[type as keyof typeof typeLabels] || '内容'
    if (!confirm(`确定删除该篇${label}？`)) return
    try {
      await deleteNote(slug)
      mutate()
      toast.success('已删除')
    } catch (e: any) {
      toast.error('删除失败: ' + e.message)
    }
  }

  return (
    <div className='flex gap-6'>
      <KnowledgeSidebar
        activeFilter={activeFilter}
        activeFolderId={activeFolderId}
        activeTag={activeTag}
        onFilterChange={handleFilterChange}
        onFolderChange={(id) => { setActiveFolderId(id); setPage(1); clearSelected() }}
        onTagChange={(tag) => { setActiveTag(tag); setPage(1); clearSelected() }}
      />
      <div className='min-w-0 flex-1'>
      <SuggestionCard onExecuted={() => mutate()} />
      <div className='mb-6 flex flex-wrap items-center gap-3'>
        <input
          value={q}
          onChange={e => { setQ(e.target.value); setPage(1); clearSelected() }}
          placeholder='搜索...'
          className='rounded-xl border border-white/40 bg-white/60 px-4 py-2 backdrop-blur-sm outline-none focus:border-[var(--color-brand)]'
        />
        <div className='flex gap-2'>
          {['', 'note', 'blog', 'mistake'].map(t => (
            <button
              key={t}
              onClick={() => { setType(t); setPage(1); clearSelected() }}
              className={cn(
                'rounded-full px-3 py-1 text-sm transition-colors',
                type === t ? 'bg-[var(--color-brand)] text-white' : 'bg-white/60 hover:bg-white/80'
              )}
            >
              {t ? typeLabels[t as keyof typeof typeLabels] : '全部'}
            </button>
          ))}
        </div>
        {selected.size > 0 && (
          <button
            onClick={handleDeleteSelected}
            disabled={deleting}
            className='ml-auto rounded-xl bg-red-500/20 px-4 py-2 text-sm text-red-600 hover:bg-red-500/30'
          >
            删除选中 ({selected.size})
          </button>
        )}
      </div>

      {isLoading ? (
        <div className='py-20 text-center text-gray-400'>加载中...</div>
      ) : data?.items.length === 0 ? (
        <div className='py-20'><EmptyState variant='no-content' title='还没有内容' description='创建笔记、博客或错题后会在这里显示' /></div>
      ) : (
        <div className='overflow-x-auto rounded-xl border border-white/40 bg-white/60 backdrop-blur-sm'>
          <table className='w-full text-sm'>
            <thead>
              <tr className='border-b border-white/20 text-left text-xs text-gray-500'>
                <th className='p-3'>
                  <input
                    type='checkbox'
                    checked={data && selected.size === data.items.length && data.items.length > 0}
                    onChange={toggleAll}
                  />
                </th>
                <th className='p-3'>标题</th>
                <th className='p-3'>类型</th>
                <th className='p-3'>标签</th>
                <th className='p-3'>日期</th>
                <th className='p-3'>操作</th>
              </tr>
            </thead>
            <tbody>
              {data?.items.map(item => (
                <tr key={item.id} className='border-b border-white/10 hover:bg-white/40'>
                  <td className='p-3'>
                    <input
                      type='checkbox'
                      checked={selected.has(item.slug)}
                      onChange={() => toggleSelect(item.slug)}
                    />
                  </td>
                  <td className='max-w-xs truncate p-3 font-medium'>
                    <Link href={getContentDetailHref(item.type, item.slug)} className='hover:text-[var(--color-brand)]'>
                      {item.title}
                    </Link>
                  </td>
                  <td className='p-3'>
                    <span className={cn('rounded-full px-2 py-0.5 text-xs', typeColors[item.type])}>
                      {typeLabels[item.type]}
                    </span>
                  </td>
                  <td className='p-3'>
                    <div className='flex flex-wrap gap-1'>
                      {item.tags.slice(0, 3).map(t => (
                        <span key={t.id} className='rounded bg-gray-200/60 px-1.5 py-0.5 text-xs text-gray-500'>
                          {t.name}
                        </span>
                      ))}
                    </div>
                  </td>
                  <td className='p-3 text-xs text-gray-500'>
                    {dayjs(item.updated_at).format('MM-DD HH:mm')}
                  </td>
                  <td className='p-3'>
                    <div className='flex gap-2'>
                      <Link
                        href={getContentEditHref(item.type, item.slug)}
                        className='rounded bg-white/60 px-2 py-1 text-xs hover:bg-white/80'
                      >
                        编辑
                      </Link>
                      <button
                        onClick={() => handleDeleteOne(item.slug, item.type)}
                        className='rounded bg-red-500/10 px-2 py-1 text-xs text-red-500 transition-colors hover:bg-red-500/20'
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

      {data && data.total > 30 && (
        <div className='mt-6 flex justify-center gap-2'>
          <button disabled={page <= 1} onClick={() => { setPage(p => p - 1); clearSelected() }} className='rounded-lg bg-white/60 px-3 py-1 text-sm disabled:opacity-40'>上一页</button>
          <span className='px-3 py-1 text-sm text-gray-500'>{page} / {Math.ceil(data.total / 30)}</span>
          <button disabled={page >= Math.ceil(data.total / 30)} onClick={() => { setPage(p => p + 1); clearSelected() }} className='rounded-lg bg-white/60 px-3 py-1 text-sm disabled:opacity-40'>下一页</button>
        </div>
      )}
      </div>
    </div>
  )
}

function LoginForm({ onLogin }: { onLogin: () => void }) {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await login(username, password)
      onLogin()
    } catch (err: any) {
      setError(err.message || '登录失败')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className='mx-auto max-w-sm px-4 py-20'>
      <h1 className='mb-8 text-center text-2xl font-bold'>管理面板登录</h1>
      <form onSubmit={handleSubmit} className='space-y-4'>
        <div>
          <label htmlFor='username' className='mb-1 block text-sm text-gray-500'>用户名</label>
          <input
            id='username'
            type='text'
            value={username}
            onChange={e => setUsername(e.target.value)}
            required
            className='w-full rounded-xl border border-white/40 bg-white/60 px-4 py-2.5 backdrop-blur-sm outline-none focus:border-[var(--color-brand)]'
          />
        </div>
        <div>
          <label htmlFor='password' className='mb-1 block text-sm text-gray-500'>密码</label>
          <input
            id='password'
            type='password'
            value={password}
            onChange={e => setPassword(e.target.value)}
            required
            className='w-full rounded-xl border border-white/40 bg-white/60 px-4 py-2.5 backdrop-blur-sm outline-none focus:border-[var(--color-brand)]'
          />
        </div>
        {error && <p className='text-sm text-red-500'>{error}</p>}
        <button
          type='submit'
          disabled={loading}
          className='w-full rounded-xl bg-[var(--color-brand)] py-2.5 text-sm text-white transition-transform hover:scale-[1.02] active:scale-[0.98] disabled:opacity-50'
        >
          {loading ? '登录中...' : '登录'}
        </button>
      </form>
      <p className='mt-4 text-center text-sm text-gray-400'>
        <Link href='/' className='text-[var(--color-brand)] underline'>返回首页</Link>
      </p>
    </div>
  )
}

export default function ManagePage() {
  return (
    <Suspense fallback={<div className='mx-auto max-w-5xl px-4 py-20 text-center text-gray-400'>加载中...</div>}>
      <ManagePageInner />
    </Suspense>
  )
}

function ManagePageInner() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const tabParam = searchParams.get('tab')
  const validTabs: TabType[] = ['content', 'music', 'recommendation', 'settings']
  const initialTab = validTabs.includes(tabParam as TabType) ? (tabParam as TabType) : 'content'
  const [activeTab, setActiveTab] = useState<TabType>(initialTab)
  const [authenticated, setAuthenticated] = useState(false)
  const [user, setUser] = useState<User | null>(null)
  const [checking, setChecking] = useState(true)

  useEffect(() => {
    const t = searchParams.get('tab')
    const nextTab = validTabs.includes(t as TabType) ? (t as TabType) : 'content'
    setActiveTab(nextTab)
  }, [searchParams])

  useEffect(() => {
    if (isLoggedIn()) {
      getMe()
        .then(u => {
          setUser(u)
          setAuthenticated(true)
        })
        .catch(() => {
          logout()
          setAuthenticated(false)
        })
        .finally(() => setChecking(false))
    } else {
      setChecking(false)
    }
  }, [])

  const handleTabChange = (tab: TabType) => {
    setActiveTab(tab)
    router.push(`/manage?tab=${tab}`)
  }

  const handleLogin = async () => {
    try {
      const u = await getMe()
      setUser(u)
      setAuthenticated(true)
    } catch {
      setAuthenticated(false)
    }
  }

  const handleLogout = () => {
    logout()
    setAuthenticated(false)
    setUser(null)
  }

  if (checking) {
    return (
      <div className='mx-auto max-w-xl px-4 py-20 text-center text-gray-400'>
        验证中...
      </div>
    )
  }

  if (!authenticated) {
    return <LoginForm onLogin={handleLogin} />
  }

  return (
    <div className='mx-auto max-w-5xl px-4 py-8'>
      <div className='mb-6 flex items-center justify-between'>
        <motion.h1 initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} className='text-2xl font-bold'>
          管理面板
        </motion.h1>
        <div className='flex items-center gap-3'>
          <span className='max-w-[120px] truncate text-sm text-gray-400'>{user?.username}</span>
          <button
            onClick={handleLogout}
            className='inline-flex items-center gap-1.5 rounded-lg bg-white/60 px-3 py-1.5 text-sm text-gray-500 transition-colors hover:bg-white/80 hover:text-gray-700'
            aria-label='退出登录'
          >
            <LogOut className='h-3.5 w-3.5' />
            退出
          </button>
        </div>
      </div>

      <div className='mb-6 border-b border-white/20'>
        <div className='flex gap-1'>
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => handleTabChange(tab.id)}
              className={cn(
                'relative px-4 py-2.5 text-sm transition-colors',
                activeTab === tab.id ? 'text-[var(--color-brand)]' : 'text-gray-500 hover:text-gray-700'
              )}
            >
              {tab.label}
              {activeTab === tab.id && (
                <motion.div
                  layoutId='manage-tab-indicator'
                  className='absolute right-0 bottom-0 left-0 h-0.5 bg-[var(--color-brand)]'
                />
              )}
            </button>
          ))}
        </div>
      </div>

      {activeTab === 'content' && <ContentTab />}
      {activeTab === 'music' && <MusicTab />}
      {activeTab === 'recommendation' && <RecommendationTab />}
      {activeTab === 'settings' && (
        <div className='rounded-2xl border border-white/40 bg-white/60 p-6 backdrop-blur-sm'>
          <SiteSettingsPanel />
        </div>
      )}
    </div>
  )
}
