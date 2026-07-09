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
} from '@/lib/api/ai-runs'

const PAGE_SIZE = 20

const statusLabel: Record<AiRunStatus, string> = {
  running: '运行中',
  succeeded: '成功',
  failed: '失败',
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
      toast.error(error instanceof Error ? error.message : '加载 AI Runs 失败')
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
      toast.error(error instanceof Error ? error.message : '加载 Run 详情失败')
    }
  }

  const retry = async () => {
    if (!selected) return
    setActing('retry')
    try {
      const child = await retryAiRun(selected.id)
      toast.success(`已创建重试 attempt ${child.attempt}`)
      setSelected(child)
      await loadRuns()
    } catch (error) {
      if (error instanceof ApiError && error.status === 409) {
        toast.error('无法重试：该 Run 缺少 replay input。')
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
        toast.error('该 Run 已被更新，请刷新后重试。')
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
      <div className='flex flex-wrap items-end justify-between gap-4 border-b border-white/55 pb-3'>
        <div>
          <h2 id='runs-title' className='font-medium text-slate-800'>业务审计 Runs</h2>
          <p className='mt-1 text-xs text-slate-400'>人工接受只确认输出，不会直接写入正式题目、错题或复习项。</p>
        </div>
        <div className='flex gap-2'>
          <select
            aria-label='Run 状态'
            value={status}
            onChange={event => changeStatus(event.target.value as AiRunStatus | '')}
            className='rounded-lg border border-white/40 bg-white/60 px-2 py-1 text-xs'
          >
            <option value=''>全部状态</option>
            <option value='running'>运行中</option>
            <option value='succeeded'>成功</option>
            <option value='failed'>失败</option>
          </select>
          <select
            aria-label='人工审核状态'
            value={reviewStatus}
            onChange={event => changeReviewStatus(event.target.value as AiRunReviewStatus | '')}
            className='rounded-lg border border-white/40 bg-white/60 px-2 py-1 text-xs'
          >
            <option value=''>全部审核状态</option>
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
            <p className='py-12 text-center text-sm text-slate-400'>加载中…</p>
          ) : runs.length === 0 ? (
            <p className='py-12 text-center text-sm text-slate-400'>暂无符合条件的 Run</p>
          ) : (
            <table className='w-full text-left text-sm' data-testid='ai-runs-table'>
              <thead className='border-b border-white/40 text-xs text-slate-400'>
                <tr>
                  <th className='py-2 pr-3 font-medium'>时间</th>
                  <th className='py-2 pr-3 font-medium'>任务</th>
                  <th className='py-2 pr-3 font-medium'>运行</th>
                  <th className='py-2 pr-3 font-medium'>校验</th>
                  <th className='py-2 font-medium'>人工状态</th>
                </tr>
              </thead>
              <tbody>
                {runs.map(run => (
                  <tr
                    key={run.id}
                    data-run-id={run.id}
                    className='cursor-pointer border-b border-white/30 hover:bg-white/30'
                    onClick={() => openRun(run.id)}
                  >
                    <td className='py-2.5 pr-3 text-xs text-slate-500'>{new Date(run.created_at).toLocaleString('zh-CN', { hour12: false })}</td>
                    <td className='py-2.5 pr-3 font-mono text-xs text-slate-700'>{run.task_type}</td>
                    <td className='py-2.5 pr-3 text-xs'>{statusLabel[run.status]}</td>
                    <td className='py-2.5 pr-3 text-xs text-slate-500'>{run.validation_status}</td>
                    <td className='py-2.5 text-xs text-slate-500'>{run.review_status}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
          <div className='mt-3 flex items-center justify-between border-t border-white/45 pt-3 text-xs text-slate-500'>
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

        <aside aria-label='AI Run 详情' className='border-l border-white/45 pl-5'>
          {!selected ? (
            <p className='py-12 text-sm text-slate-400'>选择一条 Run 查看受控详情。</p>
          ) : (
            <div className='space-y-4'>
              <div>
                <p className='font-mono text-xs text-slate-400'>{selected.id}</p>
                <h3 className='mt-1 font-medium text-slate-800'>{selected.task_type}</h3>
                <p className='mt-1 text-xs text-slate-500'>
                  attempt {selected.attempt} · {selected.provider_used || '未选择 provider'} · {selected.prompt_version || '无 Prompt 版本'}
                </p>
              </div>
              <div>
                <h4 className='text-xs font-medium text-slate-500'>受控输出</h4>
                <pre className='mt-1 max-h-72 overflow-auto whitespace-pre-wrap rounded-xl bg-slate-950/90 p-3 text-xs text-slate-100'>
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
                        onChange={event => setRejectNote(event.target.value)}
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
                        className='rounded-xl border border-amber-200 bg-amber-50/80 p-3'
                      >
                        <p className='text-xs leading-5 text-amber-900'>
                          确认{pendingDecision === 'accepted' ? '接受' : '拒绝'}该 AI 输出？此操作只记录人工决定，不会直接写入正式题目或错题。
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
