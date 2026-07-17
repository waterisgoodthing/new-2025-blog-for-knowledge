'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'

import { listQuestions, type Question, type QuestionStatus } from '@/lib/api/questions'

import { ManageEmptyState } from '../../../components/manage-empty-state'
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

  useEffect(() => {
    setLoading(true)
    listQuestions({ status })
      .then(setQuestions)
      .catch((reason: unknown) => setError(reason instanceof Error ? reason.message : '加载失败'))
      .finally(() => setLoading(false))
  }, [status])

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
          <ManageEmptyState variant='loading' message='正在加载题库…' />
        ) : null}
        {!loading && error ? (
          <ManageEmptyState variant='error' message={error} />
        ) : null}
        {!loading && !error && questions.length === 0 ? (
          <ManageEmptyState
            variant={status === 'active' ? 'filtered-empty' : 'empty'}
            message='当前没有正式题目；请先确认一份草稿。'
          />
        ) : null}
        {questions.map((question) => (
          <ManageListRow
            key={question.id}
            href={`/manage/questions/${question.id}`}
            title={question.title || question.question_text}
            meta={`${question.question_type} · v${question.version}`}
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
