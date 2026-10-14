'use client'

import { FormEvent, useEffect, useMemo, useState } from 'react'
import { PlusCircle } from 'lucide-react'
import { useRouter } from 'next/navigation'

import {
  confirmMistakeAiCandidate,
  createMistakeAiCandidate,
  createMistakeDraft,
  type MistakeAiCandidate,
  type MistakeReason,
} from '@/lib/api/mistakes'
import { listQuestions, type Difficulty, type Question } from '@/lib/api/questions'
import { ManageFormPanel } from '../../../components/manage-form-panel'
import { KnowledgePointMultiSelect } from '../../../components/knowledge-point-select'

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
 * Mistake draft creation form — one of the capture methods.
 * Creates a mistake draft from an active formal question via the
 * same API and fields as the former mistake-workspace create form.
 * On success, navigates to the mistake draft detail page.
 */
export function MistakeDraftEntry() {
  const router = useRouter()
  const [questions, setQuestions] = useState<Question[]>([])
  const [questionId, setQuestionId] = useState('')
  const [myAnswer, setMyAnswer] = useState('')
  const [reasonCategory, setReasonCategory] = useState<MistakeReason>('unknown')
  const [mistakeReason, setMistakeReason] = useState('')
  const [difficulty, setDifficulty] = useState<Difficulty | ''>('')
  const [knowledgePointIds, setKnowledgePointIds] = useState<number[]>([])
  const [loading, setLoading] = useState(true)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)
  // B05b: optional AI error-interpretation candidate generated through the
  // canonical trusted-run contract; cleared whenever its inputs change.
  const [aiBusy, setAiBusy] = useState(false)
  const [aiError, setAiError] = useState<string | null>(null)
  const [candidate, setCandidate] = useState<MistakeAiCandidate | null>(null)

  const selectedQuestion = useMemo(
    () => questions.find((question) => question.id === questionId) ?? null,
    [questionId, questions],
  )

  useEffect(() => {
    listQuestions({ status: 'active' })
      .then((nextQuestions) => {
        setQuestions(nextQuestions)
        if (nextQuestions[0]) setQuestionId(nextQuestions[0].id)
      })
      .catch((reason) => setError(message(reason, '加载题目失败')))
      .finally(() => setLoading(false))
  }, [])

  const generateCandidate = async () => {
    if (!questionId) return
    const reason = mistakeReason.trim()
    if (!reason) {
      setAiError('请先填写错因说明，AI 才能给出错因候选')
      return
    }
    setAiBusy(true)
    setAiError(null)
    setCandidate(null)
    try {
      const next = await createMistakeAiCandidate({
        question_id: questionId,
        my_answer: myAnswer || null,
        user_error_reason: reason,
      })
      setCandidate(next)
    } catch (generateError) {
      setAiError(message(generateError, '生成AI错因候选失败'))
    } finally {
      setAiBusy(false)
    }
  }

  const confirmCandidate = async () => {
    if (!candidate || !questionId) return
    setBusy(true)
    setError(null)
    try {
      const created = await confirmMistakeAiCandidate({
        run_id: candidate.run_id,
        review_revision: candidate.review_revision,
        question_id: questionId,
        my_answer: myAnswer || null,
        user_error_reason: mistakeReason.trim() || null,
        reason_category: reasonCategory,
        mistake_reason: mistakeReason || null,
        difficulty: difficulty || null,
        knowledge_point_ids: knowledgePointIds,
        confirmed_candidate: candidate.candidate,
      })
      router.push(`/manage/mistakes/${created.draft_item_id}?kind=draft`)
    } catch (confirmError) {
      setError(message(confirmError, 'AI 候选确认失败'))
      setBusy(false)
    }
  }

  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (!questionId) return
    setBusy(true)
    setError(null)
    try {
      const created = await createMistakeDraft({
        question_id: questionId,
        my_answer: myAnswer || null,
        reason_category: reasonCategory,
        mistake_reason: mistakeReason || null,
        difficulty: difficulty || null,
        knowledge_point_ids: knowledgePointIds,
      })
      router.push(`/manage/mistakes/${created.draft_item_id}?kind=draft`)
    } catch (reason) {
      setError(message(reason, '创建错题草稿失败'))
      setBusy(false)
    }
  }

  return (
    <ManageFormPanel
      variant='heavy'
      title='从题库记录错题'
      description='只从已确认的正式题目创建；选择一道题，记录错因，生成错题草稿后进入待确认。'
      error={error ?? undefined}
      onSubmit={submit}
      actions={
        <button
          disabled={busy || !questionId}
          className='inline-flex items-center gap-2 rounded-lg bg-[var(--color-brand)] px-5 py-2.5 text-sm font-medium text-white disabled:opacity-45'
        >
          <PlusCircle className='h-4 w-4' />
          {busy ? '创建中…' : '创建草稿'}
        </button>
      }
    >
      {!loading && questions.length === 0 ? (
        <p role='status' className='rounded-lg bg-amber-50 px-3 py-2 text-sm leading-6 text-amber-700'>
          题库中还没有已确认的正式题目。请先到&ldquo;待确认&rdquo;审核题目入库，再来记录错题。
        </p>
      ) : null}
      <label className='block text-sm font-medium text-slate-700'>
        来源题目
        <select
          value={questionId}
          disabled={loading || busy}
          onChange={(event) => {
            setQuestionId(event.target.value)
            setKnowledgePointIds([])
            setCandidate(null)
          }}
          className='mt-2 w-full rounded-lg border border-slate-200 bg-white px-3 py-2.5 text-sm'
        >
          {questions.map((question) => (
            <option key={question.id} value={question.id}>
              {question.title || question.question_text.slice(0, 42)}
            </option>
          ))}
        </select>
      </label>
      {selectedQuestion ? (
        <div className='rounded-lg bg-slate-50 p-4 text-sm leading-6 text-slate-600'>
          <p className='font-medium text-slate-800'>{selectedQuestion.title || '未命名题目'}</p>
          <p className='mt-1 line-clamp-4 whitespace-pre-wrap'>{selectedQuestion.question_text}</p>
        </div>
      ) : null}
      <label className='block text-sm font-medium text-slate-700'>
        我的答案
        <textarea
          value={myAnswer}
          disabled={busy}
          onChange={(event) => {
            setMyAnswer(event.target.value)
            setCandidate(null)
          }}
          rows={3}
          className='mt-2 w-full rounded-lg border border-slate-200 px-3 py-2.5 text-sm'
          placeholder='记录当时的错误答案或思路'
        />
      </label>
      <div className='grid gap-4 sm:grid-cols-2'>
        <label className='block text-sm font-medium text-slate-700'>
          错因类型
          <select
            value={reasonCategory}
            disabled={busy}
            onChange={(event) => setReasonCategory(event.target.value as MistakeReason)}
            className='mt-2 w-full rounded-lg border border-slate-200 bg-white px-3 py-2.5 text-sm'
          >
            {Object.entries(reasonLabels).map(([value, label]) => (
              <option key={value} value={value}>{label}</option>
            ))}
          </select>
        </label>
        <label className='block text-sm font-medium text-slate-700'>
          难度
          <select
            value={difficulty}
            disabled={busy}
            onChange={(event) => setDifficulty(event.target.value as Difficulty | '')}
            className='mt-2 w-full rounded-lg border border-slate-200 bg-white px-3 py-2.5 text-sm'
          >
            <option value=''>未设置</option>
            <option value='easy'>简单</option>
            <option value='medium'>中等</option>
            <option value='hard'>困难</option>
          </select>
        </label>
      </div>
      <label className='block text-sm font-medium text-slate-700'>
        错因说明
        <textarea
          value={mistakeReason}
          disabled={busy}
          onChange={(event) => {
            setMistakeReason(event.target.value)
            setCandidate(null)
          }}
          rows={3}
          className='mt-2 w-full rounded-lg border border-slate-200 px-3 py-2.5 text-sm'
          placeholder='这一步为什么错？'
        />
      </label>
      <div className='rounded-lg border border-slate-200 bg-slate-50 p-4 text-sm leading-6 text-slate-600'>
        <div className='flex flex-wrap items-center justify-between gap-3'>
          <p className='text-slate-700'>AI 错因候选（可选，生成后仍需人工确认）</p>
          <button
            type='button'
            disabled={aiBusy || busy || !questionId || !mistakeReason.trim()}
            onClick={() => void generateCandidate()}
            className='inline-flex min-h-10 items-center rounded-lg border border-slate-300 bg-white px-3 text-sm text-slate-700 disabled:opacity-45'
          >
            {aiBusy ? '生成中…' : candidate ? '重新生成候选' : '生成AI错因候选'}
          </button>
        </div>
        {aiError ? <p className='mt-2 text-sm text-red-600'>{aiError}</p> : null}
        {candidate ? (
          <div className='mt-3 space-y-2'>
            <p className='rounded bg-white p-2 text-slate-700'>
              AI候选：{String((candidate.candidate as { summary?: string }).summary ?? '（无摘要）')}
            </p>
            <button
              type='button'
              disabled={busy || aiBusy}
              onClick={() => void confirmCandidate()}
              className='inline-flex min-h-10 items-center rounded-lg bg-[var(--color-brand)] px-3 text-sm font-medium text-white disabled:opacity-45'
            >
              {busy ? '确认中…' : '按AI候选创建草稿'}
            </button>
          </div>
        ) : null}
      </div>
      <KnowledgePointMultiSelect
        disabled={busy || !selectedQuestion}
        subjectId={selectedQuestion?.subject_id}
        values={knowledgePointIds}
        onChange={setKnowledgePointIds}
      />
    </ManageFormPanel>
  )
}
