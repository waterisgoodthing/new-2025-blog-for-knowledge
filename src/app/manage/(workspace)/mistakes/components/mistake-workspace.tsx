'use client'

import Link from 'next/link'
import { FormEvent, useEffect, useMemo, useState } from 'react'
import { ArrowRight, CheckCircle2, PlusCircle } from 'lucide-react'

import {
  createMistakeDraft,
  listMistakeDrafts,
  listMistakes,
  type Mistake,
  type MistakeDraft,
  type MistakeReason,
} from '@/lib/api/mistakes'
import { listQuestions, type Difficulty, type Question } from '@/lib/api/questions'
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

export function MistakeWorkspace() {
  const [questions, setQuestions] = useState<Question[]>([])
  const [drafts, setDrafts] = useState<MistakeDraft[]>([])
  const [mistakes, setMistakes] = useState<Mistake[]>([])
  const [questionId, setQuestionId] = useState('')
  const [myAnswer, setMyAnswer] = useState('')
  const [reasonCategory, setReasonCategory] = useState<MistakeReason>('unknown')
  const [mistakeReason, setMistakeReason] = useState('')
  const [difficulty, setDifficulty] = useState<Difficulty | ''>('')
  const [knowledgePointIds, setKnowledgePointIds] = useState<number[]>([])
  const [loading, setLoading] = useState(true)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const selectedQuestion = useMemo(
    () => questions.find((question) => question.id === questionId) ?? null,
    [questionId, questions],
  )

  async function load() {
    setLoading(true)
    setError(null)
    try {
      const [nextQuestions, nextDrafts, nextMistakes] = await Promise.all([
        listQuestions({ status: 'active' }),
        listMistakeDrafts('pending'),
        listMistakes('active'),
      ])
      setQuestions(nextQuestions)
      setDrafts(nextDrafts)
      setMistakes(nextMistakes)
      if (!questionId && nextQuestions[0]) setQuestionId(nextQuestions[0].id)
    } catch (reason) {
      setError(message(reason, '加载错题工作区失败'))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void load()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const createDraft = async (event: FormEvent) => {
    event.preventDefault()
    if (!questionId) return
    setBusy(true)
    setError(null)
    try {
      await createMistakeDraft({
        question_id: questionId,
        my_answer: myAnswer || null,
        reason_category: reasonCategory,
        mistake_reason: mistakeReason || null,
        difficulty: difficulty || null,
        knowledge_point_ids: knowledgePointIds,
      })
      setMyAnswer('')
      setMistakeReason('')
      setReasonCategory('unknown')
      setDifficulty('')
      setKnowledgePointIds([])
      await load()
    } catch (reason) {
      setError(message(reason, '创建错题草稿失败'))
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className='grid gap-7 xl:grid-cols-[minmax(0,0.95fr)_minmax(0,1.05fr)]'>
      <section className='rounded-3xl border border-slate-200/70 bg-white/80 p-5 shadow-sm'>
        <div className='flex items-center gap-2'>
          <PlusCircle className='h-5 w-5 text-[var(--color-brand)]' />
          <h2 className='font-semibold text-slate-900'>从题库创建错题草稿</h2>
        </div>
        <p className='mt-2 text-sm leading-6 text-slate-500'>
          只从已确认的正式 Question 创建；公开错题 Note 不会被改写或迁移。
        </p>
        <form onSubmit={createDraft} className='mt-5 space-y-4'>
          {!loading && questions.length === 0 ? (
            <p role='status' className='rounded-xl bg-amber-50 px-3 py-2 text-sm leading-6 text-amber-700'>
              题库中还没有 active 状态的正式题目。请先在“待审核”确认题目入库，再创建错题草稿。
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
              }}
              className='mt-2 w-full rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-sm'
            >
              {questions.map((question) => (
                <option key={question.id} value={question.id}>
                  {question.title || question.question_text.slice(0, 42)}
                </option>
              ))}
            </select>
          </label>
          {selectedQuestion ? (
            <div className='rounded-2xl bg-slate-50 p-4 text-sm leading-6 text-slate-600'>
              <p className='font-medium text-slate-800'>{selectedQuestion.title || '未命名题目'}</p>
              <p className='mt-1 line-clamp-4 whitespace-pre-wrap'>{selectedQuestion.question_text}</p>
            </div>
          ) : null}
          <label className='block text-sm font-medium text-slate-700'>
            我的答案
            <textarea
              value={myAnswer}
              disabled={busy}
              onChange={(event) => setMyAnswer(event.target.value)}
              rows={3}
              className='mt-2 w-full rounded-xl border border-slate-200 px-3 py-2.5 text-sm'
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
                className='mt-2 w-full rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-sm'
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
                className='mt-2 w-full rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-sm'
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
              onChange={(event) => setMistakeReason(event.target.value)}
              rows={3}
              className='mt-2 w-full rounded-xl border border-slate-200 px-3 py-2.5 text-sm'
              placeholder='这一步为什么错？'
            />
          </label>
          <KnowledgePointMultiSelect
            disabled={busy || !selectedQuestion}
            subjectId={selectedQuestion?.subject_id}
            values={knowledgePointIds}
            onChange={setKnowledgePointIds}
          />
          {error ? <p role='alert' className='text-sm text-red-600'>{error}</p> : null}
          <button
            disabled={busy || !questionId}
            className='inline-flex items-center gap-2 rounded-xl bg-[var(--color-brand)] px-5 py-2.5 text-sm font-medium text-white disabled:opacity-45'
          >
            <PlusCircle className='h-4 w-4' />
            {busy ? '创建中…' : '创建草稿'}
          </button>
        </form>
      </section>

      <section className='space-y-7'>
        <div className='rounded-3xl border border-slate-200/70 bg-white/80 p-5 shadow-sm'>
          <div className='flex items-center justify-between gap-4'>
            <div>
              <h2 className='font-semibold text-slate-900'>待审核草稿</h2>
              <p className='mt-1 text-sm text-slate-500'>人工确认后才会生成私有 Mistake 与 ReviewItem。</p>
            </div>
            <span className='rounded-full bg-amber-50 px-3 py-1 text-xs text-amber-700'>{drafts.length} 条</span>
          </div>
          {loading ? <p className='py-6 text-sm text-slate-400'>正在加载…</p> : null}
          {!loading && drafts.length === 0 ? <p className='py-6 text-sm text-slate-500'>暂无待审核错题草稿。</p> : null}
          {drafts.map((draft) => (
            <Link key={draft.draft_item_id} href={`/manage/mistakes/${draft.draft_item_id}?kind=draft`} className='group flex items-center gap-4 border-t border-slate-100 py-4 first:mt-4'>
              <span className='min-w-0 flex-1'>
                <span className='block truncate font-medium text-slate-800'>{draft.title || draft.question_text}</span>
                <span className='mt-1 block text-xs text-slate-400'>{reasonLabels[draft.reason_category]} · {draft.status} · v{draft.version}</span>
              </span>
              <ArrowRight className='h-4 w-4 text-slate-300 group-hover:text-[var(--color-brand)]' />
            </Link>
          ))}
        </div>

        <div className='rounded-3xl border border-slate-200/70 bg-white/80 p-5 shadow-sm'>
          <div className='flex items-center justify-between gap-4'>
            <div>
              <h2 className='font-semibold text-slate-900'>正式错题</h2>
              <p className='mt-1 text-sm text-slate-500'>仅管理员可见；公开 `/mistakes` 仍使用旧 Note。</p>
            </div>
            <span className='rounded-full bg-emerald-50 px-3 py-1 text-xs text-emerald-700'>{mistakes.length} 条</span>
          </div>
          {!loading && mistakes.length === 0 ? <p className='py-6 text-sm text-slate-500'>暂无正式错题。</p> : null}
          {mistakes.map((mistake) => (
            <Link key={mistake.id} href={`/manage/mistakes/${mistake.id}?kind=mistake`} className='group flex items-center gap-4 border-t border-slate-100 py-4 first:mt-4'>
              <CheckCircle2 className='h-4 w-4 text-emerald-500' />
              <span className='min-w-0 flex-1'>
                <span className='block truncate font-medium text-slate-800'>{mistake.title || mistake.question_text}</span>
                <span className='mt-1 block text-xs text-slate-400'>{reasonLabels[mistake.reason_category]} · {mistake.status} · review {mistake.review_item_id}</span>
              </span>
              <ArrowRight className='h-4 w-4 text-slate-300 group-hover:text-[var(--color-brand)]' />
            </Link>
          ))}
        </div>
      </section>
    </div>
  )
}
