'use client'

import Link from 'next/link'
import { FormEvent, useEffect, useState } from 'react'
import { ArrowLeft, CheckCircle2, XCircle } from 'lucide-react'
import { useRouter } from 'next/navigation'

import {
  convertQuestionDraft,
  getQuestionDraft,
  rejectQuestionDraft,
  updateQuestionDraft,
  type QuestionDraft,
} from '@/lib/api/drafts'
import type { Difficulty, QuestionType } from '@/lib/api/questions'
import { listSubjects, type Subject } from '@/lib/api/taxonomy'
import { ManageFormPanel } from '../../../components/manage-form-panel'
import { KnowledgePointMultiSelect } from '../../../components/knowledge-point-select'

export function DraftEditor({ draftId }: { draftId: string }) {
  const router = useRouter()
  const [draft, setDraft] = useState<QuestionDraft | null>(null)
  const [subjects, setSubjects] = useState<Subject[]>([])
  const [optionsText, setOptionsText] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    Promise.all([getQuestionDraft(draftId), listSubjects({ status: 'active' })])
      .then(([nextDraft, nextSubjects]) => {
        setDraft(nextDraft)
        setOptionsText(nextDraft.options.join('\n'))
        setSubjects(nextSubjects)
      })
      .catch((reason: unknown) => setError(reason instanceof Error ? reason.message : '加载失败'))
  }, [draftId])

  const save = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (!draft) return
    const optionValues = optionsText.split('\n').map((value) => value.trim()).filter(Boolean)
    if ((draft.question_type === 'single_choice' || draft.question_type === 'multiple_choice') && optionValues.length < 2) {
      setError('选择题至少需要填写两个选项，每行一个。')
      return
    }
    setBusy(true)
    setError(null)
    try {
      const updated = await updateQuestionDraft(draft.item.id, {
        version: draft.item.version,
        subject_id: draft.subject_id,
        title: draft.title,
        question_text: draft.question_text,
        question_type: draft.question_type,
        options:
          draft.question_type === 'single_choice' || draft.question_type === 'multiple_choice'
            ? optionValues
            : [],
        correct_answer: draft.correct_answer,
        explanation: draft.explanation,
        difficulty: draft.difficulty,
        knowledge_point_ids: draft.knowledge_point_ids,
      })
      setDraft(updated)
      setOptionsText(updated.options.join('\n'))
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : '保存失败')
    } finally {
      setBusy(false)
    }
  }

  if (!draft) return <p className='text-sm text-slate-500'>{error || '正在加载草稿…'}</p>
  const editable = draft.item.status === 'pending' || draft.item.status === 'needs_fix'

  return (
    <div className='max-w-3xl space-y-7'>
      <Link href='/manage/drafts' className='inline-flex items-center gap-2 text-sm text-slate-500'><ArrowLeft className='h-4 w-4' />返回草稿</Link>
      <div>
        <p className='text-xs tracking-wider text-[var(--color-brand)]'>{draft.item.status === 'pending' ? '待确认' : draft.item.status === 'needs_fix' ? '需修正' : draft.item.status === 'rejected' ? '已拒绝' : '已入库'} · 版本 {draft.item.version}</p>
        <h1 className='mt-2 text-2xl font-semibold text-slate-900'>审核题目草稿</h1>
      </div>
      {draft.item.status === 'converted' && draft.item.target_id ? (
        <Link href={`/manage/questions/${draft.item.target_id}`} className='inline-flex rounded-lg bg-emerald-50 px-4 py-3 text-sm text-emerald-700'>已进入题库，查看正式题目 →</Link>
      ) : null}
      <ManageFormPanel
        onSubmit={save}
        error={error ?? undefined}
        actions={editable ? (
          <>
            <button
              type='button'
              disabled={busy}
              onClick={async () => {
                if (!window.confirm('确认拒绝这份草稿？拒绝后不可继续编辑或转换。')) return
                setBusy(true)
                try { setDraft(await rejectQuestionDraft(draft.item.id, draft.item.version)) } catch (reason) { setError(reason instanceof Error ? reason.message : '拒绝失败') } finally { setBusy(false) }
              }}
              className='mr-auto inline-flex items-center gap-2 rounded-lg border border-red-200 px-4 py-2 text-sm text-red-600'
            >
              <XCircle className='h-4 w-4' />拒绝
            </button>
            <div className='flex gap-3'>
              <button disabled={busy || !draft.question_text.trim()} className='rounded-lg border border-slate-200 px-4 py-2 text-sm'>保存修改</button>
              <button
                type='button'
                disabled={busy}
                onClick={async () => {
                  const optionValues = optionsText.split('\n').map((value) => value.trim()).filter(Boolean)
                  if ((draft.question_type === 'single_choice' || draft.question_type === 'multiple_choice') && optionValues.length < 2) {
                    setError('选择题至少需要填写两个选项，每行一个。')
                    return
                  }
                  if (!window.confirm('确认当前内容并转入正式题库？')) return
                  setBusy(true)
                  try {
                    const question = await convertQuestionDraft(draft.item.id, draft.item.version)
                    router.push(`/manage/questions/${question.id}`)
                  } catch (reason) { setError(reason instanceof Error ? reason.message : '转换失败'); setBusy(false) }
                }}
                className='inline-flex items-center gap-2 rounded-lg bg-[var(--color-brand)] px-4 py-2 text-sm text-white'
              >
                <CheckCircle2 className='h-4 w-4' />确认入库
              </button>
            </div>
          </>
        ) : undefined}
      >
        <div className='grid gap-4 sm:grid-cols-2'>
          <label className='text-sm text-slate-600'>科目
            <select disabled={!editable} value={draft.subject_id} onChange={(event) => setDraft({ ...draft, subject_id: Number(event.target.value), knowledge_point_ids: [] })} className='mt-2 w-full rounded-lg border border-slate-200 px-3 py-2.5'>
              {subjects.map((subject) => <option key={subject.id} value={subject.id}>{subject.name}</option>)}
            </select>
          </label>
          <label className='text-sm text-slate-600'>题型
            <select disabled={!editable} value={draft.question_type} onChange={(event) => setDraft({ ...draft, question_type: event.target.value as QuestionType })} className='mt-2 w-full rounded-lg border border-slate-200 px-3 py-2.5'>
              <option value='short_answer'>简答题</option><option value='single_choice'>单选题</option><option value='multiple_choice'>多选题</option><option value='true_false'>判断题</option><option value='essay'>论述题</option>
            </select>
          </label>
        </div>
        <label className='block text-sm text-slate-600'>标题（可选）
          <input disabled={!editable} value={draft.title ?? ''} onChange={(event) => setDraft({ ...draft, title: event.target.value || null })} className='mt-2 w-full rounded-lg border border-slate-200 px-3 py-2.5' />
        </label>
        <label className='block text-sm text-slate-600'>题干
          <textarea disabled={!editable} value={draft.question_text} onChange={(event) => setDraft({ ...draft, question_text: event.target.value })} rows={6} className='mt-2 w-full rounded-lg border border-slate-200 px-3 py-2.5' />
        </label>
        {draft.question_type === 'single_choice' || draft.question_type === 'multiple_choice' ? (
          <label className='block text-sm text-slate-600'>选项（每行一项）
            <textarea disabled={!editable} value={optionsText} onChange={(event) => setOptionsText(event.target.value)} rows={5} className='mt-2 w-full rounded-lg border border-slate-200 px-3 py-2.5' />
          </label>
        ) : null}
        <div className='grid gap-4 sm:grid-cols-2'>
          <label className='text-sm text-slate-600'>正确答案
            <textarea disabled={!editable} value={draft.correct_answer ?? ''} onChange={(event) => setDraft({ ...draft, correct_answer: event.target.value || null })} rows={3} className='mt-2 w-full rounded-lg border border-slate-200 px-3 py-2.5' />
          </label>
          <label className='text-sm text-slate-600'>解析
            <textarea disabled={!editable} value={draft.explanation ?? ''} onChange={(event) => setDraft({ ...draft, explanation: event.target.value || null })} rows={3} className='mt-2 w-full rounded-lg border border-slate-200 px-3 py-2.5' />
          </label>
        </div>
        <label className='block text-sm text-slate-600'>难度
          <select disabled={!editable} value={draft.difficulty ?? ''} onChange={(event) => setDraft({ ...draft, difficulty: (event.target.value || null) as Difficulty | null })} className='mt-2 w-full rounded-lg border border-slate-200 px-3 py-2.5'>
            <option value=''>未设置</option><option value='easy'>简单</option><option value='medium'>中等</option><option value='hard'>困难</option>
          </select>
        </label>
        <KnowledgePointMultiSelect disabled={!editable} subjectId={draft.subject_id} values={draft.knowledge_point_ids} onChange={(values) => setDraft({ ...draft, knowledge_point_ids: values })} />
      </ManageFormPanel>
    </div>
  )
}
