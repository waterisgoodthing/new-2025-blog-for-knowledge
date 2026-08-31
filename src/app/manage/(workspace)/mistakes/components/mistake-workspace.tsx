'use client'

import { useCallback, useEffect, useState } from 'react'

import {
  listMistakes,
  type Mistake,
  type MistakeReason,
  type MistakeStatus,
} from '@/lib/api/mistakes'
import { formatChineseDate } from '@/lib/manage-display'

import { FeatureState } from '../../../components/feature-state'
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

  const load = useCallback(() => {
    setLoading(true)
    setError(null)
    listMistakes(status || undefined)
      .then(setMistakes)
      .catch((reason: unknown) => setError(message(reason, '加载错题失败')))
      .finally(() => setLoading(false))
  }, [status])

  useEffect(() => {
    load()
  }, [load])

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
          <FeatureState state={{ kind: 'loading', label: '正在加载错题', rows: 4 }} />
        ) : null}
        {!loading && error ? (
          <FeatureState state={{ kind: 'error', title: '错题加载失败', description: error, retry: load }} />
        ) : null}
        {!loading && !error && mistakes.length === 0 ? (
          <FeatureState state={{ kind: 'empty', title: status ? '没有符合条件的错题' : '暂无错题', description: '从题库记录错误后，正式错题会显示在这里。' }} />
        ) : null}
        {mistakes.map((mistake) => {
          const date = formatChineseDate(mistake.created_at)
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
