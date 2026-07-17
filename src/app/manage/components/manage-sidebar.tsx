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
  FileQuestion,
  Library,
  Search,
  Settings,
  Sun,
} from 'lucide-react'
import { cn } from '@/lib/utils'

type LucideIcon = typeof Sun

type NavItem = {
  href: string
  label: string
  icon: LucideIcon
  match: (pathname: string) => boolean
}

type NavGroup = {
  title: string
  items: NavItem[]
}

export const navGroups: NavGroup[] = [
  {
    title: 'Workspace',
    items: [
      {
        href: '/manage/dashboard',
        label: 'Dashboard',
        icon: Sun,
        match: (p) => p === '/manage/dashboard',
      },
      {
        href: '/manage/subjects',
        label: 'Subjects',
        icon: Library,
        match: (p) => p === '/manage/subjects' || p.startsWith('/manage/subjects/'),
      },
      {
        href: '/manage/knowledge-points',
        label: 'Knowledge Points',
        icon: DatabaseZap,
        match: (p) =>
          p === '/manage/knowledge-points' ||
          p.startsWith('/manage/knowledge-points/'),
      },
    ],
  },
  {
    title: 'Learning',
    items: [
      {
        href: '/manage/questions',
        label: 'Questions',
        icon: FileQuestion,
        match: (p) => p === '/manage/questions' || p.startsWith('/manage/questions/'),
      },
      {
        href: '/manage/mistakes',
        label: 'Mistakes',
        icon: ClipboardCheck,
        match: (p) => p === '/manage/mistakes' || p.startsWith('/manage/mistakes/'),
      },
      {
        href: '/manage/review',
        label: 'Review',
        icon: Brain,
        match: (p) => p === '/manage/review',
      },
      {
        href: '/manage/attachments',
        label: 'Attachments',
        icon: Archive,
        match: (p) => p === '/manage/attachments' || p.startsWith('/manage/attachments/'),
      },
    ],
  },
  {
    title: 'System',
    items: [
      {
        href: '/manage/ai',
        label: 'AI',
        icon: Bot,
        match: (p) => p === '/manage/ai' || p.startsWith('/manage/ai/'),
      },
      {
        href: '/manage/jobs',
        label: 'Jobs',
        icon: Archive,
        match: (p) => p === '/manage/jobs' || p.startsWith('/manage/jobs/'),
      },
      {
        href: '/manage/search',
        label: 'Search',
        icon: Search,
        match: (p) => p === '/manage/search',
      },
      {
        href: '/manage/analytics',
        label: 'Analytics',
        icon: BarChart3,
        match: (p) => p === '/manage/analytics',
      },
      {
        href: '/manage/settings',
        label: 'Settings',
        icon: Settings,
        match: (p) => p === '/manage/settings',
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
            {group.items.map(({ href, label, icon: Icon, match }) => {
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
                  <span>{label}</span>
                </Link>
              )
            })}
          </div>
        ))}
      </nav>
    </aside>
  )
}
