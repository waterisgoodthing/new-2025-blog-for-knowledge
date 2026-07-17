'use client'

import { useEffect, useState } from 'react'

import {
  listMistakes,
  type Mistake,
  type MistakeReason,
  type MistakeStatus,
} from '@/lib/api/mistakes'

import { ManageEmptyState } from '../../../components/manage-empty-state'
import { ManageStatusBadge } from '../../../components/manage-status-badge'
import {
  ManageListRow,
  ManageTableContainer,
} from '../../../components/manage-table-container'

const statusFilters: Array<{ value: '' | MistakeStatus; label: string }> = [
  { value: '', label: '全部' },
  { value: 'active', label: '在用' },
  { value: 'archived', label: '已归档' },
]

const statusLabels: Record<MistakeStatus, string> = {
  active: '在用',
  archived: '已归档',
}

const statusTones: Record<MistakeStatus, 'neutral' | 'info' | 'success' | 'warning' | 'danger'> = {
  active: 'success',
  archived: 'neutral',
}

const reasonLabels: Record<MistakeReason, string> = {
  concept: '概念理解',
  calculation: '计算过程',
  reading: '审题阅读',
  careless: '粗心失误',
  unknown: '未分类',
}

function formatDate(iso: string): string {
  const date = new Date(iso)
  if (Number.isNaN(date.getTime())) return ''
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${date.getFullYear()}-${month}-${day}`
}

function message(reason: unknown, fallback: string) {
  return reason instanceof Error ? reason.message : fallback
}

/**
 * Formal mistake list — the manage workspace's "错题本".
 * Only shows confirmed mistakes; draft creation has moved to
 * the capture page, and draft review to the drafts review center.
 */
export function MistakeWorkspace() {
  const [mistakes, setMistakes] = useState<Mistake[]>([])
  const [status, setStatus] = useState<'' | MistakeStatus>('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    setLoading(true)
    listMistakes(status || undefined)
      .then(setMistakes)
      .catch((reason: unknown) => setError(message(reason, '加载错题失败')))
      .finally(() => setLoading(false))
  }, [status])

  return (
    <section>
      <ManageTableContainer
        count={loading ? undefined : mistakes.length}
        header={
          <>
            <h2 className='font-medium text-slate-800'>正式错题</h2>
            <select
              aria-label='错题状态'
              value={status}
              onChange={(event) => setStatus(event.target.value as '' | MistakeStatus)}
              className='rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm'
            >
              {statusFilters.map((item) => (
                <option key={item.value} value={item.value}>{item.label}</option>
              ))}
            </select>
          </>
        }
      >
        {loading ? (
          <ManageEmptyState variant='loading' message='正在加载错题…' />
        ) : null}
        {!loading && error ? (
          <ManageEmptyState variant='error' message={error} />
        ) : null}
        {!loading && !error && mistakes.length === 0 ? (
          <ManageEmptyState
            variant={status ? 'filtered-empty' : 'empty'}
            message='当前没有错题。'
          />
        ) : null}
        {mistakes.map((mistake) => {
          const date = formatDate(mistake.created_at)
          const reasonLabel = reasonLabels[mistake.reason_category] ?? mistake.reason_category
          return (
            <ManageListRow
              key={mistake.id}
              href={`/manage/mistakes/${mistake.id}?kind=mistake`}
              title={mistake.title || mistake.question_text}
              meta={`${reasonLabel} · v${mistake.version}${date ? ` · ${date}` : ''}`}
            >
              <ManageStatusBadge tone={statusTones[mistake.status]}>
                {statusLabels[mistake.status]}
              </ManageStatusBadge>
            </ManageListRow>
          )
        })}
      </ManageTableContainer>
    </section>
  )
}
