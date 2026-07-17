'use client'

import { useCallback, useEffect, useState } from 'react'

import {
  listDrafts,
  type DraftStatus,
  type QuestionDraft,
} from '@/lib/api/drafts'
import {
  listMistakeDrafts,
  type MistakeDraft,
  type MistakeDraftStatus,
  type MistakeReason,
} from '@/lib/api/mistakes'
import type { QuestionType } from '@/lib/api/questions'

import { ManageEmptyState } from '../../../components/manage-empty-state'
import { ManageStatusBadge } from '../../../components/manage-status-badge'
import {
  ManageListRow,
  ManageTableContainer,
} from '../../../components/manage-table-container'

type DraftKind = 'question' | 'mistake'
type ReviewStatus = DraftStatus | MistakeDraftStatus

interface UnifiedDraft {
  kind: DraftKind
  key: string
  href: string
  title: string
  meta: string
  status: ReviewStatus
  createdAt: string
}

const kindFilters: Array<{ value: '' | DraftKind; label: string }> = [
  { value: '', label: '全部' },
  { value: 'question', label: '题目' },
  { value: 'mistake', label: '错题' },
]

const kindLabels: Record<DraftKind, string> = {
  question: '题目',
  mistake: '错题',
}

const kindTones: Record<DraftKind, 'neutral' | 'info' | 'success' | 'warning' | 'danger'> = {
  question: 'info',
  mistake: 'warning',
}

const statusLabels: Record<ReviewStatus, string> = {
  pending: '待确认',
  needs_fix: '需修正',
  rejected: '已拒绝',
  converted: '已入库',
}

const statusTones: Record<ReviewStatus, 'neutral' | 'info' | 'success' | 'warning' | 'danger'> = {
  pending: 'warning',
  needs_fix: 'info',
  rejected: 'danger',
  converted: 'success',
}

const questionTypeLabels: Record<QuestionType, string> = {
  short_answer: '简答题',
  single_choice: '单选题',
  multiple_choice: '多选题',
  true_false: '判断题',
  essay: '论述题',
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

function fromQuestionDraft(draft: QuestionDraft): UnifiedDraft {
  const date = formatDate(draft.created_at)
  const typeLabel = questionTypeLabels[draft.question_type] ?? draft.question_type
  return {
    kind: 'question',
    key: `q-${draft.item.id}`,
    href: `/manage/drafts/${draft.item.id}`,
    title: draft.title || draft.question_text,
    meta: `${typeLabel} · v${draft.item.version}${date ? ` · ${date}` : ''}`,
    status: draft.item.status,
    createdAt: draft.created_at,
  }
}

function fromMistakeDraft(draft: MistakeDraft): UnifiedDraft {
  const date = formatDate(draft.created_at)
  const reasonLabel = reasonLabels[draft.reason_category] ?? draft.reason_category
  return {
    kind: 'mistake',
    key: `m-${draft.draft_item_id}`,
    href: `/manage/mistakes/${draft.draft_item_id}?kind=draft`,
    title: draft.title || draft.question_text,
    meta: `${reasonLabel} · v${draft.version}${date ? ` · ${date}` : ''}`,
    status: draft.status,
    createdAt: draft.created_at,
  }
}

export function DraftWorkspace() {
  const [unified, setUnified] = useState<UnifiedDraft[]>([])
  const [kind, setKind] = useState<'' | DraftKind>('')
  const [loading, setLoading] = useState(true)
  const [questionError, setQuestionError] = useState<string | null>(null)
  const [mistakeError, setMistakeError] = useState<string | null>(null)

  const load = useCallback(() => {
    setLoading(true)
    setQuestionError(null)
    setMistakeError(null)
    Promise.allSettled([listDrafts(), listMistakeDrafts()])
      .then(([questionResult, mistakeResult]) => {
        const items: UnifiedDraft[] = []
        if (questionResult.status === 'fulfilled') {
          items.push(...questionResult.value.map(fromQuestionDraft))
        } else {
          setQuestionError(
            questionResult.reason instanceof Error
              ? questionResult.reason.message
              : '题目草稿加载失败',
          )
        }
        if (mistakeResult.status === 'fulfilled') {
          items.push(...mistakeResult.value.map(fromMistakeDraft))
        } else {
          setMistakeError(
            mistakeResult.reason instanceof Error
              ? mistakeResult.reason.message
              : '错题草稿加载失败',
          )
        }
        items.sort((a, b) => {
          if (!a.createdAt && !b.createdAt) return 0
          if (!a.createdAt) return 1
          if (!b.createdAt) return -1
          return b.createdAt.localeCompare(a.createdAt)
        })
        setUnified(items)
      })
      .finally(() => setLoading(false))
  }, [])

  useEffect(() => {
    load()
  }, [load])

  const filtered = kind ? unified.filter((item) => item.kind === kind) : unified
  const hasAnyError = Boolean(questionError || mistakeError)
  const filteredError =
    kind === 'question' ? questionError : kind === 'mistake' ? mistakeError : null

  // When kind === '' and any source failed with no items to show,
  // display a combined error instead of an empty state
  const combinedError =
    filteredError ??
    (kind === '' && hasAnyError && filtered.length === 0
      ? [questionError, mistakeError].filter(Boolean).join('；')
      : null)

  const showErrorState = !loading && filtered.length === 0 && Boolean(combinedError)
  const showListEmpty = !loading && filtered.length === 0 && !combinedError

  // Partial error: some items loaded but a source failed
  const otherError =
    kind === 'question'
      ? mistakeError
      : kind === 'mistake'
        ? questionError
        : null

  return (
    <section>
      <ManageTableContainer
        count={loading ? undefined : filtered.length}
        header={
          <>
            <h2 className='font-medium text-slate-800'>审核队列</h2>
            <select
              aria-label='草稿类型'
              value={kind}
              onChange={(event) => setKind(event.target.value as '' | DraftKind)}
              className='rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm'
            >
              {kindFilters.map((item) => (
                <option key={item.value} value={item.value}>{item.label}</option>
              ))}
            </select>
          </>
        }
      >
        {loading ? (
          <ManageEmptyState variant='loading' message='正在加载草稿…' />
        ) : null}
        {showErrorState ? (
          <div className='space-y-3'>
            <ManageEmptyState variant='error' message={combinedError ?? '加载失败'} />
            <div className='flex justify-center'>
              <button
                type='button'
                onClick={load}
                className='rounded-lg border border-slate-200 px-4 py-2 text-sm text-slate-600 hover:bg-white'
              >
                重试
              </button>
            </div>
          </div>
        ) : null}
        {showListEmpty ? (
          <ManageEmptyState
            variant={kind ? 'filtered-empty' : 'empty'}
            message='当前没有草稿。'
          />
        ) : null}
        {filtered.map((draft) => (
          <ManageListRow
            key={draft.key}
            href={draft.href}
            title={draft.title}
            meta={draft.meta}
          >
            <div className='flex items-center gap-2'>
              <ManageStatusBadge tone={kindTones[draft.kind]}>
                {kindLabels[draft.kind]}
              </ManageStatusBadge>
              <ManageStatusBadge tone={statusTones[draft.status]}>
                {statusLabels[draft.status]}
              </ManageStatusBadge>
            </div>
          </ManageListRow>
        ))}
      </ManageTableContainer>
      {!loading && hasAnyError && filtered.length > 0 && otherError ? (
        <p role='alert' className='mt-4 rounded-lg bg-red-50 px-3 py-2 text-sm leading-6 text-red-600'>
          {otherError}
        </p>
      ) : null}
      {!loading && hasAnyError && filtered.length > 0 && !otherError && kind === '' ? (
        <p role='alert' className='mt-4 rounded-lg bg-red-50 px-3 py-2 text-sm leading-6 text-red-600'>
          {questionError ?? mistakeError}
        </p>
      ) : null}
    </section>
  )
}
