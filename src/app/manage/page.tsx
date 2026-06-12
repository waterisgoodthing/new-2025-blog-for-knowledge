'use client'

import { useState, useEffect, Suspense } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import Link from 'next/link'
import { motion } from 'motion/react'
import { useNoteIndex } from '@/hooks/use-note-index'
import { deleteNote, batchDeleteNotes } from '@/lib/api/notes'
import { login, logout, getMe, loginWithPasskey, isPasskeyAvailable, checkPasskeyRegistered, type PasskeyStatusResult, type User } from '@/lib/api/auth'
import { toast } from 'sonner'
import { cn } from '@/lib/utils'
import { EmptyState } from '@/components/empty-state'
import Image from 'next/image'
import { useConfigStore } from '@/app/(home)/stores/config-store'
import { Compass, MessageSquare, BookOpen, FileText, AlertCircle, Info, Lock } from 'lucide-react'
import dayjs from 'dayjs'
import { MusicTab } from './music-tab'
import { RecommendationTab } from './recommendation-tab'
import { AITab } from './ai-tab'
import { SecurityTab } from './security-tab'
import { AuditTab } from './audit-tab'
import { listGuestMessages, moderateGuestMessage, type GuestMessage } from '@/lib/api/guest-messages'
import { LogOut } from 'lucide-react'
import { getContentDetailHref, getContentEditHref } from '@/lib/content-routes'
import { KnowledgeSidebar } from '@/app/notes/components/knowledge-sidebar'
import { SuggestionCard } from '@/app/notes/components/suggestion-card'
import { SiteSettingsPanel } from '@/app/(home)/config-dialog/site-settings-panel'

const typeLabels = { note: '笔记', blog: '博客', mistake: '错题' }
const typeColors = { note: 'bg-blue-500/20 text-blue-600', blog: 'bg-green-500/20 text-green-600', mistake: 'bg-red-500/20 text-red-600' }

type TabType = 'overview' | 'content' | 'folders-tags' | 'music' | 'ai' | 'settings' | 'security' | 'audit' | 'guestbook'

const tabs: { id: TabType; label: string; passkeyOnly?: boolean }[] = [
  { id: 'overview', label: '总览' },
  { id: 'content', label: '内容管理' },
  { id: 'folders-tags', label: '文件夹与标签' },
  { id: 'music', label: '音乐管理' },
  { id: 'ai', label: 'AI 管理' },
  { id: 'guestbook', label: '留言审核' },
  { id: 'settings', label: '页面设置', passkeyOnly: true },
  { id: 'security', label: '安全设置', passkeyOnly: true },
  { id: 'audit', label: '操作记录' },
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
	        canManage
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

function OverviewTab() {
  return (
    <div className='space-y-6'>
      <div className='grid grid-cols-2 gap-4 md:grid-cols-4'>
        {[
          { label: '笔记', color: 'bg-blue-500/10 text-blue-600' },
          { label: '博客', color: 'bg-green-500/10 text-green-600' },
          { label: '错题', color: 'bg-red-500/10 text-red-600' },
          { label: '待复习', color: 'bg-orange-500/10 text-orange-600' },
        ].map(card => (
          <div key={card.label} className={cn('rounded-2xl border border-white/40 p-4 backdrop-blur-sm', card.color)}>
            <div className='text-sm opacity-70'>{card.label}</div>
            <div className='mt-1 text-2xl font-bold'>--</div>
          </div>
        ))}
      </div>
      <div className='rounded-2xl border border-white/40 bg-white/60 p-6 backdrop-blur-sm'>
        <h3 className='mb-3 font-medium'>快速操作</h3>
        <div className='flex flex-wrap gap-2'>
          <Link href='/write-note' className='rounded-xl bg-[var(--color-brand)] px-4 py-2 text-sm text-white hover:scale-105'>写笔记</Link>
          <Link href='/write' className='rounded-xl bg-green-500/20 px-4 py-2 text-sm text-green-700 hover:bg-green-500/30'>写博客</Link>
          <Link href='/write-mistake' className='rounded-xl bg-red-500/20 px-4 py-2 text-sm text-red-700 hover:bg-red-500/30'>写错题</Link>
        </div>
      </div>
    </div>
  )
}

function FoldersTagsTab() {
  return (
    <div className='rounded-2xl border border-white/40 bg-white/60 p-6 backdrop-blur-sm'>
      <h3 className='mb-4 font-medium'>文件夹与标签管理</h3>
      <p className='text-sm text-gray-500'>文件夹和标签管理功能将在后续实现中完善。</p>
    </div>
  )
}


function LoginForm({ onLogin }: { onLogin: () => void }) {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [passkeyLoading, setPasskeyLoading] = useState(false)
  const [passkeySupported] = useState(() => isPasskeyAvailable())
  const [passkeyStatus, setPasskeyStatus] = useState<PasskeyStatusResult | null>(null)
  const { siteContent } = useConfigStore()

  useEffect(() => {
    if (!passkeySupported) {
      setPasskeyStatus({ registered: false })
      return
    }
    checkPasskeyRegistered().then(setPasskeyStatus)
  }, [passkeySupported])

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

  const handlePasskeyLogin = async () => {
    setError('')
    setPasskeyLoading(true)
    try {
      await loginWithPasskey()
      onLogin()
    } catch (err: any) {
      setError(err.message || 'Passkey 登录失败')
    } finally {
      setPasskeyLoading(false)
    }
  }

  const quickLinks = [
    { icon: BookOpen, label: '博客', href: '/blog' },
    { icon: FileText, label: '笔记', href: '/notes' },
    { icon: AlertCircle, label: '错题', href: '/mistakes' },
    { icon: Compass, label: '发现', href: '/discover' },
    { icon: MessageSquare, label: '留言', href: '/guestbook' },
    { icon: Info, label: '关于', href: '/about' },
  ]

  return (
    <div className='mx-auto max-w-sm px-4 py-12'>
      <div className='mb-8 flex flex-col items-center gap-3'>
        <Image
          src={siteContent.avatarUrl || '/images/avatar.png'}
          alt='avatar'
          width={56}
          height={56}
          className='rounded-full'
          style={{ boxShadow: '0 8px 24px -4px #E2D9CE' }}
        />
        <h1 className='text-xl font-bold text-gray-800'>{siteContent.meta.title || '管理'}</h1>
        <p className='text-center text-sm text-gray-400'>登录后即可管理内容、策展发现和审核留言</p>
      </div>

      {passkeySupported && passkeyStatus === null && (
        <div className='mb-4 text-center text-sm text-gray-400'>检查 Passkey 状态...</div>
      )}

      {passkeySupported && passkeyStatus && 'registered' in passkeyStatus && passkeyStatus.registered && (
        <>
          <button
            onClick={handlePasskeyLogin}
            disabled={passkeyLoading}
            className='flex w-full items-center justify-center gap-2 rounded-xl border border-white/40 bg-white/60 py-2.5 text-sm font-medium transition-colors hover:bg-white/80 disabled:opacity-50'
          >
            <Lock className='h-4 w-4' />
            {passkeyLoading ? '验证中...' : '使用 Passkey 登录'}
          </button>
          <p className='mt-2 text-center text-xs text-gray-400'>
            Passkey 登录拥有最高权限，可执行密码更改等敏感操作
          </p>

          <div className='my-5 flex items-center gap-3'>
            <div className='h-px flex-1 bg-white/20' />
            <span className='text-xs text-gray-400'>或使用密码</span>
            <div className='h-px flex-1 bg-white/20' />
          </div>
        </>
      )}

      {passkeySupported && passkeyStatus && 'registered' in passkeyStatus && !passkeyStatus.registered && (
        <div className='mb-5 rounded-xl border border-white/20 bg-white/30 px-4 py-3 text-center text-xs text-gray-500'>
          当前浏览器支持 Passkey，但服务器未注册 Passkey。使用密码登录后可在安全设置中注册。
        </div>
      )}

      {passkeySupported && passkeyStatus && 'error' in passkeyStatus && (
        <div className='mb-5 rounded-xl border border-red-200/40 bg-red-50/60 px-4 py-3 text-center text-xs text-red-600'>
          无法检查 Passkey 状态：{passkeyStatus.message}。可先使用密码登录。
        </div>
      )}

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
          {loading ? '登录中...' : '密码登录'}
        </button>
      </form>

      {!passkeySupported && (
        <p className='mt-3 text-center text-xs text-gray-400'>
          当前浏览器不支持 Passkey，仅可使用密码登录（普通权限）
        </p>
      )}

      <div className='mt-8 border-t border-white/20 pt-6'>
        <p className='mb-3 text-center text-xs text-gray-400'>浏览公开内容</p>
        <div className='flex flex-wrap justify-center gap-2'>
          {quickLinks.map(link => (
            <Link
              key={link.href}
              href={link.href}
              className='flex items-center gap-1.5 rounded-lg bg-white/40 px-3 py-1.5 text-xs text-gray-500 transition-colors hover:bg-white/60 hover:text-gray-700'
            >
              <link.icon className='h-3.5 w-3.5' />
              {link.label}
            </Link>
          ))}
        </div>
      </div>
    </div>
  )
}

function GuestbookTab() {
  const [messages, setMessages] = useState<GuestMessage[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState<'all' | 'visible' | 'hidden'>('all')

  const load = async (p: number, f: 'all' | 'visible' | 'hidden') => {
    setLoading(true)
    try {
      const statusParam = f === 'all' ? undefined : f
      const res = await listGuestMessages({ page: p, size: 30, status: statusParam as any })
      setMessages(res.items)
      setTotal(res.total)
    } catch {
      // silent
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load(1, filter) }, [filter])

  const handleModerate = async (id: string, newStatus: 'visible' | 'hidden') => {
    try {
      await moderateGuestMessage(id, newStatus)
      toast.success(newStatus === 'hidden' ? '已隐藏' : '已恢复可见')
      load(page, filter)
    } catch (e: any) {
      toast.error('操作失败: ' + (e?.message || '未知错误'))
    }
  }

  const attachmentLabels: Record<string, string> = { home: '首页', blog: '博客', note: '笔记', mistake: '错题' }

  return (
    <div className='space-y-4'>
      <div className='flex items-center gap-3'>
        <div className='flex gap-1 rounded-lg border border-white/40 bg-white/60 p-0.5'>
          {(['all', 'visible', 'hidden'] as const).map(f => (
            <button
              key={f}
              onClick={() => { setFilter(f); setPage(1) }}
              className={cn(
                'rounded-md px-3 py-1 text-xs transition-colors',
                filter === f ? 'bg-[var(--color-brand)] text-white' : 'text-gray-500 hover:text-gray-700'
              )}>
              {f === 'all' ? '全部' : f === 'visible' ? '可见' : '已隐藏'}
            </button>
          ))}
        </div>
        <span className='text-xs text-gray-400'>共 {total} 条留言</span>
      </div>

      {loading ? (
        <div className='py-12 text-center text-gray-400'>加载中...</div>
      ) : messages.length === 0 ? (
        <div className='py-12'>
          <EmptyState variant='no-content' title='暂无留言' description='还没有收到任何留言' />
        </div>
      ) : (
        <div className='space-y-2'>
          {messages.map(msg => (
            <div
              key={msg.id}
              className={cn(
                'rounded-xl border p-4 backdrop-blur-sm',
                msg.status === 'hidden' ? 'border-red-200/40 bg-red-50/30' : 'border-white/40 bg-white/60'
              )}>
              <div className='mb-2 flex items-center gap-2'>
                <span className='font-medium text-gray-700'>{msg.nickname || '匿名访客'}</span>
                {msg.attachment_type && (
                  <span className='rounded-full bg-gray-100 px-2 py-0.5 text-[10px] text-gray-500'>
                    {attachmentLabels[msg.attachment_type] || msg.attachment_type}
                    {msg.attachment_slug ? ` / ${msg.attachment_slug}` : ''}
                  </span>
                )}
                <span className={cn(
                  'rounded-full px-2 py-0.5 text-[10px]',
                  msg.status === 'visible' ? 'bg-green-100 text-green-600' : 'bg-red-100 text-red-600'
                )}>
                  {msg.status === 'visible' ? '可见' : '已隐藏'}
                </span>
                <span className='ml-auto text-xs text-gray-400'>
                  {dayjs(msg.created_at).format('MM-DD HH:mm')}
                </span>
              </div>
              <p className='whitespace-pre-wrap text-sm text-gray-600'>{msg.content}</p>
              <div className='mt-3 flex gap-2'>
                {msg.status === 'visible' ? (
                  <button
                    onClick={() => handleModerate(msg.id, 'hidden')}
                    className='rounded-lg bg-red-500/10 px-3 py-1 text-xs text-red-600 hover:bg-red-500/20'>
                    隐藏
                  </button>
                ) : (
                  <button
                    onClick={() => handleModerate(msg.id, 'visible')}
                    className='rounded-lg bg-green-500/10 px-3 py-1 text-xs text-green-600 hover:bg-green-500/20'>
                    恢复可见
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {total > 30 && (
        <div className='flex justify-center gap-2'>
          <button disabled={page <= 1} onClick={() => { const p = page - 1; setPage(p); load(p, filter) }} className='rounded-lg bg-white/60 px-3 py-1 text-sm disabled:opacity-40'>上一页</button>
          <span className='px-3 py-1 text-sm text-gray-500'>{page} / {Math.ceil(total / 30)}</span>
          <button disabled={page >= Math.ceil(total / 30)} onClick={() => { const p = page + 1; setPage(p); load(p, filter) }} className='rounded-lg bg-white/60 px-3 py-1 text-sm disabled:opacity-40'>下一页</button>
        </div>
      )}
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
  const validTabs: TabType[] = ['overview', 'content', 'folders-tags', 'music', 'ai', 'settings', 'security', 'audit', 'guestbook']
  const initialTab = validTabs.includes(tabParam as TabType) ? (tabParam as TabType) : 'content'
  const [activeTab, setActiveTab] = useState<TabType>(initialTab)
  const [authenticated, setAuthenticated] = useState(false)
  const [user, setUser] = useState<(User & { auth_level?: string }) | null>(null)
  const [checking, setChecking] = useState(true)

  useEffect(() => {
    const t = searchParams.get('tab')
    const nextTab = validTabs.includes(t as TabType) ? (t as TabType) : 'content'
    setActiveTab(nextTab)
  }, [searchParams])

  useEffect(() => {
    getMe()
      .then(u => {
        setUser(u)
        setAuthenticated(true)
      })
      .catch(() => {
        setAuthenticated(false)
      })
      .finally(() => setChecking(false))
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

  const handleLogout = async () => {
    await logout()
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
        <div className='flex gap-1 overflow-x-auto'>
          {tabs.map((tab) => {
            const isPasskeyLocked = tab.passkeyOnly && user?.auth_level !== 'passkey'
            return (
              <button
                key={tab.id}
                onClick={() => isPasskeyLocked ? null : handleTabChange(tab.id)}
                disabled={isPasskeyLocked}
                className={cn(
                  'relative flex items-center gap-1 whitespace-nowrap px-4 py-2.5 text-sm transition-colors',
                  activeTab === tab.id ? 'text-[var(--color-brand)]' : 'text-gray-500 hover:text-gray-700',
                  isPasskeyLocked && 'cursor-not-allowed opacity-40',
                )}
                title={isPasskeyLocked ? '需要 Passkey 认证' : undefined}
              >
                {isPasskeyLocked && <Lock className='h-3 w-3' />}
                {tab.label}
                {activeTab === tab.id && (
                  <motion.div
                    layoutId='manage-tab-indicator'
                    className='absolute right-0 bottom-0 left-0 h-0.5 bg-[var(--color-brand)]'
                  />
                )}
              </button>
            )
          })}
        </div>
      </div>

      {activeTab === 'overview' && <OverviewTab />}
      {activeTab === 'content' && <ContentTab />}
      {activeTab === 'folders-tags' && <FoldersTagsTab />}
      {activeTab === 'music' && <MusicTab />}
      {activeTab === 'ai' && <AITab />}
      {activeTab === 'settings' && (
        user?.auth_level === 'passkey' ? (
          <div className='rounded-2xl border border-white/40 bg-white/60 p-6 backdrop-blur-sm'>
            <SiteSettingsPanel />
          </div>
        ) : (
          <div className='py-20'>
            <EmptyState variant='not-logged-in' title='需要 Passkey 认证' description='页面设置仅限 Passkey 管理员访问' />
          </div>
        )
      )}
      {activeTab === 'security' && <SecurityTab authLevel={user?.auth_level} />}
      {activeTab === 'audit' && <AuditTab />}
      {activeTab === 'guestbook' && <GuestbookTab />}
    </div>
  )
}
