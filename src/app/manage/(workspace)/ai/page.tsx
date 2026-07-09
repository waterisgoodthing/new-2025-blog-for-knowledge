'use client'

import { useState, useEffect, useCallback } from 'react'
import Link from 'next/link'
import { toast } from 'sonner'
import { ManagePageHeader } from '../../components/manage-page-header'
import {
  getCallLogs,
  getCallLogStats,
  getProviderHealthSnapshot,
  getProviderStatus,
  getUsageCostStats,
  type AiCallLogEntry,
  type AiCallLogStatsItem,
  type AiProviderHealthSnapshotItem,
  type AiProviderStatusItem,
  type AiUsageCostStatsItem,
} from '@/lib/api/ai'

const PAGE_SIZE = 20

function formatPercent(value: number) {
  return `${(value * 100).toFixed(1)}%`
}

function formatLatency(value: number) {
  return `${Math.round(value)}ms`
}

function formatUnknownNumber(value: number | null) {
  return value === null ? 'unknown' : value.toLocaleString('zh-CN')
}

function formatUnknownCost(value: string | number | null, currency: string | null) {
  if (value === null) return 'unknown'
  return `${value}${currency ? ` ${currency}` : ''}`
}

function healthBadgeClass(status: string) {
  if (status === 'healthy') return 'bg-green-500/10 text-green-600'
  if (status === 'degraded') return 'bg-amber-500/10 text-amber-600'
  return 'bg-slate-500/10 text-slate-500'
}

export default function ManageAiPage() {
  const [logs, setLogs] = useState<AiCallLogEntry[]>([])
  const [stats, setStats] = useState<AiCallLogStatsItem[]>([])
  const [providerStatus, setProviderStatus] = useState<AiProviderStatusItem[]>([])
  const [usageCostStats, setUsageCostStats] = useState<AiUsageCostStatsItem[]>([])
  const [healthSnapshot, setHealthSnapshot] = useState<AiProviderHealthSnapshotItem[]>([])
  const [loading, setLoading] = useState(true)
  const [filterTaskType, setFilterTaskType] = useState('')
  const [filterSuccess, setFilterSuccess] = useState('')
  const [offset, setOffset] = useState(0)

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const successParam = filterSuccess === '' ? undefined : filterSuccess === 'success'
      const [logsData, statsData, providerStatusData, usageCostData, healthSnapshotData] = await Promise.all([
        getCallLogs({
          task_type: filterTaskType || undefined,
          success: successParam,
          limit: PAGE_SIZE,
          offset,
        }),
        getCallLogStats(),
        getProviderStatus(),
        getUsageCostStats(),
        getProviderHealthSnapshot(),
      ])
      setLogs(logsData)
      setStats(statsData.items)
      setProviderStatus(providerStatusData)
      setUsageCostStats(usageCostData.items)
      setHealthSnapshot(healthSnapshotData.items)
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : String(e)
      toast.error('加载 AI 治理数据失败: ' + msg)
    } finally {
      setLoading(false)
    }
  }, [filterTaskType, filterSuccess, offset])

  useEffect(() => {
    load()
  }, [load])

  const handleFilterChange = (taskType: string, success: string) => {
    setFilterTaskType(taskType)
    setFilterSuccess(success)
    setOffset(0)
  }

  const taskTypes = stats.map(s => s.task_type)

  return (
    <div className='space-y-8'>
      <ManagePageHeader
        eyebrow='Batch 11 · AI Run Audit'
        title='AI 控制台'
        description='业务 Run 审计与技术调用日志保持双轨，人工决定不会直接写入正式内容。'
      />

      <section className='flex flex-wrap items-center justify-between gap-4 rounded-2xl border border-white/45 bg-white/55 p-5'>
        <div>
          <h2 className='font-medium text-slate-800'>业务 Run 审计</h2>
          <p className='mt-1 text-sm text-slate-500'>查看受控输出，并完成人工接受、拒绝与重试。</p>
        </div>
        <Link
          href='/manage/ai/runs'
          className='rounded-lg bg-slate-900 px-4 py-2 text-sm text-white transition hover:bg-slate-700'
        >
          打开 Run 审计页
        </Link>
      </section>

      <section aria-labelledby='governance-title' className='space-y-4'>
        <div className='flex flex-wrap items-end justify-between gap-4 border-b border-white/55 pb-3'>
          <div>
            <h2 id='governance-title' className='font-medium text-slate-800'>Provider / Routing / Usage 只读治理</h2>
            <p className='mt-1 text-xs text-slate-500'>
              面板只展示配置状态与基于 ai_call_logs 的观测快照；不提供在线编辑，不执行真实 provider health probe。
            </p>
          </div>
          <span className='rounded-full bg-slate-900/5 px-3 py-1 text-xs text-slate-500'>Read-only</span>
        </div>

        <div className='grid grid-cols-1 gap-4 xl:grid-cols-3'>
          <div className='rounded-2xl border border-white/40 bg-white/60 p-4'>
            <div className='flex items-center justify-between gap-3'>
              <h3 className='text-sm font-medium text-slate-800'>Provider 状态</h3>
              <span className='text-xs text-slate-400'>{providerStatus.length} 个配置项</span>
            </div>
            {loading ? (
              <p className='py-8 text-center text-sm text-slate-400'>加载中...</p>
            ) : providerStatus.length === 0 ? (
              <p className='py-8 text-center text-sm text-slate-400'>暂无 provider 配置状态</p>
            ) : (
              <div className='mt-4 space-y-3'>
                {providerStatus.map(provider => (
                  <div key={`${provider.name}-${provider.role}`} className='rounded-xl bg-white/55 p-3'>
                    <div className='flex items-start justify-between gap-3'>
                      <div className='min-w-0'>
                        <p className='font-mono text-xs font-medium text-slate-700'>{provider.name}</p>
                        <p className='mt-1 truncate font-mono text-xs text-slate-500'>{provider.model}</p>
                      </div>
                      <span className={`rounded-full px-2 py-0.5 text-xs ${provider.configured ? 'bg-green-500/10 text-green-600' : 'bg-slate-500/10 text-slate-500'}`}>
                        {provider.configured ? 'configured' : 'not configured'}
                      </span>
                    </div>
                    <div className='mt-3 grid grid-cols-2 gap-2 text-xs text-slate-500'>
                      <span>角色：{provider.role}</span>
                      <span className='truncate'>Base URL：{provider.base_url_label}</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className='rounded-2xl border border-white/40 bg-white/60 p-4 xl:col-span-2'>
            <div className='flex items-center justify-between gap-3'>
              <h3 className='text-sm font-medium text-slate-800'>Health Snapshot</h3>
              <span className='text-xs text-slate-400'>最近技术调用事实，不等同真实探针</span>
            </div>
            {loading ? (
              <p className='py-8 text-center text-sm text-slate-400'>加载中...</p>
            ) : healthSnapshot.length === 0 ? (
              <p className='py-8 text-center text-sm text-slate-400'>暂无可聚合的 health snapshot</p>
            ) : (
              <div className='mt-4 overflow-x-auto'>
                <table className='w-full text-left text-sm'>
                  <thead>
                    <tr className='border-b border-white/40 text-xs text-slate-400'>
                      <th className='py-2 pr-4 font-medium'>Provider</th>
                      <th className='py-2 pr-4 font-medium'>Model</th>
                      <th className='py-2 pr-4 font-medium'>状态</th>
                      <th className='py-2 pr-4 font-medium'>调用</th>
                      <th className='py-2 pr-4 font-medium'>失败率</th>
                      <th className='py-2 pr-4 font-medium'>Fallback</th>
                      <th className='py-2 pr-4 font-medium'>平均延迟</th>
                      <th className='py-2 font-medium'>原因</th>
                    </tr>
                  </thead>
                  <tbody>
                    {healthSnapshot.map(item => (
                      <tr key={`${item.provider}-${item.model}`} className='border-b border-white/30 hover:bg-white/30'>
                        <td className='py-2.5 pr-4 font-mono text-xs text-slate-700'>{item.provider}</td>
                        <td className='py-2.5 pr-4 font-mono text-xs text-slate-600'>{item.model}</td>
                        <td className='py-2.5 pr-4'>
                          <span className={`inline-block rounded-full px-2 py-0.5 text-xs ${healthBadgeClass(item.status)}`}>
                            {item.status}
                          </span>
                        </td>
                        <td className='py-2.5 pr-4 font-mono text-xs text-slate-600'>{item.call_count}</td>
                        <td className='py-2.5 pr-4 font-mono text-xs text-slate-600'>{formatPercent(item.failure_rate)}</td>
                        <td className='py-2.5 pr-4 font-mono text-xs text-slate-600'>{formatPercent(item.fallback_rate)}</td>
                        <td className='py-2.5 pr-4 font-mono text-xs text-slate-600'>{formatLatency(item.avg_latency_ms)}</td>
                        <td className='py-2.5 text-xs text-slate-500'>
                          <span className='block max-w-[240px] truncate' title={`${item.source}: ${item.reason}`}>
                            {item.reason}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>

        <div className='rounded-2xl border border-white/40 bg-white/60 p-4'>
          <div className='flex flex-wrap items-center justify-between gap-3'>
            <div>
              <h3 className='text-sm font-medium text-slate-800'>Usage / Cost Snapshot</h3>
              <p className='mt-1 text-xs text-slate-500'>
                token usage 与 cost 当前只展示真实返回值；unknown 表示 provider 未返回或未记录，不代表 0，也不是精确账单。
              </p>
            </div>
            <span className='rounded-full bg-amber-500/10 px-3 py-1 text-xs text-amber-700'>Not billing data</span>
          </div>
          {loading ? (
            <p className='py-8 text-center text-sm text-slate-400'>加载中...</p>
          ) : usageCostStats.length === 0 ? (
            <p className='py-8 text-center text-sm text-slate-400'>暂无 usage / cost 聚合记录</p>
          ) : (
            <div className='mt-4 overflow-x-auto'>
              <table className='w-full text-left text-sm'>
                <thead>
                  <tr className='border-b border-white/40 text-xs text-slate-400'>
                    <th className='py-2 pr-4 font-medium'>日期</th>
                    <th className='py-2 pr-4 font-medium'>任务类型</th>
                    <th className='py-2 pr-4 font-medium'>Provider</th>
                    <th className='py-2 pr-4 font-medium'>Model</th>
                    <th className='py-2 pr-4 font-medium'>调用</th>
                    <th className='py-2 pr-4 font-medium'>成功 / 失败</th>
                    <th className='py-2 pr-4 font-medium'>Fallback</th>
                    <th className='py-2 pr-4 font-medium'>延迟</th>
                    <th className='py-2 pr-4 font-medium'>Tokens</th>
                    <th className='py-2 font-medium'>Estimated Cost</th>
                  </tr>
                </thead>
                <tbody>
                  {usageCostStats.map(item => (
                    <tr key={`${item.date}-${item.task_type}-${item.provider}-${item.model}`} className='border-b border-white/30 hover:bg-white/30'>
                      <td className='py-2.5 pr-4 font-mono text-xs text-slate-600'>{item.date}</td>
                      <td className='py-2.5 pr-4 font-mono text-xs text-slate-700'>{item.task_type}</td>
                      <td className='py-2.5 pr-4 text-xs text-slate-600'>{item.provider}</td>
                      <td className='py-2.5 pr-4 font-mono text-xs text-slate-600'>{item.model}</td>
                      <td className='py-2.5 pr-4 font-mono text-xs text-slate-600'>{item.call_count}</td>
                      <td className='py-2.5 pr-4 font-mono text-xs text-slate-600'>{item.success_count} / {item.failure_count}</td>
                      <td className='py-2.5 pr-4 font-mono text-xs text-slate-600'>{item.fallback_count}</td>
                      <td className='py-2.5 pr-4 font-mono text-xs text-slate-600'>{formatLatency(item.avg_latency_ms)}</td>
                      <td className='py-2.5 pr-4 font-mono text-xs text-slate-600'>
                        in {formatUnknownNumber(item.input_tokens)} / out {formatUnknownNumber(item.output_tokens)}
                      </td>
                      <td className='py-2.5 font-mono text-xs text-slate-600'>
                        {formatUnknownCost(item.estimated_cost, item.currency)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </section>

      {/* 统计卡片 */}
      <section aria-labelledby='stats-title'>
        <div className='flex items-end justify-between gap-4 border-b border-white/55 pb-3'>
          <h2 id='stats-title' className='font-medium text-slate-800'>调用统计（按任务类型）</h2>
          <span className='text-xs text-slate-400'>{stats.length} 种任务类型</span>
        </div>
        {stats.length === 0 ? (
          <p className='py-8 text-center text-sm text-slate-400'>暂无调用记录</p>
        ) : (
          <div className='grid grid-cols-1 gap-4 py-5 sm:grid-cols-2 lg:grid-cols-3'>
            {stats.map(s => {
              const successRate = s.total > 0 ? ((s.success_count / s.total) * 100).toFixed(1) : '0.0'
              return (
                <div key={s.task_type} className='rounded-2xl border border-white/40 bg-white/60 p-4 backdrop-blur-sm'>
                  <div className='flex items-center justify-between'>
                    <span className='font-mono text-sm font-medium text-slate-700'>{s.task_type}</span>
                    <span className='text-xs text-slate-400'>{s.total} 次</span>
                  </div>
                  <div className='mt-3 flex items-center gap-4 text-xs'>
                    <div>
                      <span className='text-slate-400'>成功率</span>
                      <span className={`ml-1 font-medium ${Number(successRate) >= 80 ? 'text-green-600' : Number(successRate) >= 50 ? 'text-amber-600' : 'text-red-600'}`}>
                        {successRate}%
                      </span>
                    </div>
                    <div>
                      <span className='text-slate-400'>成功</span>
                      <span className='ml-1 font-medium text-green-600'>{s.success_count}</span>
                    </div>
                    <div>
                      <span className='text-slate-400'>平均延迟</span>
                      <span className='ml-1 font-mono text-slate-700'>{Math.round(s.avg_latency_ms)}ms</span>
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </section>

      {/* 过滤栏 */}
      <section aria-labelledby='logs-title'>
        <div className='flex flex-wrap items-end justify-between gap-4 border-b border-white/55 pb-3'>
          <h2 id='logs-title' className='font-medium text-slate-800'>调用日志</h2>
          <div className='flex items-center gap-3'>
            <label className='flex items-center gap-2 text-xs text-slate-500'>
              <span>任务类型</span>
              <select
                value={filterTaskType}
                onChange={e => handleFilterChange(e.target.value, filterSuccess)}
                className='rounded-lg border border-white/40 bg-white/60 px-2 py-1 text-sm outline-none focus:border-[var(--color-brand)]'
              >
                <option value=''>全部</option>
                {taskTypes.map(t => (
                  <option key={t} value={t}>{t}</option>
                ))}
              </select>
            </label>
            <label className='flex items-center gap-2 text-xs text-slate-500'>
              <span>状态</span>
              <select
                value={filterSuccess}
                onChange={e => handleFilterChange(filterTaskType, e.target.value)}
                className='rounded-lg border border-white/40 bg-white/60 px-2 py-1 text-sm outline-none focus:border-[var(--color-brand)]'
              >
                <option value=''>全部</option>
                <option value='success'>成功</option>
                <option value='fail'>失败</option>
              </select>
            </label>
            <button
              onClick={load}
              disabled={loading}
              className='rounded-lg bg-[var(--color-brand)]/10 px-3 py-1 text-xs text-[var(--color-brand)] hover:bg-[var(--color-brand)]/20 disabled:opacity-50'
            >
              {loading ? '加载中...' : '刷新'}
            </button>
          </div>
        </div>

        {/* 日志表格 */}
        {loading ? (
          <div className='py-20 text-center text-sm text-slate-400'>加载中...</div>
        ) : logs.length === 0 ? (
          <div className='py-20 text-center text-sm text-slate-400'>暂无日志记录</div>
        ) : (
          <div className='overflow-x-auto py-4'>
            <table className='w-full text-left text-sm'>
              <thead>
                <tr className='border-b border-white/40 text-xs text-slate-400'>
                  <th className='py-2 pr-4 font-medium'>时间</th>
                  <th className='py-2 pr-4 font-medium'>任务类型</th>
                  <th className='py-2 pr-4 font-medium'>Provider</th>
                  <th className='py-2 pr-4 font-medium'>Model</th>
                  <th className='py-2 pr-4 font-medium'>延迟</th>
                  <th className='py-2 pr-4 font-medium'>状态</th>
                  <th className='py-2 pr-4 font-medium'>Fallback</th>
                  <th className='py-2 font-medium'>错误</th>
                </tr>
              </thead>
              <tbody>
                {logs.map(log => (
                  <tr key={log.id} className='border-b border-white/30 hover:bg-white/30'>
                    <td className='py-2.5 pr-4 text-xs text-slate-500'>
                      {new Date(log.created_at).toLocaleString('zh-CN', { hour12: false })}
                    </td>
                    <td className='py-2.5 pr-4 font-mono text-xs text-slate-700'>{log.task_type}</td>
                    <td className='py-2.5 pr-4 text-xs text-slate-600'>{log.provider_used}</td>
                    <td className='py-2.5 pr-4 font-mono text-xs text-slate-600'>{log.model}</td>
                    <td className='py-2.5 pr-4 font-mono text-xs text-slate-600'>{log.latency_ms}ms</td>
                    <td className='py-2.5 pr-4'>
                      <span className={`inline-block rounded-full px-2 py-0.5 text-xs ${log.success ? 'bg-green-500/10 text-green-600' : 'bg-red-500/10 text-red-600'}`}>
                        {log.success ? '成功' : '失败'}
                      </span>
                    </td>
                    <td className='py-2.5 pr-4'>
                      {log.fallback_used ? (
                        <span className='text-xs text-amber-600'>是</span>
                      ) : (
                        <span className='text-xs text-slate-300'>否</span>
                      )}
                    </td>
                    <td className='py-2.5 text-xs text-red-500'>
                      {log.error ? (
                        <span className='block max-w-[200px] truncate' title={log.error}>{log.error}</span>
                      ) : (
                        <span className='text-slate-300'>—</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* 分页 */}
        {!loading && logs.length > 0 && (
          <div className='flex items-center justify-between pt-4'>
            <span className='text-xs text-slate-400'>
              第 {offset + 1}–{offset + logs.length} 条
            </span>
            <div className='flex items-center gap-2'>
              <button
                onClick={() => setOffset(Math.max(0, offset - PAGE_SIZE))}
                disabled={offset === 0}
                className='rounded-lg bg-white/60 px-3 py-1 text-xs text-slate-500 hover:bg-white/80 disabled:opacity-30'
              >
                上一页
              </button>
              <button
                onClick={() => setOffset(offset + PAGE_SIZE)}
                disabled={logs.length < PAGE_SIZE}
                className='rounded-lg bg-white/60 px-3 py-1 text-xs text-slate-500 hover:bg-white/80 disabled:opacity-30'
              >
                下一页
              </button>
            </div>
          </div>
        )}
      </section>
    </div>
  )
}
