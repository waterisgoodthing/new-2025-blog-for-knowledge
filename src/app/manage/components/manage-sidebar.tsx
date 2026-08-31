'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import {
  Archive,
  BarChart3,
  Bot,
  Brain,
  ClipboardCheck,
  DatabaseZap,
  FilePenLine,
  FileQuestion,
  Library,
  ScanLine,
  Search,
  Settings,
  Sun,
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { manageCapabilityStates, type ManageCapabilityState } from '../(workspace)/capability-state'

type LucideIcon = typeof Sun

type NavItem = {
  href: string
  label: string
  icon: LucideIcon
  match: (pathname: string) => boolean
  status?: ManageCapabilityState
}

type NavGroup = {
  title: string
  items: NavItem[]
}

export const navGroups: NavGroup[] = [
  {
    title: '学习空间',
    items: [
      {
        href: '/manage/dashboard',
        label: '概览',
        icon: Sun,
        match: (p) => p === '/manage/dashboard',
      },
    ],
  },
  {
    title: '内容管理',
    items: [
      {
        href: '/manage/drafts',
        label: '草稿',
        icon: FilePenLine,
        match: (p) => p === '/manage/drafts' || p.startsWith('/manage/drafts/'),
        status: manageCapabilityStates.drafts,
      },
      {
        href: '/manage/questions',
        label: '题目',
        icon: FileQuestion,
        match: (p) => p === '/manage/questions' || p.startsWith('/manage/questions/'),
      },
      {
        href: '/manage/mistakes',
        label: '错题',
        icon: ClipboardCheck,
        match: (p) => p === '/manage/mistakes' || p.startsWith('/manage/mistakes/'),
      },
    ],
  },
  {
    title: '知识体系',
    items: [
      {
        href: '/manage/subjects',
        label: '科目',
        icon: Library,
        match: (p) => p === '/manage/subjects' || p.startsWith('/manage/subjects/'),
      },
      {
        href: '/manage/knowledge-points',
        label: '知识点',
        icon: DatabaseZap,
        match: (p) =>
          p === '/manage/knowledge-points' ||
          p.startsWith('/manage/knowledge-points/'),
      },
    ],
  },
  {
    title: '学习计划',
    items: [
      {
        href: '/manage/review',
        label: '复习',
        icon: Brain,
        match: (p) => p === '/manage/review',
      },
    ],
  },
  {
    title: '资料管理',
    items: [
      {
        href: '/manage/attachments',
        label: '附件',
        icon: Archive,
        match: (p) => p === '/manage/attachments' || p.startsWith('/manage/attachments/'),
      },
    ],
  },
  {
    title: '工具',
    items: [
      {
        href: '/manage/capture',
        label: '采集',
        icon: ScanLine,
        match: (p) => p === '/manage/capture' || p.startsWith('/manage/capture/'),
        status: manageCapabilityStates.capture,
      },
      {
        href: '/manage/ai',
        label: 'AI',
        icon: Bot,
        match: (p) => p === '/manage/ai' || p.startsWith('/manage/ai/'),
        status: manageCapabilityStates.ai,
      },
    ],
  },
  {
    title: '系统',
    items: [
      {
        href: '/manage/settings',
        label: '设置',
        icon: Settings,
        match: (p) => p === '/manage/settings',
      },
    ],
  },
  {
    title: '后续能力',
    items: [
      {
        href: '/manage/jobs',
        label: '任务',
        icon: Archive,
        match: (p) => p === '/manage/jobs' || p.startsWith('/manage/jobs/'),
        status: manageCapabilityStates.jobs,
      },
      {
        href: '/manage/search',
        label: '搜索',
        icon: Search,
        match: (p) => p === '/manage/search',
        status: manageCapabilityStates.search,
      },
      {
        href: '/manage/analytics',
        label: '分析',
        icon: BarChart3,
        match: (p) => p === '/manage/analytics',
        status: manageCapabilityStates.analytics,
      },
    ],
  },
]

export const allItems = navGroups.flatMap((g) => g.items)

export function ManageSidebar() {
  const pathname = usePathname()

  return (
    <aside
      aria-label='学习管理导航'
      className='hidden min-w-0 overflow-hidden border-white/45 bg-white/48 shadow-[0_18px_70px_-38px_rgba(66,107,113,0.45)] backdrop-blur-xl md:mr-0 md:block md:min-h-[calc(100svh-3rem)] md:w-56 md:shrink-0 md:rounded-[28px] md:border'
    >
      <nav
        className='hidden md:flex md:flex-col md:gap-4 md:p-3'
        aria-label='导航（桌面端分组）'
      >
        {navGroups.map((group) => (
          <div key={group.title} className='flex flex-col gap-1.5'>
            <p className='px-3 text-xs font-medium tracking-wide text-slate-400'>
              {group.title}
            </p>
            {group.items.map(({ href, label, icon: Icon, match, status }) => {
              const active = match(pathname)
              return (
                <Link
                  key={href}
                  href={href}
                  aria-current={active ? 'page' : undefined}
                  className={cn(
                    'group flex w-full items-center gap-2 rounded-2xl px-3 py-2.5 text-sm transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-brand)]/45',
                    active
                      ? 'bg-[var(--color-brand)]/14 font-medium text-[var(--color-brand)]'
                      : 'text-slate-500 hover:bg-white/65 hover:text-slate-800',
                  )}
                >
                  <Icon className='h-4 w-4 shrink-0' aria-hidden='true' />
                  <span className='min-w-0 flex-1'>{label}</span>
                  {status === 'deferred' ? (
                    <span className='text-[10px] text-slate-400'>后续</span>
                  ) : null}
                </Link>
              )
            })}
          </div>
        ))}
      </nav>
    </aside>
  )
}
