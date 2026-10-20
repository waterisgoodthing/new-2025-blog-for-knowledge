'use client'

import { CircleAlert, Inbox } from 'lucide-react'
import { type ReactNode, useRef, useState } from 'react'

export type AsyncStateStatus = 'loading' | 'empty' | 'error'

export type AsyncStatePanelProps = {
  status: AsyncStateStatus
  error?: unknown
  emptyHint?: ReactNode
  onRetry?: () => void | Promise<unknown>
  loadingLabel?: string
  skeletonRows?: number
  skeletonTestId?: string
  retryLabel?: string
  title?: string
}

function errorMessage(error: unknown): string {
  if (typeof error === 'string' && error) return error
  if (error instanceof Error && error.name === 'ApiError' && error.message) return error.message
  return '服务暂时不可用，请稍后重试。'
}

export function AsyncStatePanel({
  status,
  error,
  emptyHint = '暂无可展示内容。',
  onRetry,
  loadingLabel = '正在加载内容',
  skeletonRows = 4,
  skeletonTestId = 'async-state-panel-skeleton',
  retryLabel = '重试',
  title
}: AsyncStatePanelProps) {
  const panelRef = useRef<HTMLDivElement>(null)
  const [retrying, setRetrying] = useState(false)

  if (status === 'loading') {
    return (
      <div role='status' aria-label={loadingLabel} className='space-y-3 py-4 motion-reduce:animate-none'>
        {Array.from({ length: Math.max(1, skeletonRows) }, (_, index) => (
          <div key={index} data-testid={skeletonTestId} className='animate-pulse border-b border-slate-200/55 pb-3 motion-reduce:animate-none' aria-hidden='true'>
            <div className='h-3 w-2/5 rounded-full bg-slate-200/75' />
            <div className='mt-2 h-2.5 w-3/5 rounded-full bg-slate-100' />
          </div>
        ))}
      </div>
    )
  }

  const handleRetry = () => {
    if (!onRetry || retrying) return
    const result = onRetry()
    if (!result || typeof result.then !== 'function') {
      panelRef.current?.focus()
      return
    }
    setRetrying(true)
    void Promise.resolve(result).then(() => undefined, () => undefined).finally(() => {
      setRetrying(false)
      panelRef.current?.focus()
    })
  }

  return (
    <div ref={panelRef} role='region' aria-label='数据面板' tabIndex={-1} className='flex min-h-44 items-center border-y border-slate-200/60 py-8 outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-brand)]/45'>
      <div className='max-w-lg'>
        <div className='flex items-start gap-3'>
          <span className={`mt-0.5 inline-flex h-9 w-9 shrink-0 items-center justify-center rounded-full ${status === 'error' ? 'bg-red-50 text-red-600' : 'bg-slate-100 text-slate-500'}`}>
            {status === 'error' ? <CircleAlert className='h-4 w-4' aria-hidden='true' /> : <Inbox className='h-4 w-4' aria-hidden='true' />}
          </span>
          <div>
            <h2 className='font-semibold text-slate-900'>{title ?? (status === 'error' ? '加载失败' : '暂无内容')}</h2>
            {status === 'error' ? (
              <p role='alert' aria-live='assertive' className='mt-1 break-words text-sm leading-6 text-slate-500'>{errorMessage(error)}</p>
            ) : (
              <div className='mt-1 text-sm leading-6 text-slate-500'>{emptyHint}</div>
            )}
            {status === 'error' && onRetry ? (
              <button type='button' onClick={handleRetry} disabled={retrying} aria-busy={retrying} className='mt-4 rounded-lg border border-slate-200 bg-white/70 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-white disabled:cursor-wait disabled:opacity-60 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-brand)]/45'>
                {retrying ? '重试中...' : retryLabel}
              </button>
            ) : null}
          </div>
        </div>
      </div>
    </div>
  )
}
