'use client'

import { useCallback, useEffect, useRef, useState } from 'react'
import Link from 'next/link'
import { ArrowUpRight, PencilLine } from 'lucide-react'

import { AsyncStatePanel } from '@/components/async-state-panel'
import { getTodayPractice, type PracticeTodayResponse } from '@/lib/api/practice'

const SELECTION_REASON_TEXT: Record<string, string> = {
  weak_kp_wrong_rate: '该知识点错误率较高',
  weak_kp_lapse: '该知识点遗忘较多',
  weak_kp_due: '该知识点有待复习内容',
}

export function selectionReasonText(reason: string): string {
  return SELECTION_REASON_TEXT[reason] ?? reason
}

export function PracticeToday() {
  const [data, setData] = useState<PracticeTodayResponse | null>(null)
  const [error, setError] = useState<unknown>(null)
  const [loading, setLoading] = useState(true)
  const resultRegionRef = useRef<HTMLDivElement>(null)
  const retryRequestedRef = useRef(false)

  const load = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      setData(await getTodayPractice())
    } catch (reason) {
      setError(reason)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    void load()
  }, [load])

  useEffect(() => {
    if (!data || !retryRequestedRef.current) return
    retryRequestedRef.current = false
    resultRegionRef.current?.focus()
  }, [data])

  const retry = () => {
    retryRequestedRef.current = true
    return load()
  }

  if (loading) {
    return <AsyncStatePanel status='loading' loadingLabel='正在加载今日练习' skeletonRows={4} />
  }

  if (error || !data) {
    return <AsyncStatePanel status='error' title='今日练习加载失败' error='请检查服务状态后重试。' onRetry={retry} retryLabel='重新尝试' />
  }

  if (data.items.length === 0) {
    return <AsyncStatePanel status='empty' title='今日暂无合适练习' emptyHint='当前没有符合薄弱知识点条件的练习题目，稍后会自动更新。' />
  }

  return (
    <div
      ref={resultRegionRef}
      role='region'
      aria-label='今日练习结果'
      tabIndex={-1}
      className='space-y-3 outline-none focus-visible:ring-2 focus-visible:ring-[var(--brand)]/45'>
      <p className='text-sm text-[var(--admin-text-secondary)]'>共 {data.items.length} 道练习，均来自薄弱知识点。</p>
      <ol className='space-y-3'>
        {data.items.map(item => (
          <li key={`${item.knowledge_point_id}-${item.question_id}`} className='rounded-2xl border border-[var(--admin-border)]/70 p-5'>
            <div className='flex items-center justify-between gap-3'>
              <p className='text-sm font-medium text-[var(--admin-text-primary)]'>知识点 #{item.knowledge_point_id}</p>
              <PencilLine className='h-4 w-4 text-[var(--brand)]' aria-hidden='true' />
            </div>
            <p className='mt-1 text-xs text-[var(--admin-text-tertiary)]'>选题理由：{selectionReasonText(item.selection_reason)}</p>
            <Link
              href={`/manage/questions/${item.question_id}`}
              className='mt-3 inline-flex items-center gap-1 text-sm font-medium text-[var(--brand)] focus-visible:ring-2 focus-visible:ring-[var(--brand)]/45 focus-visible:outline-none'>
              打开题目
              <ArrowUpRight className='h-4 w-4' aria-hidden='true' />
            </Link>
          </li>
        ))}
      </ol>
    </div>
  )
}
