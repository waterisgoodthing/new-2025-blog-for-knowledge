'use client'

import Link from 'next/link'
import { FormEvent, useEffect, useState } from 'react'
import { ArrowRight, Plus } from 'lucide-react'
import { useRouter } from 'next/navigation'

import {
  createQuestionDraft,
  listDrafts,
  type DraftStatus,
  type QuestionDraft,
} from '@/lib/api/drafts'
import type { QuestionType } from '@/lib/api/questions'
import { listSubjects, type Subject } from '@/lib/api/taxonomy'

const statuses: Array<{ value: '' | DraftStatus; label: string }> = [
  { value: '', label: '全部状态' },
  { value: 'pending', label: '待审核' },
  { value: 'needs_fix', label: '需修正' },
  { value: 'rejected', label: '已拒绝' },
  { value: 'converted', label: '已入库' },
]

export function DraftWorkspace() {
  const router = useRouter()
  const [drafts, setDrafts] = useState<QuestionDraft[]>([])
  const [subjects, setSubjects] = useState<Subject[]>([])
  const [status, setStatus] = useState<'' | DraftStatus>('')
  const [subjectId, setSubjectId] = useState('')
  const [questionText, setQuestionText] = useState('')
  const [questionType, setQuestionType] = useState<QuestionType>('short_answer')
  const [optionsText, setOptionsText] = useState('')
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    setLoading(true)
    Promise.all([listDrafts(status || undefined), listSubjects({ is_active: true })])
      .then(([nextDrafts, nextSubjects]) => {
        setDrafts(nextDrafts)
        setSubjects(nextSubjects)
        if (!subjectId && nextSubjects[0]) setSubjectId(String(nextSubjects[0].id))
      })
      .catch((reason: unknown) => setError(reason instanceof Error ? reason.message : '加载失败'))
      .finally(() => setLoading(false))
  }, [status, subjectId])

  const submit = async (event: FormEvent) => {
    event.preventDefault()
    if (!subjectId || !questionText.trim()) return
    const optionValues = optionsText.split('\n').map((value) => value.trim()).filter(Boolean)
    if ((questionType === 'single_choice' || questionType === 'multiple_choice') && optionValues.length < 2) {
      setError('选择题至少需要填写两个选项，每行一个。')
      return
    }
    setSaving(true)
    setError(null)
    try {
      const created = await createQuestionDraft({
        subject_id: Number(subjectId),
        question_text: questionText,
        question_type: questionType,
        options:
          questionType === 'single_choice' || questionType === 'multiple_choice'
            ? optionValues
            : [],
      })
      router.push(`/manage/drafts/${created.item.id}`)
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : '创建失败')
      setSaving(false)
    }
  }

  return (
    <div className='grid gap-8 lg:grid-cols-[minmax(0,1fr)_22rem]'>
      <section>
        <div className='flex flex-wrap items-center justify-between gap-3 border-b border-slate-200/70 pb-3'>
          <h2 className='font-medium text-slate-800'>审核队列</h2>
          <select
            aria-label='草稿状态'
            value={status}
            onChange={(event) => setStatus(event.target.value as '' | DraftStatus)}
            className='rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm'
          >
            {statuses.map((item) => <option key={item.value} value={item.value}>{item.label}</option>)}
          </select>
        </div>
        {loading ? <p className='py-7 text-sm text-slate-400'>正在加载草稿…</p> : null}
        {!loading && drafts.length === 0 ? <p className='py-7 text-sm text-slate-500'>当前没有草稿。</p> : null}
        {drafts.map((draft) => (
          <Link
            key={draft.item.id}
            href={`/manage/drafts/${draft.item.id}`}
            className='group flex items-center gap-4 border-b border-slate-200/55 py-4'
          >
            <span className='min-w-0 flex-1'>
              <span className='block truncate font-medium text-slate-800'>{draft.title || draft.question_text}</span>
              <span className='mt-1 block text-xs text-slate-400'>
                {draft.item.status} · {draft.question_type} · v{draft.item.version}
              </span>
            </span>
            <ArrowRight className='h-4 w-4 text-slate-300 group-hover:text-[var(--color-brand)]' />
          </Link>
        ))}
      </section>

      <form onSubmit={submit} className='h-fit space-y-4 rounded-2xl border border-slate-200/70 bg-white/55 p-5'>
        <h2 className='font-medium text-slate-800'>手工创建题目草稿</h2>
        {!loading && subjects.length === 0 ? (
          <p role='status' className='rounded-xl bg-amber-50 px-3 py-2 text-sm leading-6 text-amber-700'>
            还没有可用科目。请先到“科目”页面创建并启用科目，再创建题目草稿。
          </p>
        ) : null}
        <label className='block text-sm text-slate-600'>科目
          <select value={subjectId} onChange={(event) => setSubjectId(event.target.value)} className='mt-2 w-full rounded-xl border border-slate-200 px-3 py-2.5'>
            {subjects.map((subject) => <option key={subject.id} value={subject.id}>{subject.name}</option>)}
          </select>
        </label>
        <label className='block text-sm text-slate-600'>题型
          <select value={questionType} onChange={(event) => setQuestionType(event.target.value as QuestionType)} className='mt-2 w-full rounded-xl border border-slate-200 px-3 py-2.5'>
            <option value='short_answer'>简答题</option>
            <option value='single_choice'>单选题</option>
            <option value='multiple_choice'>多选题</option>
            <option value='true_false'>判断题</option>
            <option value='essay'>论述题</option>
          </select>
        </label>
        <label className='block text-sm text-slate-600'>题干
          <textarea value={questionText} onChange={(event) => setQuestionText(event.target.value)} rows={5} className='mt-2 w-full rounded-xl border border-slate-200 px-3 py-2.5' />
        </label>
        {questionType === 'single_choice' || questionType === 'multiple_choice' ? (
          <label className='block text-sm text-slate-600'>选项（每行一项）
            <textarea value={optionsText} onChange={(event) => setOptionsText(event.target.value)} rows={4} className='mt-2 w-full rounded-xl border border-slate-200 px-3 py-2.5' />
          </label>
        ) : null}
        <button disabled={saving || !subjectId || !questionText.trim()} className='inline-flex w-full items-center justify-center gap-2 rounded-xl bg-[var(--color-brand)] px-4 py-2.5 text-sm text-white disabled:opacity-45'>
          <Plus className='h-4 w-4' />{saving ? '正在创建…' : '创建草稿'}
        </button>
        {error ? <p role='alert' className='text-sm text-red-600'>{error}</p> : null}
      </form>
    </div>
  )
}
