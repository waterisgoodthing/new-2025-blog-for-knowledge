'use client'

import { useCallback, useEffect, useState } from 'react'
import { toast } from 'sonner'

import { ApiError } from '@/lib/api/client'
import {
  decideAiRun,
  getAiRun,
  getAiRuns,
  retryAiRun,
  type AiRunDetail,
  type AiRunListItem,
  type AiRunReviewStatus,
  type AiRunStatus,
  type AiRunValidationStatus,
} from '@/lib/api/ai-runs'
import { ManageEmptyState } from '../../../components/manage-empty-state'
import { ManageStatusBadge } from '../../../components/manage-status-badge'

const PAGE_SIZE = 20

const statusLabel: Record<AiRunStatus, string> = {
  running: '运行中',
  succeeded: '成功',
  failed: '失败',
}

const statusTone: Record<AiRunStatus, 'neutral' | 'info' | 'success' | 'warning' | 'danger'> = {
  running: 'info',
  succeeded: 'success',
  failed: 'danger',
}

const validationStatusLabel: Record<AiRunValidationStatus, string> = {
  pending: '待校验',
  passed: '通过',
  failed: '未通过',
  warning: '有警告',
  not_applicable: '不适用',
}

const reviewStatusLabel: Record<AiRunReviewStatus, string> = {
  not_required: '无需确认',
  pending: '待确认',
  accepted: '已接受',
  rejected: '已拒绝',
}

const reviewTone: Record<AiRunReviewStatus, 'neutral' | 'info' | 'success' | 'warning' | 'danger'> = {
  not_required: 'neutral',
  pending: 'warning',
  accepted: 'success',
  rejected: 'danger',
}

export function AiRunsPanel() {
  const [runs, setRuns] = useState<AiRunListItem[]>([])
  const [selected, setSelected] = useState<AiRunDetail | null>(null)
  const [status, setStatus] = useState<AiRunStatus | ''>('')
  const [reviewStatus, setReviewStatus] = useState<AiRunReviewStatus | ''>('')
  const [offset, setOffset] = useState(0)
  const [total, setTotal] = useState(0)
  const [rejectNote, setRejectNote] = useState('')
  const [pendingDecision, setPendingDecision] = useState<'accepted' | 'rejected' | null>(null)
  const [loading, setLoading] = useState(true)
  const [acting, setActing] = useState<'retry' | 'accepted' | 'rejected' | null>(null)

  const loadRuns = useCallback(async () => {
    setLoading(true)
    try {
      const response = await getAiRuns({
        status,
        review_status: reviewStatus,
        limit: PAGE_SIZE,
        offset,
      })
      setRuns(response.items)
      setTotal(response.total)
    } catch (error) {
      toast.error(error instanceof Error ? error.message : '加载处理记录失败')
    } finally {
      setLoading(false)
    }
  }, [offset, reviewStatus, status])

  useEffect(() => {
    loadRuns()
  }, [loadRuns])

  const openRun = async (runId: string) => {
    try {
      setSelected(await getAiRun(runId))
      setRejectNote('')
      setPendingDecision(null)
    } catch (error) {
      toast.error(error instanceof Error ? error.message : '加载详情失败')
    }
  }

  const retry = async () => {
    if (!selected) return
    setActing('retry')
    try {
      const child = await retryAiRun(selected.id)
      toast.success(`已创建重试（第 ${child.attempt} 次）`)
      setSelected(child)
      await loadRuns()
    } catch (error) {
      if (error instanceof ApiError && error.status === 409) {
        toast.error('无法重试：缺少重试所需的输入。')
      } else {
        toast.error(error instanceof Error ? error.message : '无法重试')
      }
    } finally {
      setActing(null)
    }
  }

  const decide = async (decision: 'accepted' | 'rejected') => {
    if (!selected) return
    setActing(decision)
    try {
      const updated = await decideAiRun(
        selected.id,
        decision,
        selected.review_revision,
        decision === 'rejected' ? rejectNote.trim() : undefined,
      )
      setSelected(updated)
      setRejectNote('')
      setPendingDecision(null)
      toast.success(decision === 'accepted' ? '已接受该输出' : '已拒绝该输出')
      await loadRuns()
    } catch (error) {
      if (error instanceof ApiError && error.status === 409) {
        toast.error('该记录已被更新，请刷新后重试。')
      } else {
        toast.error(error instanceof Error ? error.message : '提交人工决定失败')
      }
    } finally {
      setActing(null)
    }
  }

  const changeStatus = (value: AiRunStatus | '') => {
    setStatus(value)
    setOffset(0)
    setSelected(null)
  }

  const changeReviewStatus = (value: AiRunReviewStatus | '') => {
    setReviewStatus(value)
    setOffset(0)
    setSelected(null)
  }

  const pageStart = total === 0 ? 0 : offset + 1
  const pageEnd = Math.min(offset + runs.length, total)

  return (
    <section aria-labelledby='runs-title' className='space-y-4'>
      <div className='flex flex-wrap items-end justify-between gap-4 border-b border-slate-200/70 pb-3'>
        <div>
          <h2 id='runs-title' className='font-medium text-slate-800'>全部记录</h2>
          <p className='mt-1 text-xs text-slate-400'>人工接受只确认输出，不会直接写入正式题目、错题或复习项。</p>
        </div>
        <div className='flex gap-2'>
          <select
            aria-label='处理状态'
            value={status}
            onChange={(event) => changeStatus(event.target.value as AiRunStatus | '')}
            className='rounded-lg border border-slate-200 bg-white/60 px-2 py-1 text-xs'
          >
            <option value=''>全部状态</option>
            <option value='running'>运行中</option>
            <option value='succeeded'>成功</option>
            <option value='failed'>失败</option>
          </select>
          <select
            aria-label='人工确认状态'
            value={reviewStatus}
            onChange={(event) => changeReviewStatus(event.target.value as AiRunReviewStatus | '')}
            className='rounded-lg border border-slate-200 bg-white/60 px-2 py-1 text-xs'
          >
            <option value=''>全部确认状态</option>
            <option value='pending'>待确认</option>
            <option value='accepted'>已接受</option>
            <option value='rejected'>已拒绝</option>
            <option value='not_required'>无需确认</option>
          </select>
        </div>
      </div>

      <div className='grid gap-5 lg:grid-cols-[minmax(0,1.45fr)_minmax(300px,0.8fr)]'>
        <div className='overflow-x-auto'>
          {loading ? (
            <ManageEmptyState variant='loading' message='正在加载…' />
          ) : null}
          {!loading && runs.length === 0 ? (
            <ManageEmptyState variant='empty' message='暂无符合条件的记录。' />
          ) : null}
          {!loading && runs.length > 0 ? (
            <table className='w-full text-left text-sm' data-testid='ai-runs-table'>
              <thead className='border-b border-slate-200/55 text-xs text-slate-400'>
                <tr>
                  <th className='py-2 pr-3 font-medium'>时间</th>
                  <th className='py-2 pr-3 font-medium'>任务</th>
                  <th className='py-2 pr-3 font-medium'>状态</th>
                  <th className='py-2 pr-3 font-medium'>校验结果</th>
                  <th className='py-2 font-medium'>人工确认</th>
                </tr>
              </thead>
              <tbody>
                {runs.map((run) => (
                  <tr
                    key={run.id}
                    data-run-id={run.id}
                    tabIndex={0}
                    aria-label={`${run.task_type}，${statusLabel[run.status]}，${reviewStatusLabel[run.review_status]}，按 Enter 查看详情`}
                    className='cursor-pointer border-b border-slate-200/40 hover:bg-white/30 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-brand)]/45 focus-visible:ring-inset'
                    onClick={() => openRun(run.id)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' || e.key === ' ') {
                        e.preventDefault()
                        openRun(run.id)
                      }
                    }}
                  >
                    <td className='py-2.5 pr-3 text-xs text-slate-500'>{new Date(run.created_at).toLocaleString('zh-CN', { hour12: false })}</td>
                    <td className='py-2.5 pr-3 font-mono text-xs text-slate-700'>{run.task_type}</td>
                    <td className='py-2.5 pr-3'>
                      <ManageStatusBadge tone={statusTone[run.status]}>
                        {statusLabel[run.status]}
                      </ManageStatusBadge>
                    </td>
                    <td className='py-2.5 pr-3 text-xs text-slate-500'>
                      {validationStatusLabel[run.validation_status] ?? run.validation_status}
                    </td>
                    <td className='py-2.5 pr-3'>
                      <ManageStatusBadge tone={reviewTone[run.review_status]}>
                        {reviewStatusLabel[run.review_status]}
                      </ManageStatusBadge>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : null}
          <div className='mt-3 flex items-center justify-between border-t border-slate-200/45 pt-3 text-xs text-slate-500'>
            <span>{pageStart}–{pageEnd} / {total}</span>
            <div className='flex gap-2'>
              <button
                type='button'
                onClick={() => setOffset(Math.max(0, offset - PAGE_SIZE))}
                disabled={loading || offset === 0}
                className='rounded-lg border border-slate-200 px-3 py-1.5 hover:bg-white disabled:cursor-not-allowed disabled:opacity-40'
              >
                上一页
              </button>
              <button
                type='button'
                onClick={() => setOffset(offset + PAGE_SIZE)}
                disabled={loading || offset + runs.length >= total}
                className='rounded-lg border border-slate-200 px-3 py-1.5 hover:bg-white disabled:cursor-not-allowed disabled:opacity-40'
              >
                下一页
              </button>
            </div>
          </div>
        </div>

        <aside aria-label='记录详情' className='border-l border-slate-200/45 pl-5'>
          {!selected ? (
            <ManageEmptyState variant='empty' message='选择一条记录查看详情。' />
          ) : (
            <div className='space-y-4'>
              <div>
                <p className='font-mono text-xs text-slate-400'>{selected.id}</p>
                <h3 className='mt-1 font-medium text-slate-800'>{selected.task_type}</h3>
                <p className='mt-1 text-xs text-slate-500'>
                  第 {selected.attempt} 次尝试 · {selected.provider_used || '未选择服务商'} · {selected.prompt_version || '无提示词版本'}
                </p>
              </div>
              <div>
                <h4 className='text-xs font-medium text-slate-500'>受控输出</h4>
                <pre className='mt-1 max-h-72 overflow-auto whitespace-pre-wrap rounded-lg bg-slate-950/90 p-3 text-xs text-slate-100'>
                  {JSON.stringify(selected.output_data, null, 2)}
                </pre>
              </div>
              <div className='flex flex-wrap gap-2'>
                {selected.status !== 'running' && (
                  <button
                    onClick={retry}
                    disabled={acting !== null}
                    className='rounded-lg border border-slate-200 px-3 py-1.5 text-xs text-slate-600 hover:bg-white disabled:opacity-50'
                  >
                    {acting === 'retry' ? '重试中…' : '重试'}
                  </button>
                )}
                {selected.review_status === 'pending' && (
                  <div className='w-full space-y-3'>
                    <label className='block text-xs text-slate-500'>
                      拒绝说明（可选）
                      <textarea
                        value={rejectNote}
                        onChange={(event) => setRejectNote(event.target.value)}
                        maxLength={1000}
                        rows={3}
                        className='mt-1 w-full rounded-lg border border-slate-200 bg-white/70 px-3 py-2 text-sm text-slate-700'
                        placeholder='记录人工拒绝原因'
                      />
                    </label>
                    <div className='flex flex-wrap gap-2'>
                      <button
                        onClick={() => setPendingDecision('accepted')}
                        disabled={acting !== null}
                        className='rounded-lg bg-emerald-600 px-3 py-1.5 text-xs text-white disabled:opacity-50'
                      >
                        {acting === 'accepted' ? '接受中…' : '接受输出'}
                      </button>
                      <button
                        onClick={() => setPendingDecision('rejected')}
                        disabled={acting !== null}
                        className='rounded-lg bg-red-600/10 px-3 py-1.5 text-xs text-red-700 disabled:opacity-50'
                      >
                        {acting === 'rejected' ? '拒绝中…' : '拒绝输出'}
                      </button>
                    </div>
                    {pendingDecision && (
                      <div
                        role='alertdialog'
                        aria-label='确认人工决定'
                        className='rounded-lg border border-amber-200 bg-amber-50/80 p-3'
                      >
                        <p className='text-xs leading-5 text-amber-900'>
                          确认{pendingDecision === 'accepted' ? '接受' : '拒绝'}该输出？此操作只记录人工决定，不会直接写入正式题目或错题。
                        </p>
                        <div className='mt-2 flex gap-2'>
                          <button
                            type='button'
                            onClick={() => decide(pendingDecision)}
                            disabled={acting !== null}
                            className='rounded-lg bg-slate-900 px-3 py-1.5 text-xs text-white disabled:opacity-50'
                          >
                            {acting === pendingDecision ? '提交中…' : '确认提交'}
                          </button>
                          <button
                            type='button'
                            onClick={() => setPendingDecision(null)}
                            disabled={acting !== null}
                            className='rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-xs text-slate-600 disabled:opacity-50'
                          >
                            取消
                          </button>
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          )}
        </aside>
      </div>
    </section>
  )
}
