'use client'

import Link from 'next/link'
import { useEffect, useState } from 'react'
import { ArrowRight } from 'lucide-react'

import { listQuestions, type Question, type QuestionStatus } from '@/lib/api/questions'

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
      <div className='flex items-center justify-between gap-4 border-b border-slate-200/70 pb-3'>
        <h2 className='font-medium text-slate-800'>题目列表</h2>
        <select aria-label='题目状态' value={status} onChange={(event) => setStatus(event.target.value as QuestionStatus)} className='rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm'>
          <option value='active'>使用中</option><option value='archived'>已归档</option>
        </select>
      </div>
      {loading ? <p className='py-7 text-sm text-slate-400'>正在加载题库…</p> : null}
      {error ? <p role='alert' className='py-5 text-sm text-red-600'>{error}</p> : null}
      {!loading && questions.length === 0 ? <p className='py-7 text-sm text-slate-500'>当前没有正式题目；请先确认一份草稿。</p> : null}
      {questions.map((question) => (
        <Link key={question.id} href={`/manage/questions/${question.id}`} className='group flex items-center gap-4 border-b border-slate-200/55 py-4'>
          <span className='min-w-0 flex-1'>
            <span className='block truncate font-medium text-slate-800'>{question.title || question.question_text}</span>
            <span className='mt-1 block text-xs text-slate-400'>{question.question_type} · {question.status} · v{question.version}</span>
          </span>
          <ArrowRight className='h-4 w-4 text-slate-300 group-hover:text-[var(--color-brand)]' />
        </Link>
      ))}
    </section>
  )
}
