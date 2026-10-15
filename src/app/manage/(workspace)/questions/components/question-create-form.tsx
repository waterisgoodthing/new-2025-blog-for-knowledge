'use client'

import { FormEvent, useEffect, useState } from 'react'
import { ArrowLeft } from 'lucide-react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'

import {
  createQuestion,
  type Difficulty,
  type QuestionType,
} from '@/lib/api/questions'
import { listSubjects, type Subject } from '@/lib/api/taxonomy'
import { KnowledgePointMultiSelect } from '../../../components/knowledge-point-select'
import { ManageFormPanel } from '../../../components/manage-form-panel'

const choiceTypes = new Set<QuestionType>(['single_choice', 'multiple_choice'])

export function QuestionCreateForm() {
  const router = useRouter()
  const [subjects, setSubjects] = useState<Subject[]>([])
  const [subjectId, setSubjectId] = useState<number>()
  const [questionType, setQuestionType] = useState<QuestionType>('short_answer')
  const [title, setTitle] = useState('')
  const [stem, setStem] = useState('')
  const [optionsText, setOptionsText] = useState('')
  const [answerText, setAnswerText] = useState('')
  const [analysis, setAnalysis] = useState('')
  const [difficulty, setDifficulty] = useState<Difficulty>('unspecified')
  const [knowledgePointIds, setKnowledgePointIds] = useState<number[]>([])
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    listSubjects({ status: 'active' })
      .then((items) => {
        setSubjects(items)
        if (items[0]) setSubjectId(items[0].id)
      })
      .catch((reason: unknown) => setError(reason instanceof Error ? reason.message : '科目加载失败'))
  }, [])

  const save = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (!subjectId) return setError('请先选择科目。')
    const optionValues = optionsText.split('\n').map((value) => value.trim()).filter(Boolean)
    const options = optionValues.map((text, index) => ({ key: String.fromCharCode(65 + index), text }))
    const value = choiceTypes.has(questionType)
      ? answerText.split(/[\n,]/).map((item) => item.trim()).filter(Boolean)
      : questionType === 'true_false'
        ? answerText === 'true'
        : answerText.trim()
    setBusy(true)
    setError(null)
    try {
      const question = await createQuestion({
        subject_id: subjectId,
        title: title.trim() || null,
        stem_md: stem,
        question_type: questionType,
        options: choiceTypes.has(questionType) ? options : [],
        answer_data: { kind: questionType, value },
        analysis_md: analysis.trim() || null,
        difficulty,
        knowledge_point_links: knowledgePointIds.map((knowledge_point_id) => ({ knowledge_point_id })),
        sources: [{ source_type: 'manual', source_title: '手工录入' }],
      })
      router.push(`/manage/questions/${question.id}`)
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : '创建失败')
      setBusy(false)
    }
  }

  return (
    <div className='max-w-3xl space-y-7'>
      <Link href='/manage/questions' className='inline-flex items-center gap-2 text-sm text-slate-500'>
        <ArrowLeft className='h-4 w-4' aria-hidden='true' />返回题库
      </Link>
      <ManageFormPanel onSubmit={save} error={error ?? undefined} actions={<button disabled={busy || !stem.trim()} className='rounded-lg bg-[var(--color-brand)] px-5 py-2 text-sm text-white disabled:opacity-45'>{busy ? '创建中…' : '创建题目'}</button>}>
        <div className='grid gap-4 sm:grid-cols-2'>
          <label className='text-sm text-slate-600'>科目
            <select required value={subjectId ?? ''} onChange={(event) => { setSubjectId(Number(event.target.value)); setKnowledgePointIds([]) }} className='mt-2 w-full rounded-lg border border-slate-200 px-3 py-2.5'>
              {subjects.map((subject) => <option key={subject.id} value={subject.id}>{subject.name}</option>)}
            </select>
          </label>
          <label className='text-sm text-slate-600'>题型
            <select value={questionType} onChange={(event) => { setQuestionType(event.target.value as QuestionType); setOptionsText(''); setAnswerText('') }} className='mt-2 w-full rounded-lg border border-slate-200 px-3 py-2.5'>
              <option value='short_answer'>简答题</option><option value='single_choice'>单选题</option><option value='multiple_choice'>多选题</option><option value='true_false'>判断题</option><option value='essay'>论述题</option>
            </select>
          </label>
        </div>
        <label className='block text-sm text-slate-600'>标题（可选）<input value={title} onChange={(event) => setTitle(event.target.value)} className='mt-2 w-full rounded-lg border border-slate-200 px-3 py-2.5' /></label>
        <label className='block text-sm text-slate-600'>题干<textarea required value={stem} onChange={(event) => setStem(event.target.value)} rows={6} className='mt-2 w-full rounded-lg border border-slate-200 px-3 py-2.5' /></label>
        {choiceTypes.has(questionType) ? <label className='block text-sm text-slate-600'>选项（每行一项）<textarea value={optionsText} onChange={(event) => setOptionsText(event.target.value)} rows={5} className='mt-2 w-full rounded-lg border border-slate-200 px-3 py-2.5' /></label> : null}
        <label className='block text-sm text-slate-600'>{questionType === 'true_false' ? '正确答案' : '答案'}
          {questionType === 'true_false' ? <select value={answerText} onChange={(event) => setAnswerText(event.target.value)} className='mt-2 w-full rounded-lg border border-slate-200 px-3 py-2.5'><option value=''>请选择</option><option value='true'>正确</option><option value='false'>错误</option></select> : <textarea value={answerText} onChange={(event) => setAnswerText(event.target.value)} rows={3} className='mt-2 w-full rounded-lg border border-slate-200 px-3 py-2.5' />}
        </label>
        <label className='block text-sm text-slate-600'>解析（可选）<textarea value={analysis} onChange={(event) => setAnalysis(event.target.value)} rows={4} className='mt-2 w-full rounded-lg border border-slate-200 px-3 py-2.5' /></label>
        <label className='block text-sm text-slate-600'>难度<select value={difficulty} onChange={(event) => setDifficulty(event.target.value as Difficulty)} className='mt-2 w-full rounded-lg border border-slate-200 px-3 py-2.5'><option value='unspecified'>未设置</option><option value='easy'>简单</option><option value='medium'>中等</option><option value='hard'>困难</option></select></label>
        {subjectId ? <KnowledgePointMultiSelect subjectId={subjectId} values={knowledgePointIds} onChange={setKnowledgePointIds} /> : null}
      </ManageFormPanel>
    </div>
  )
}
