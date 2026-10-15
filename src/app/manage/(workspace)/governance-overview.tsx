'use client'

import useSWR from 'swr'
import { getGovernanceSummary, type GovernanceSection } from '@/lib/api/governance'
import { ManageEmptyState } from '../components/manage-empty-state'
import { ManagePageHeader } from '../components/manage-page-header'
import { ManageStatusBadge } from '../components/manage-status-badge'

const labels = { ai: 'AI 治理', tasks: '任务队列', statistics: '学习统计', report: '审计报告', settings: '设置治理' } as const
const tones = { ready: 'success', empty: 'neutral', unavailable: 'warning' } as const
const statusLabels = { ready: '有真实数据', empty: '明确空态', unavailable: '未提供' } as const

function SectionCard({ name, section }: { name: keyof typeof labels; section: GovernanceSection }) {
  return (
    <article className='rounded-xl border border-slate-200/70 bg-white/55 p-4'>
      <div className='flex items-center justify-between gap-3'>
        <h2 className='font-medium text-slate-800'>{labels[name]}</h2>
        <ManageStatusBadge tone={tones[section.status]}>{statusLabels[section.status]}</ManageStatusBadge>
      </div>
      <p className='mt-3 text-2xl font-semibold text-slate-800'>{section.count ?? '—'}</p>
      <p className='mt-2 text-xs text-slate-500'>来源：{section.source}</p>
      {section.detail ? <p className='mt-1 text-xs text-slate-400'>{section.detail}</p> : null}
    </article>
  )
}

export function GovernanceOverview() {
  const state = useSWR('manage-governance-summary', getGovernanceSummary, { revalidateOnFocus: false })
  return (
    <div className='space-y-8'>
      <ManagePageHeader eyebrow='治理' title='系统治理总览' description='指标只来自已持久化的管理数据；未建模能力保持明确未提供。' />
      {state.isLoading ? <ManageEmptyState variant='loading' message='正在加载治理数据…' /> : null}
      {state.error ? <ManageEmptyState variant='error' message='治理数据加载失败，请稍后重试。' /> : null}
      {state.data ? (
        <>
          <GovernanceContent data={state.data} />
        </>
      ) : null}
    </div>
  )
}

function GovernanceContent({ data }: { data: Awaited<ReturnType<typeof getGovernanceSummary>> }) {
  return (
    <>
          <p className='text-xs text-slate-400'>生成时间：{new Date(data.generated_at).toLocaleString('zh-CN', { hour12: false })}</p>
          <div className='grid gap-4 sm:grid-cols-2 xl:grid-cols-5'>
            {(Object.keys(labels) as Array<keyof typeof labels>).map((key) => <SectionCard key={key} name={key} section={data[key]} />)}
          </div>
    </>
  )
}
