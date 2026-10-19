'use client'

import { useEffect, useRef, useState, type KeyboardEvent } from 'react'
import { CheckCircle2, History, PenLine } from 'lucide-react'

import {
  listDueReviewItems,
  listReviewRecords,
  submitReview,
  type ReviewItem,
  type ReviewRating,
  type ReviewRecord,
} from '@/lib/api/review-items'
import { getMistake } from '@/lib/api/mistakes'
import { getQuestion, type Question } from '@/lib/api/questions'
import { submitReanswer, type ReanswerEvaluation } from '@/lib/api/attempts'
import { formatChineseDateTime } from '@/lib/manage-display'

import { FeatureState } from '../../components/feature-state'
import { ManagePanel } from '../../components/manage-panel'

function message(reason: unknown, fallback: string) {
  return reason instanceof Error ? reason.message : fallback
}

const ratings: ReviewRating[] = [0, 1, 2, 3, 4, 5]

const verdictText: Record<ReanswerEvaluation['verdict'], string> = {
  correct: '作答正确',
  incorrect: '作答有误',
  needs_human: '需人工判定',
}

interface ReanswerPanel {
  open: boolean
  phase: 'editing' | 'evaluated'
  question: Question | null
  questionMissing: boolean
  answer: string
  evaluation: ReanswerEvaluation | null
  attemptId: string | null
  busy: boolean
  error: string | null
}

const closedPanel: ReanswerPanel = {
  open: false,
  phase: 'editing',
  question: null,
  questionMissing: false,
  answer: '',
  evaluation: null,
  attemptId: null,
  busy: false,
  error: null,
}

export function ReviewQueue() {
  const [items, setItems] = useState<ReviewItem[]>([])
  const [records, setRecords] = useState<Record<string, ReviewRecord[]>>({})
  const [loading, setLoading] = useState(true)
  const [busyId, setBusyId] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)
  const [panels, setPanels] = useState<Record<string, ReanswerPanel>>({})

  // EV01 fix: every in-flight re-answer request captures the item's generation
  // and may only publish its result while that generation is still current.
  // Opening, closing, switching the question or editing the answer bumps it, so
  // a late response can never attach an old evaluation/attempt to a new answer.
  const generationRef = useRef<Record<string, number>>({})
  const mountedRef = useRef(true)

  function bumpGeneration(itemId: string): number {
    const next = (generationRef.current[itemId] ?? 0) + 1
    generationRef.current[itemId] = next
    return next
  }

  function isCurrent(itemId: string, generation: number): boolean {
    return mountedRef.current && (generationRef.current[itemId] ?? 0) === generation
  }

  useEffect(() => {
    mountedRef.current = true
    return () => {
      mountedRef.current = false
      generationRef.current = {}
    }
  }, [])

  async function load() {
    setLoading(true)
    setError(null)
    try {
      setItems(await listDueReviewItems())
    } catch (reason) {
      setError(message(reason, '加载复习队列失败'))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void load()
  }, [])

  async function toggleRecords(itemId: string) {
    if (records[itemId]) {
      setRecords((current) => {
        const next = { ...current }
        delete next[itemId]
        return next
      })
      return
    }
    setBusyId(itemId)
    setError(null)
    try {
      const nextRecords = await listReviewRecords(itemId)
      setRecords((current) => ({ ...current, [itemId]: nextRecords }))
    } catch (reason) {
      setError(message(reason, '加载复习记录失败'))
    } finally {
      setBusyId(null)
    }
  }

  function patchPanel(itemId: string, patch: Partial<ReanswerPanel>) {
    setPanels((current) => ({ ...current, [itemId]: { ...(current[itemId] ?? closedPanel), ...patch } }))
  }

  async function openReanswer(item: ReviewItem) {
    const generation = bumpGeneration(item.id)
    patchPanel(item.id, { ...closedPanel, open: true, busy: true })
    setError(null)
    try {
      const mistake = await getMistake(item.target_id)
      if (!isCurrent(item.id, generation)) return
      if (!mistake.question_id) {
        patchPanel(item.id, { busy: false, questionMissing: true })
        return
      }
      const question = await getQuestion(mistake.question_id)
      if (!isCurrent(item.id, generation)) return
      patchPanel(item.id, { busy: false, question })
    } catch (reason) {
      if (!isCurrent(item.id, generation)) return
      patchPanel(item.id, { busy: false, error: message(reason, '加载题目失败') })
    }
  }

  function closeReanswer(itemId: string) {
    bumpGeneration(itemId)
    patchPanel(itemId, { ...closedPanel })
  }

  async function submitAnswer(item: ReviewItem) {
    const panel = panels[item.id] ?? closedPanel
    if (!panel.question || !panel.answer.trim()) return
    const generation = generationRef.current[item.id] ?? 0
    const questionId = panel.question.id
    const answer = panel.answer.trim()
    patchPanel(item.id, { busy: true, error: null })
    try {
      const result = await submitReanswer(questionId, answer)
      // Drop the response if the panel was closed, reopened, switched or the
      // answer was edited while the request was in flight.
      if (!isCurrent(item.id, generation)) return
      patchPanel(item.id, {
        busy: false,
        phase: 'evaluated',
        evaluation: result.evaluation,
        attemptId: result.attempt.id,
      })
    } catch (reason) {
      if (!isCurrent(item.id, generation)) return
      patchPanel(item.id, { busy: false, error: message(reason, '提交作答失败') })
    }
  }

  async function submit(item: ReviewItem, rating: ReviewRating, attemptId?: string) {
    setBusyId(item.id)
    setError(null)
    setSuccess(null)
    try {
      const updated = await submitReview(item.id, rating, item.next_review_at, attemptId)
      bumpGeneration(item.id)
      setItems((current) => current.filter((candidate) => candidate.id !== item.id))
      setPanels((current) => {
        const next = { ...current }
        delete next[item.id]
        return next
      })
      setSuccess(`已提交复习，下一次复习时间：${formatChineseDateTime(updated.next_review_at)}`)
    } catch (reason) {
      setError(message(reason, '提交复习失败'))
    } finally {
      setBusyId(null)
    }
  }

  function ratingKeyDown(item: ReviewItem, attemptId: string | null, event: KeyboardEvent) {
    if (busyId === item.id) return
    if (/^[0-5]$/.test(event.key)) {
      event.preventDefault()
      void submit(item, Number(event.key) as ReviewRating, attemptId ?? undefined)
    }
  }

  function setAnswer(itemId: string, next: string) {
    // Editing the answer invalidates any previous evaluation/attempt so the
    // user cannot confirm a score that belongs to an earlier submission.
    bumpGeneration(itemId)
    patchPanel(itemId, { answer: next, phase: 'editing', evaluation: null, attemptId: null, busy: false })
  }

  function renderAnswerInput(item: ReviewItem, panel: ReanswerPanel) {
    const question = panel.question
    if (!question) return null
    const options = question.options ?? []
    if (options.length > 0) {
      const multiple = question.question_type === 'multiple_choice'
      const optionKeys = options.map((option) => option.key)
      const selected = new Set(
        panel.answer
          .split(',')
          .map((key) => key.trim())
          .filter(Boolean),
      )
      return (
        <div
          className='flex flex-wrap gap-2'
          role='group'
          aria-label={multiple ? '作答选项（可多选）' : '作答选项'}
        >
          {options.map((option) => {
            const pressed = multiple ? selected.has(option.key) : panel.answer === option.key
            return (
              <button
                key={option.key}
                disabled={panel.busy}
                onClick={() => {
                  if (!multiple) {
                    setAnswer(item.id, option.key)
                    return
                  }
                  const next = new Set(selected)
                  if (next.has(option.key)) next.delete(option.key)
                  else next.add(option.key)
                  setAnswer(
                    item.id,
                    optionKeys.filter((key) => next.has(key)).join(','),
                  )
                }}
                aria-pressed={pressed}
                className='min-h-11 rounded-lg border border-[var(--admin-border)] bg-[var(--admin-surface)] px-3 text-sm text-[var(--admin-text-[var(--admin-text-primary)])] disabled:opacity-45'
              >
                {option.key}. {option.text}
              </button>
            )
          })}
        </div>
      )
    }
    return (
      <label className='flex flex-col gap-2 text-sm text-[var(--admin-text-[var(--admin-text-secondary)])]'>
        你的答案
        <input
          value={panel.answer}
          disabled={panel.busy}
          onChange={(event) => setAnswer(item.id, event.target.value)}
          placeholder='输入本次重做答案'
          className='min-h-11 rounded-lg border border-[var(--admin-border)] bg-[var(--admin-surface)] px-3 text-[var(--admin-text-[var(--admin-text-primary)])] disabled:opacity-45'
        />
      </label>
    )
  }

  function renderReanswer(item: ReviewItem) {
    const panel = panels[item.id] ?? closedPanel
    if (!panel.open) {
      return (
        <button
          disabled={busyId === item.id}
          onClick={() => void openReanswer(item)}
          className='inline-flex min-h-11 items-center gap-2 rounded-lg border border-[var(--admin-border)] px-3 text-sm text-[var(--admin-text-[var(--admin-text-secondary)])] disabled:opacity-45'
        >
          <PenLine className='h-4 w-4' />
          再答
        </button>
      )
    }
    return (
      <div className='mt-4 space-y-3 rounded-xl border border-[var(--admin-border)] bg-[var(--admin-surface-subtle)] p-4'>
        <div className='flex items-center justify-between'>
          <p className='text-sm font-semibold text-[var(--admin-text-[var(--admin-text-primary)])]'>再答</p>
          <button
            onClick={() => closeReanswer(item.id)}
            className='min-h-11 px-2 text-sm text-[var(--admin-text-[var(--admin-text-secondary)])]'
          >
            收起
          </button>
        </div>
        {panel.busy && !panel.question && !panel.questionMissing ? (
          <p className='text-sm text-[var(--admin-text-[var(--admin-text-secondary)])]'>正在加载题目…</p>
        ) : null}
        {panel.error ? <p className='text-sm text-red-600'>{panel.error}</p> : null}
        {panel.questionMissing ? (
          <p className='text-sm text-[var(--admin-text-[var(--admin-text-secondary)])]'>该错题无关联题目，仅支持人工评分（下方六档）。</p>
        ) : null}
        {panel.question ? (
          <div className='space-y-3'>
            {renderAnswerInput(item, panel)}
            {panel.phase === 'editing' ? (
              <button
                disabled={panel.busy || !panel.answer.trim()}
                onClick={() => void submitAnswer(item)}
                className='min-h-11 rounded-lg bg-[var(--color-brand)] px-4 text-sm font-semibold text-white disabled:opacity-45'
              >
                {panel.busy ? '判分中…' : '提交作答'}
              </button>
            ) : (
              <p className='text-xs text-[var(--admin-text-[var(--admin-text-secondary)])]'>修改答案后将重新判分。</p>
            )}
          </div>
        ) : null}
        {panel.phase === 'evaluated' && panel.evaluation ? (
          <div className='space-y-2'>
            <p className='text-sm text-[var(--admin-text-[var(--admin-text-primary)])]'>
              判定：{verdictText[panel.evaluation.verdict]}
              {panel.evaluation.recommendation !== null
                ? `，建议评分 ${panel.evaluation.recommendation} 分（已预选，可更改）`
                : '，请人工确认评分'}
            </p>
            <p className='text-xs text-[var(--admin-text-[var(--admin-text-secondary)])]'>在下方六档中确认或修正评分后提交，本次提交将关联此次再答记录。</p>
          </div>
        ) : null}
      </div>
    )
  }

  function renderRatings(item: ReviewItem) {
    const panel = panels[item.id] ?? closedPanel
    const attemptId = panel.phase === 'evaluated' ? panel.attemptId : null
    const recommended = panel.phase === 'evaluated' ? panel.evaluation?.recommendation : undefined
    return (
      <div
        className='flex flex-wrap gap-2 lg:max-w-56 lg:justify-end'
        role='group'
        aria-label='六档评分，键盘 0 到 5 快捷提交'
        onKeyDown={(event) => ratingKeyDown(item, attemptId, event)}
      >
        {/* §7.3 纵向排列在此以横向 wrap 实现（§11.2 响应式理由）：窄屏单列、
            宽屏右置；键盘顺序与视觉顺序一致。动效编排（§7.2/§7.4）递延，见 PR-08 文档。 */}
        {ratings.map((rating) => (
          <button
            key={rating}
            disabled={busyId === item.id}
            onClick={() => void submit(item, rating, attemptId ?? undefined)}
            aria-label={`提交 ${rating} 分复习结果${recommended === rating ? '（机器推荐）' : ''}`}
            aria-pressed={recommended === rating}
            className={`h-11 w-11 rounded-lg border text-sm font-semibold disabled:opacity-45 ${
              recommended === rating
                ? 'border-[var(--color-brand)] bg-[var(--color-brand)] text-white'
                : 'border-[var(--admin-border)] bg-[var(--admin-surface)] text-[var(--admin-text-[var(--admin-text-primary)])] hover:border-[var(--color-brand)] hover:text-[var(--color-brand)]'
            }`}
          >
            {rating}
          </button>
        ))}
      </div>
    )
  }

  return (
    <section className='space-y-5'>
      <ManagePanel
        variant='heavy'
        title='今日到期'
        description='固定间隔 v2：失败 0–1 分回到 1 天，2 分 2 天；连续成功按 3 / 7 / 14 / 30 天推进，4 连成功且末评不低于 4 分进入掌握。完整语义见 convergence design.md D2（repetitions>4 维持 30 天，5 分不跳级，paused 不入列）。'
      >
        {success ? (
          <p className='inline-flex items-center gap-2 rounded-lg bg-emerald-50 px-3 py-2 text-sm text-emerald-700'>
            <CheckCircle2 className='h-4 w-4' />
            {success}
          </p>
        ) : null}
        {error ? (
          <FeatureState state={{ kind: 'error', title: '复习操作失败', description: error, retry: load }} />
        ) : null}
      </ManagePanel>

      {loading ? (
        <ManagePanel variant='heavy'>
          <FeatureState state={{ kind: 'loading', label: '正在加载复习队列', rows: 3 }} />
        </ManagePanel>
      ) : null}
      {!loading && items.length === 0 ? (
        <ManagePanel variant='heavy'>
          <FeatureState state={{ kind: 'empty', title: '今日复习已完成', description: '当前没有到期复习任务。' }} />
        </ManagePanel>
      ) : null}

      {items.map((item) => (
        <ManagePanel key={item.id} variant='heavy'>
          <div className='flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between'>
            <div className='min-w-0 flex-1'>
              <p className='text-xs tracking-wider text-[var(--color-brand)] uppercase'>
                {item.algorithm} · 第 {item.repetitions + 1} 次 · 当前间隔 {item.interval_days} 天
              </p>
              <h3 className='mt-2 whitespace-pre-wrap text-base font-semibold leading-7 text-[var(--admin-text-[var(--admin-text-primary)])]'>{item.question_text}</h3>
              {item.mistake_reason ? <p className='mt-3 rounded-lg bg-amber-50 p-3 text-sm leading-6 text-amber-800'>错因：{item.mistake_reason}</p> : null}
              <p className='mt-3 text-xs text-[var(--admin-text-[var(--admin-text-tertiary)])]'>到期时间：{formatChineseDateTime(item.next_review_at)}</p>
            </div>
            <div className='flex flex-col gap-3'>
              {renderRatings(item)}
              <div className='flex flex-wrap gap-2 lg:justify-end'>
                {renderReanswer(item)}
                <button
                  disabled={busyId === item.id}
                  onClick={() => void toggleRecords(item.id)}
                  className='inline-flex min-h-11 items-center gap-2 rounded-lg border border-[var(--admin-border)] px-3 text-sm text-[var(--admin-text-[var(--admin-text-secondary)])] disabled:opacity-45'
                >
                  <History className='h-4 w-4' />
                  记录
                </button>
              </div>
            </div>
          </div>
          {records[item.id] ? (
            <div className='mt-5 border-t border-[var(--admin-divider)] pt-4'>
              {records[item.id].length === 0 ? <p className='text-sm text-[var(--admin-text-[var(--admin-text-tertiary)])]'>暂无历史记录。</p> : null}
              {records[item.id].map((record) => (
                <div key={record.id} className='grid gap-2 border-b border-[var(--admin-divider)] py-3 text-sm text-[var(--admin-text-[var(--admin-text-secondary)])] last:border-b-0 sm:grid-cols-4'>
                  <span>评分 {record.rating}{record.attempt_id ? ' · 含再答' : ''}</span>
                  <span>{record.previous_interval_days} → {record.next_interval_days} 天</span>
                  <span className='sm:col-span-2'>{formatChineseDateTime(record.reviewed_at)}</span>
                </div>
              ))}
            </div>
          ) : null}
        </ManagePanel>
      ))}
    </section>
  )
}
