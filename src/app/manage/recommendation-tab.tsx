'use client'

import { useState, useEffect, useCallback } from 'react'
import { ChevronDown, ChevronRight, RefreshCw } from 'lucide-react'
import { EmptyState } from '@/components/empty-state'
import {
  getTodayRecommendation,
  deleteTodayRecommendation,
  getRecommendationHistory,
  type DailyRecommendation,
  type RecommendationHistoryItem,
} from '@/lib/api/recommendations'
import dayjs from 'dayjs'
import { toast } from 'sonner'

const TYPE_LABELS: Record<string, string> = {
  note: '笔记',
  mistake: '错题',
  review: '复习',
  resource: '资源',
  music: '音乐',
  podcast: '播客',
}

const TYPE_COLORS: Record<string, string> = {
  note: 'bg-blue-500/20 text-blue-600',
  mistake: 'bg-red-500/20 text-red-600',
  review: 'bg-orange-500/20 text-orange-600',
  resource: 'bg-green-500/20 text-green-600',
  music: 'bg-purple-500/20 text-purple-600',
  podcast: 'bg-pink-500/20 text-pink-600',
}

export function RecommendationTab() {
  const [today, setToday] = useState<DailyRecommendation | null>(null)
  const [history, setHistory] = useState<RecommendationHistoryItem[]>([])
  const [loading, setLoading] = useState(true)
  const [regenerating, setRegenerating] = useState(false)
  const [expandedId, setExpandedId] = useState<number | null>(null)

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const [todayData, historyData] = await Promise.all([
        getTodayRecommendation().catch(() => null),
        getRecommendationHistory().catch(() => []),
      ])
      setToday(todayData)
      setHistory(historyData)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    load()
  }, [load])

  const handleRegenerate = async () => {
    if (!confirm('确定重新生成今日推荐？当前推荐将被删除。')) return
    setRegenerating(true)
    try {
      await deleteTodayRecommendation()
      const newRec = await getTodayRecommendation()
      setToday(newRec)
      const historyData = await getRecommendationHistory()
      setHistory(historyData)
    } catch (e: any) {
      toast.error('重新生成失败: ' + e.message)
    } finally {
      setRegenerating(false)
    }
  }

  const toggleExpand = (id: number) => {
    setExpandedId((prev) => (prev === id ? null : id))
  }

  return (
    <div>
      <div className='mb-4 flex items-center justify-between'>
        <p className='text-secondary text-sm'>管理首页今日推荐卡片</p>
        <button
          onClick={handleRegenerate}
          disabled={regenerating}
          className='inline-flex items-center gap-1.5 rounded-xl bg-[var(--color-brand)] px-4 py-2 text-sm text-white transition-transform hover:scale-105 active:scale-95 disabled:opacity-50'
        >
          <RefreshCw className={`h-3.5 w-3.5 ${regenerating ? 'animate-spin' : ''}`} />
          {regenerating ? '生成中...' : '重新生成'}
        </button>
      </div>

      {loading ? (
        <div className='py-20 text-center text-gray-400'>加载中...</div>
      ) : (
        <>
          <div className='mb-6 rounded-xl border border-white/40 bg-white/60 p-5 backdrop-blur-sm'>
            <h3 className='mb-3 text-sm font-medium text-gray-500'>今日推荐</h3>
            {today ? (
              <div className='space-y-2'>
                <div className='flex items-center gap-2'>
                  <span className={`rounded-full px-2 py-0.5 text-xs ${TYPE_COLORS[today.type] || 'bg-gray-100 text-gray-500'}`}>
                    {TYPE_LABELS[today.type] || today.type}
                  </span>
                  <span className='truncate font-medium'>{today.title}</span>
                </div>
                <p className='text-secondary line-clamp-2 text-sm'>{today.reason}</p>
                <div className='flex items-center gap-3 text-xs text-gray-400'>
                  {today.target && <span>路径: {today.target}</span>}
                  {today.action_label && <span>按钮: {today.action_label}</span>}
                </div>
              </div>
            ) : (
              <p className='text-sm text-gray-400'>今日暂无推荐</p>
            )}
          </div>

          <h3 className='mb-3 text-sm font-medium text-gray-500'>推荐历史</h3>
          {history.length === 0 ? (
            <div className='py-10'><EmptyState variant='no-content' title='暂无历史记录' description='推荐历史会在这里显示' /></div>
          ) : (
            <div className='overflow-x-auto rounded-xl border border-white/40 bg-white/60 backdrop-blur-sm'>
              <table className='w-full text-sm'>
                <thead>
                  <tr className='border-b border-white/20 text-left text-xs text-gray-500'>
                    <th className='p-3'></th>
                    <th className='p-3'>日期</th>
                    <th className='p-3'>标题</th>
                    <th className='p-3'>类型</th>
                    <th className='p-3'>理由</th>
                  </tr>
                </thead>
                <tbody>
                  {history.map((item) => (
                    <>
                      <tr key={item.id} className='border-b border-white/10 hover:bg-white/40'>
                        <td className='p-3'>
                          <button onClick={() => toggleExpand(item.id)} className='text-gray-400 hover:text-gray-600'>
                            {expandedId === item.id ? <ChevronDown className='h-4 w-4' /> : <ChevronRight className='h-4 w-4' />}
                          </button>
                        </td>
                        <td className='whitespace-nowrap p-3 text-xs text-gray-500'>{dayjs(item.date).format('YYYY-MM-DD')}</td>
                        <td className='max-w-[200px] truncate p-3 font-medium'>{item.title}</td>
                        <td className='p-3'>
                          <span className={`rounded-full px-2 py-0.5 text-xs ${TYPE_COLORS[item.type] || 'bg-gray-100 text-gray-500'}`}>
                            {TYPE_LABELS[item.type] || item.type}
                          </span>
                        </td>
                        <td className='max-w-[250px] truncate p-3 text-gray-500'>{item.reason}</td>
                      </tr>
                      {expandedId === item.id && (
                        <tr key={`${item.id}-ctx`}>
                          <td colSpan={5} className='border-b border-white/10 bg-white/30 px-6 py-3'>
                            <p className='mb-1 text-xs font-medium text-gray-500'>推荐上下文：</p>
                            <pre className='max-h-40 overflow-auto whitespace-pre-wrap rounded-lg bg-white/40 p-3 font-mono text-xs text-gray-600'>
                              {item.raw_context || '无上下文数据'}
                            </pre>
                          </td>
                        </tr>
                      )}
                    </>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </>
      )}
    </div>
  )
}
