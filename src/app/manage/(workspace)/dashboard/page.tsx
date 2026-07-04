import Link from 'next/link'
import {
  Archive,
  ArrowUpRight,
  Bot,
  Brain,
  ClipboardCheck,
  Library,
  ListChecks,
  Settings,
} from 'lucide-react'
import { ManagePageHeader } from '../../components/manage-page-header'

const workspaceStatus = [
  {
    label: '待审核',
    value: '尚未接入',
    href: '/manage/drafts',
    icon: ClipboardCheck,
    batch: 'Batch 3',
  },
  {
    label: '待复习',
    value: '尚未接入',
    href: '/manage/review',
    icon: Brain,
    batch: 'Batch 4',
  },
  {
    label: '科目与知识点',
    value: '尚未接入',
    href: '/manage/subjects',
    icon: Library,
    batch: 'Batch 2',
  },
  {
    label: '附件',
    value: '私有上传已接入；OCR 暂未启用',
    href: '/manage/attachments',
    icon: Archive,
    batch: 'Batch 5',
  },
  {
    label: 'AI 控制台',
    value: '占位；第一版暂未启用',
    href: '/manage/ai',
    icon: Bot,
    batch: 'Batch 6',
  },
  {
    label: '任务观察',
    value: '占位；无后台队列',
    href: '/manage/jobs',
    icon: ListChecks,
    batch: 'Batch 6',
  },
  {
    label: '系统设置',
    value: '占位；无保存请求',
    href: '/manage/settings',
    icon: Settings,
    batch: 'Batch 6',
  },
] as const

export default function ManageDashboardPage() {
  return (
    <div className='space-y-10'>
      <ManagePageHeader
        eyebrow='Batch 1 · 工作区壳层'
        title='总览'
        description='这里先建立清晰的管理入口。业务数据会在对应批次完成后接入。'
      />

      <section aria-labelledby='workspace-status-title'>
        <div className='flex items-end justify-between gap-4 border-b border-white/55 pb-3'>
          <div>
            <h2 id='workspace-status-title' className='font-medium text-slate-800'>
              MVP 工作区
            </h2>
            <p className='mt-1 text-xs text-slate-400'>当前仅提供导航，不展示虚构数据。</p>
          </div>
          <span className='text-xs text-slate-400'>{workspaceStatus.length} 个入口</span>
        </div>

        <div>
          {workspaceStatus.map(({ label, value, href, icon: Icon, batch }) => (
            <Link
              key={href}
              href={href}
              className='group flex items-center gap-4 border-b border-white/45 py-5 transition-colors hover:bg-white/22 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-brand)]/45'
            >
              <span className='inline-flex h-10 w-10 shrink-0 items-center justify-center rounded-2xl bg-[var(--color-brand)]/9 text-[var(--color-brand)]'>
                <Icon className='h-4 w-4' aria-hidden='true' />
              </span>
              <span className='min-w-0 flex-1'>
                <span className='block font-medium text-slate-700'>{label}</span>
                <span className='mt-0.5 block text-xs text-slate-400'>
                  {batch} · {value}
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
