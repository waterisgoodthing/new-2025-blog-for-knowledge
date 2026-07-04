'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import {
  Archive,
  BookOpenCheck,
  Bot,
  Brain,
  ClipboardCheck,
  FileQuestion,
  LayoutDashboard,
  Library,
  ListChecks,
  Settings,
} from 'lucide-react'
import { cn } from '@/lib/utils'

const workspaceLinks = [
  { href: '/manage/dashboard', label: '总览', icon: LayoutDashboard },
  { href: '/manage/drafts', label: '待审核', icon: ClipboardCheck },
  { href: '/manage/questions', label: '题库', icon: FileQuestion },
  { href: '/manage/mistakes', label: '错题', icon: BookOpenCheck },
  { href: '/manage/review', label: '复习', icon: Brain },
  { href: '/manage/subjects', label: '科目', icon: Library },
  { href: '/manage/attachments', label: '附件', icon: Archive },
  { href: '/manage/ai', label: 'AI', icon: Bot },
  { href: '/manage/jobs', label: '任务', icon: ListChecks },
  { href: '/manage/settings', label: '设置', icon: Settings },
] as const

export function ManageSidebar() {
  const pathname = usePathname()

  return (
    <aside
      aria-label='学习管理导航'
      className='w-full min-w-0 overflow-hidden border-white/45 bg-white/48 shadow-[0_18px_70px_-38px_rgba(66,107,113,0.45)] backdrop-blur-xl md:min-h-[calc(100svh-3rem)] md:w-56 md:shrink-0 md:rounded-[28px] md:border'
    >
      <nav className='flex w-full max-w-full gap-1 overflow-x-auto px-1 pb-2 md:flex-col md:gap-1.5 md:p-3'>
        {workspaceLinks.map(({ href, label, icon: Icon }) => {
          const active = pathname === href

          return (
            <Link
              key={href}
              href={href}
              aria-current={active ? 'page' : undefined}
              className={cn(
                'group flex min-w-fit items-center gap-2 rounded-2xl px-3 py-2.5 text-sm transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-brand)]/45 md:w-full',
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
      </nav>
    </aside>
  )
}
