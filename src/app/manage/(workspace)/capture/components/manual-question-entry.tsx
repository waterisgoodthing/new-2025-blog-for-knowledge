'use client'

import { FormEvent, useEffect, useState } from 'react'
import { Plus } from 'lucide-react'
import { useRouter } from 'next/navigation'

import {
  createQuestionDraft,
} from '@/lib/api/drafts'
import type { QuestionType } from '@/lib/api/questions'
import { listSubjects, type Subject } from '@/lib/api/taxonomy'

import { ManageFormPanel } from '../../../components/manage-form-panel'

/**
 * Manual question entry form — one of the capture methods.
 * Creates a question draft via the same API and fields as the
 * former draft-workspace create form. On success, navigates to
 * the draft detail page (unchanged submission contract).
 */
export function ManualQuestionEntry() {
  const router = useRouter()
  const [subjects, setSubjects] = useState<Subject[]>([])
  const [subjectId, setSubjectId] = useState('')
  const [questionText, setQuestionText] = useState('')
  const [questionType, setQuestionType] = useState<QuestionType>('short_answer')
  const [optionsText, setOptionsText] = useState('')
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    listSubjects({ status: 'active' })
      .then((nextSubjects) => {
        setSubjects(nextSubjects)
        if (nextSubjects[0]) setSubjectId(String(nextSubjects[0].id))
      })
      .catch((reason: unknown) => setError(reason instanceof Error ? reason.message : '加载科目失败'))
      .finally(() => setLoading(false))
  }, [])

  const submit = async (event: FormEvent<HTMLFormElement>) => {
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
    <ManageFormPanel
      title='手工录入题目'
      description='直接填写题目内容，创建为题目草稿后进入待确认。'
      error={error ?? undefined}
      onSubmit={submit}
    >
      {!loading && subjects.length === 0 ? (
        <p role='status' className='rounded-lg bg-amber-50 px-3 py-2 text-sm leading-6 text-amber-700'>
          还没有可用科目。请先到&ldquo;学科角&rdquo;创建并启用科目，再录入题目。
        </p>
      ) : null}
      <label className='block text-sm text-slate-600'>科目
        <select value={subjectId} onChange={(event) => setSubjectId(event.target.value)} className='mt-2 w-full rounded-lg border border-slate-200 px-3 py-2.5'>
          {subjects.map((subject) => <option key={subject.id} value={subject.id}>{subject.name}</option>)}
        </select>
      </label>
      <label className='block text-sm text-slate-600'>题型
        <select value={questionType} onChange={(event) => setQuestionType(event.target.value as QuestionType)} className='mt-2 w-full rounded-lg border border-slate-200 px-3 py-2.5'>
          <option value='short_answer'>简答题</option>
          <option value='single_choice'>单选题</option>
          <option value='multiple_choice'>多选题</option>
          <option value='true_false'>判断题</option>
          <option value='essay'>论述题</option>
        </select>
      </label>
      <label className='block text-sm text-slate-600'>题干
        <textarea value={questionText} onChange={(event) => setQuestionText(event.target.value)} rows={5} className='mt-2 w-full rounded-lg border border-slate-200 px-3 py-2.5' />
      </label>
      {questionType === 'single_choice' || questionType === 'multiple_choice' ? (
        <label className='block text-sm text-slate-600'>选项（每行一项）
          <textarea value={optionsText} onChange={(event) => setOptionsText(event.target.value)} rows={4} className='mt-2 w-full rounded-lg border border-slate-200 px-3 py-2.5' />
        </label>
      ) : null}
      <button disabled={saving || !subjectId || !questionText.trim()} className='inline-flex w-full items-center justify-center gap-2 rounded-lg bg-[var(--color-brand)] px-4 py-2.5 text-sm text-white disabled:opacity-45'>
        <Plus className='h-4 w-4' />{saving ? '正在创建…' : '创建草稿'}
      </button>
    </ManageFormPanel>
  )
}
