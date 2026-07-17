import Link from 'next/link'
import {
  Archive,
  ArrowUpRight,
  Bot,
  Brain,
  ClipboardList,
  Library,
  Search,
  Settings,
} from 'lucide-react'
import { ManagePageHeader } from '../../components/manage-page-header'

const workspaceEntries = [
  {
    label: 'Subjects',
    value: 'Coming Soon',
    href: '/manage/subjects',
    icon: Library,
  },
  {
    label: 'Questions',
    value: 'Coming Soon',
    href: '/manage/questions',
    icon: ClipboardList,
  },
  {
    label: 'Mistakes',
    value: 'Coming Soon',
    href: '/manage/mistakes',
    icon: Brain,
  },
  {
    label: 'Review',
    value: 'Coming Soon',
    href: '/manage/review',
    icon: Brain,
  },
  {
    label: 'Attachments',
    value: 'Coming Soon',
    href: '/manage/attachments',
    icon: Archive,
  },
  {
    label: 'Search',
    value: 'Coming Soon',
    href: '/manage/search',
    icon: Search,
  },
  {
    label: 'AI',
    value: 'Coming Soon',
    href: '/manage/ai',
    icon: Bot,
  },
  {
    label: 'Settings',
    value: 'Coming Soon',
    href: '/manage/settings',
    icon: Settings,
  },
] as const

export default function ManageDashboardPage() {
  return (
    <div className='space-y-10'>
      <ManagePageHeader
        eyebrow='Learning Workspace'
        title='Learning Workspace'
        description='Coming Soon. This Batch 1 dashboard is a static management shell only.'
      />

      <section aria-labelledby='workspace-status-title'>
        <div className='flex items-end justify-between gap-4 border-b border-white/55 pb-3'>
          <h2 id='workspace-status-title' className='font-medium text-slate-800'>
            Static workspace containers
          </h2>
          <span className='text-xs text-slate-400'>No API connected</span>
        </div>

        <div>
          {workspaceEntries.map(({ label, value, href, icon: Icon }) => (
            <Link
              key={href}
              href={href}
              className='group flex items-center gap-4 border-b border-white/45 py-5 transition-colors hover:bg-white/22 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-brand)]/45'
            >
              <span className='inline-flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-[var(--color-brand)]/9 text-[var(--color-brand)]'>
                <Icon className='h-4 w-4' aria-hidden='true' />
              </span>
              <span className='min-w-0 flex-1'>
                <span className='block font-medium text-slate-700'>{label}</span>
                <span className='mt-0.5 block text-xs text-slate-400'>
                  {value}
                </span>
              </span>
              <ArrowUpRight
                className='h-4 w-4 text-slate-300 transition-transform group-hover:-translate-y-0.5 group-hover:translate-x-0.5 group-hover:text-[var(--color-brand)]'
                aria-hidden='true'
              />
            </Link>
          ))}
        </div>
      </section>
    </div>
  )
}
