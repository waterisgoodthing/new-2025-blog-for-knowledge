'use client'

import Link from 'next/link'
import { FormEvent, useEffect, useState } from 'react'
import { Archive, ArrowLeft } from 'lucide-react'
import { useRouter } from 'next/navigation'

import { archiveQuestion, getQuestion, updateLegacyQuestion, type Difficulty, type Question, type QuestionType } from '@/lib/api/questions'
import { listSubjects, type Subject } from '@/lib/api/taxonomy'
import { KnowledgePointMultiSelect } from '../../../components/knowledge-point-select'
import { ManageFormPanel } from '../../../components/manage-form-panel'

export function QuestionEditor({ questionId }: { questionId: string }) {
  const router = useRouter()
  const [question, setQuestion] = useState<Question | null>(null)
  const [subjects, setSubjects] = useState<Subject[]>([])
  const [optionsText, setOptionsText] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    Promise.all([getQuestion(questionId), listSubjects({ status: 'active' })])
      .then(([nextQuestion, nextSubjects]) => {
        setQuestion(nextQuestion)
        setOptionsText(nextQuestion.options.map((option) => option.text).join('\n'))
        setSubjects(nextSubjects)
      })
      .catch((reason: unknown) => setError(reason instanceof Error ? reason.message : '加载失败'))
  }, [questionId])

  const save = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (!question) return
    const optionValues = optionsText.split('\n').map((value) => value.trim()).filter(Boolean)
    if ((question.question_type === 'single_choice' || question.question_type === 'multiple_choice') && optionValues.length < 2) {
      setError('选择题至少需要填写两个选项，每行一个。')
      return
    }
    setBusy(true)
    setError(null)
    try {
      setQuestion(await updateLegacyQuestion(question.id, {
        version: question.version,
        subject_id: question.subject_id,
        title: question.title,
        question_text: question.question_text,
        question_type: question.question_type,
        options: question.question_type === 'single_choice' || question.question_type === 'multiple_choice' ? optionValues : [],
        correct_answer: question.correct_answer,
        explanation: question.explanation,
        difficulty: question.difficulty === 'unspecified' ? null : question.difficulty,
        knowledge_point_ids: question.knowledge_point_ids,
      }))
    } catch (reason) { setError(reason instanceof Error ? reason.message : '保存失败') } finally { setBusy(false) }
  }

  if (!question) return <p className='text-sm text-slate-500'>{error || '正在加载题目…'}</p>
  const active = question.status === 'active'

  return (
    <div className='max-w-3xl space-y-7'>
      <Link href='/manage/questions' className='inline-flex items-center gap-2 text-sm text-slate-500'><ArrowLeft className='h-4 w-4' />返回题库</Link>
      <div>
        <p className='text-xs tracking-wider text-[var(--color-brand)] uppercase'>{question.status} · private · v{question.version}</p>
        <h1 className='mt-2 text-2xl font-semibold text-slate-900'>编辑正式题目</h1>
        <p className='mt-2 text-sm text-slate-500'>来源：{question.sources[0]?.source_name || '手工录入'}</p>
      </div>
      <ManageFormPanel
        onSubmit={save}
        error={error ?? undefined}
        actions={active ? (
          <>
            <button
              type='button'
              disabled={busy}
              onClick={async () => {
                if (!window.confirm('确认归档这道题？题目不会被物理删除。')) return
                setBusy(true)
                try { await archiveQuestion(question.id, question.version); router.push('/manage/questions') } catch (reason) { setError(reason instanceof Error ? reason.message : '归档失败'); setBusy(false) }
              }}
              className='mr-auto inline-flex items-center gap-2 rounded-lg border border-amber-200 px-4 py-2 text-sm text-amber-700'
            >
              <Archive className='h-4 w-4' />归档
            </button>
            <button disabled={busy || !question.question_text.trim()} className='rounded-lg bg-[var(--color-brand)] px-5 py-2 text-sm text-white disabled:opacity-45'>
              {busy ? '处理中…' : '保存'}
            </button>
          </>
        ) : undefined}
      >
        <div className='grid gap-4 sm:grid-cols-2'>
          <label className='text-sm text-slate-600'>科目
            <select disabled={!active} value={question.subject_id} onChange={(event) => setQuestion({ ...question, subject_id: Number(event.target.value), knowledge_point_ids: [] })} className='mt-2 w-full rounded-lg border border-slate-200 px-3 py-2.5'>
              {subjects.map((subject) => <option key={subject.id} value={subject.id}>{subject.name}</option>)}
            </select>
          </label>
          <label className='text-sm text-slate-600'>题型
            <select disabled={!active} value={question.question_type} onChange={(event) => setQuestion({ ...question, question_type: event.target.value as QuestionType })} className='mt-2 w-full rounded-lg border border-slate-200 px-3 py-2.5'>
              <option value='short_answer'>简答题</option><option value='single_choice'>单选题</option><option value='multiple_choice'>多选题</option><option value='true_false'>判断题</option><option value='essay'>论述题</option>
            </select>
          </label>
        </div>
        <label className='block text-sm text-slate-600'>标题（可选）
          <input disabled={!active} value={question.title ?? ''} onChange={(event) => setQuestion({ ...question, title: event.target.value || null })} className='mt-2 w-full rounded-lg border border-slate-200 px-3 py-2.5' />
        </label>
        <label className='block text-sm text-slate-600'>题干
          <textarea disabled={!active} value={question.question_text} onChange={(event) => setQuestion({ ...question, question_text: event.target.value })} rows={6} className='mt-2 w-full rounded-lg border border-slate-200 px-3 py-2.5' />
        </label>
        {question.question_type === 'single_choice' || question.question_type === 'multiple_choice' ? <label className='block text-sm text-slate-600'>选项（每行一项）<textarea disabled={!active} value={optionsText} onChange={(event) => setOptionsText(event.target.value)} rows={5} className='mt-2 w-full rounded-lg border border-slate-200 px-3 py-2.5' /></label> : null}
        <div className='grid gap-4 sm:grid-cols-2'>
          <label className='text-sm text-slate-600'>正确答案<textarea disabled={!active} value={question.correct_answer ?? ''} onChange={(event) => setQuestion({ ...question, correct_answer: event.target.value || null })} rows={3} className='mt-2 w-full rounded-lg border border-slate-200 px-3 py-2.5' /></label>
          <label className='text-sm text-slate-600'>解析<textarea disabled={!active} value={question.explanation ?? ''} onChange={(event) => setQuestion({ ...question, explanation: event.target.value || null })} rows={3} className='mt-2 w-full rounded-lg border border-slate-200 px-3 py-2.5' /></label>
        </div>
        <label className='block text-sm text-slate-600'>难度
          <select disabled={!active} value={question.difficulty} onChange={(event) => setQuestion({ ...question, difficulty: event.target.value as Difficulty })} className='mt-2 w-full rounded-lg border border-slate-200 px-3 py-2.5'>
            <option value='unspecified'>未设置</option><option value='easy'>简单</option><option value='medium'>中等</option><option value='hard'>困难</option>
          </select>
        </label>
        <KnowledgePointMultiSelect disabled={!active} subjectId={question.subject_id} values={question.knowledge_point_ids} onChange={(values) => setQuestion({ ...question, knowledge_point_ids: values })} />
      </ManageFormPanel>
    </div>
  )
}
