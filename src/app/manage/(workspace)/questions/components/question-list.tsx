'use client'

import { useCallback, useEffect, useState } from 'react'
import Link from 'next/link'

import { listQuestions, type Question, type QuestionStatus } from '@/lib/api/questions'
import { questionTypeLabel } from '@/lib/manage-display'

import { FeatureState } from '../../../components/feature-state'
import { ManageStatusBadge } from '../../../components/manage-status-badge'
import {
  ManageListRow,
  ManageTableContainer,
} from '../../../components/manage-table-container'

export function QuestionList() {
  const [questions, setQuestions] = useState<Question[]>([])
  const [status, setStatus] = useState<QuestionStatus>('active')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const load = useCallback(() => {
    setLoading(true)
    setError(null)
    listQuestions({ status })
      .then(setQuestions)
      .catch((reason: unknown) => setError(reason instanceof Error ? reason.message : '加载失败'))
      .finally(() => setLoading(false))
  }, [status])

  useEffect(() => {
    load()
  }, [load])

  return (
    <section>
      <ManageTableContainer
        header={
          <>
            <h2 className='font-medium text-slate-800'>题目列表</h2>
            <div className='flex items-center gap-3'>
              <Link href='/manage/questions/new' className='rounded-lg bg-[var(--color-brand)] px-3 py-2 text-sm text-white'>新建题目</Link>
              <span className='text-xs text-slate-400'>{questions.length} 道</span>
              <select
                aria-label='题目状态'
                value={status}
                onChange={(event) => setStatus(event.target.value as QuestionStatus)}
                className='rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm'
              >
                <option value='active'>使用中</option>
                <option value='archived'>已归档</option>
              </select>
            </div>
          </>
        }
      >
        {loading ? (
          <FeatureState state={{ kind: 'loading', label: '正在加载题库', rows: 4 }} />
        ) : null}
        {!loading && error ? (
          <FeatureState state={{ kind: 'error', title: '题库加载失败', description: error, retry: load }} />
        ) : null}
        {!loading && !error && questions.length === 0 ? (
          <FeatureState state={{ kind: 'empty', title: '暂无正式题目', description: '请先确认一份题目草稿，或直接新建题目。' }} />
        ) : null}
        {questions.map((question) => (
          <ManageListRow
            key={question.id}
            href={`/manage/questions/${question.id}`}
            title={question.title || question.question_text}
            meta={`${questionTypeLabel(question.question_type)} · v${question.version}`}
          >
            <ManageStatusBadge tone={question.status === 'active' ? 'success' : 'neutral'}>
              {question.status === 'active' ? '使用中' : '已归档'}
            </ManageStatusBadge>
          </ManageListRow>
        ))}
      </ManageTableContainer>
    </section>
  )
}
