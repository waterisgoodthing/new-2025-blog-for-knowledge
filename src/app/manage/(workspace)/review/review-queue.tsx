'use client'

import { useEffect, useState } from 'react'
import { Brain, CheckCircle2, History } from 'lucide-react'

import {
  listDueReviewItems,
  listReviewRecords,
  submitReview,
  type ReviewItem,
  type ReviewRating,
  type ReviewRecord,
} from '@/lib/api/review-items'

function message(reason: unknown, fallback: string) {
  return reason instanceof Error ? reason.message : fallback
}

const ratings: ReviewRating[] = [0, 1, 2, 3, 4, 5]

export function ReviewQueue() {
  const [items, setItems] = useState<ReviewItem[]>([])
  const [records, setRecords] = useState<Record<string, ReviewRecord[]>>({})
  const [loading, setLoading] = useState(true)
  const [busyId, setBusyId] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)

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

  async function submit(item: ReviewItem, rating: ReviewRating) {
    setBusyId(item.id)
    setError(null)
    setSuccess(null)
    try {
      const updated = await submitReview(item.id, rating, item.next_review_at)
      setItems((current) => current.filter((candidate) => candidate.id !== item.id))
      setSuccess(`已提交复习，下一次复习时间：${new Date(updated.next_review_at).toLocaleString('zh-CN')}`)
    } catch (reason) {
      setError(message(reason, '提交复习失败'))
    } finally {
      setBusyId(null)
    }
  }

  return (
    <section className='space-y-5'>
      <div className='rounded-3xl border border-slate-200/70 bg-white/80 p-5 shadow-sm'>
        <div className='flex items-center gap-3'>
          <Brain className='h-5 w-5 text-[var(--color-brand)]' />
          <div>
            <h2 className='font-semibold text-slate-900'>今日到期</h2>
            <p className='mt-1 text-sm text-slate-500'>固定间隔：0-2 分为 1 天，3 分 3 天，4 分 7 天，5 分 14 天。</p>
          </div>
        </div>
        {success ? (
          <p className='mt-4 inline-flex items-center gap-2 rounded-2xl bg-emerald-50 px-3 py-2 text-sm text-emerald-700'>
            <CheckCircle2 className='h-4 w-4' />
            {success}
          </p>
        ) : null}
        {error ? <p role='alert' className='mt-4 text-sm text-red-600'>{error}</p> : null}
      </div>

      {loading ? <p className='rounded-3xl border border-slate-200/70 bg-white/80 p-6 text-sm text-slate-400'>正在加载复习队列…</p> : null}
      {!loading && items.length === 0 ? (
        <p className='rounded-3xl border border-slate-200/70 bg-white/80 p-6 text-sm text-slate-500'>当前没有到期复习项。好消息，今天的小怪兽暂时睡着了。</p>
      ) : null}

      {items.map((item) => (
        <article key={item.id} className='rounded-3xl border border-slate-200/70 bg-white/80 p-5 shadow-sm'>
          <div className='flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between'>
            <div className='min-w-0 flex-1'>
              <p className='text-xs tracking-wider text-[var(--color-brand)] uppercase'>
                {item.algorithm} · 第 {item.repetitions + 1} 次 · 当前间隔 {item.interval_days} 天
              </p>
              <h3 className='mt-2 whitespace-pre-wrap text-base font-semibold leading-7 text-slate-900'>{item.question_text}</h3>
              {item.mistake_reason ? <p className='mt-3 rounded-2xl bg-amber-50 p-3 text-sm leading-6 text-amber-800'>错因：{item.mistake_reason}</p> : null}
              <p className='mt-3 text-xs text-slate-400'>到期时间：{new Date(item.next_review_at).toLocaleString('zh-CN')}</p>
            </div>
            <div className='flex flex-wrap gap-2 lg:max-w-56 lg:justify-end'>
              {ratings.map((rating) => (
                <button
                  key={rating}
                  disabled={busyId === item.id}
                  onClick={() => void submit(item, rating)}
                  className='h-10 w-10 rounded-xl border border-slate-200 bg-white text-sm font-semibold text-slate-700 hover:border-[var(--color-brand)] hover:text-[var(--color-brand)] disabled:opacity-45'
                  aria-label={`提交 ${rating} 分复习结果`}
                >
                  {rating}
                </button>
              ))}
              <button
                disabled={busyId === item.id}
                onClick={() => void toggleRecords(item.id)}
                className='inline-flex h-10 items-center gap-2 rounded-xl border border-slate-200 px-3 text-sm text-slate-600 disabled:opacity-45'
              >
                <History className='h-4 w-4' />
                记录
              </button>
            </div>
          </div>
          {records[item.id] ? (
            <div className='mt-5 border-t border-slate-100 pt-4'>
              {records[item.id].length === 0 ? <p className='text-sm text-slate-400'>暂无历史记录。</p> : null}
              {records[item.id].map((record) => (
                <div key={record.id} className='grid gap-2 border-b border-slate-100 py-3 text-sm text-slate-600 last:border-b-0 sm:grid-cols-4'>
                  <span>评分 {record.rating}</span>
                  <span>{record.previous_interval_days} → {record.next_interval_days} 天</span>
                  <span className='sm:col-span-2'>{new Date(record.reviewed_at).toLocaleString('zh-CN')}</span>
                </div>
              ))}
            </div>
          ) : null}
        </article>
      ))}
    </section>
  )
}
