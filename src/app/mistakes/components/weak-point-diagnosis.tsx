'use client'

import { useState, useMemo } from 'react'
import Link from 'next/link'
import { motion, AnimatePresence } from 'motion/react'
import { ChevronDown, ChevronRight, BookOpen, RefreshCw, Brain, Target, AlertTriangle, FileText, Loader2, Copy, Check } from 'lucide-react'
import { useWeakPoints } from '@/hooks/use-knowledge'
import { cn } from '@/lib/utils'
import { toast } from 'sonner'
import { generateVariant, generateKnowledgeCard } from '@/lib/api/ai'

type TimeRange = 7 | 30

interface WeakPointCluster {
  knowledge_point: string
  subject: string
  severity: 'high' | 'medium' | 'low'
  mistake_count: number
  due_review_count: number
  recent_error_count: number
  top_error_reasons: string[]
  evidence_sources: { slug?: string; title?: string }[]
}

const SEVERITY_COLORS = {
  high: 'bg-red-500/15 text-red-600 border-red-200/50',
  medium: 'bg-yellow-500/15 text-yellow-600 border-yellow-200/50',
  low: 'bg-green-500/15 text-green-600 border-green-200/50',
}

const SEVERITY_LABELS = {
  high: '高',
  medium: '中',
  low: '低',
}

export function WeakPointDiagnosis() {
  const [days, setDays] = useState<TimeRange>(30)
  const [expandedIdx, setExpandedIdx] = useState<number | null>(null)
  const { data, isLoading, error } = useWeakPoints(days)
  const [generatingVariant, setGeneratingVariant] = useState<number | null>(null)
  const [generatingCard, setGeneratingCard] = useState<number | null>(null)
  const [variantResult, setVariantResult] = useState<{ idx: number; data: any } | null>(null)
  const [cardResult, setCardResult] = useState<{ idx: number; data: any } | null>(null)
  const [copiedField, setCopiedField] = useState<string | null>(null)

  const clusters = useMemo(() => {
    if (!data?.weak_points) return []
    return data.weak_points.map(wp => {
      let severity: 'high' | 'medium' | 'low' = 'low'
      if (wp.mistake_count >= 5 || wp.due_review_count >= 3) severity = 'high'
      else if (wp.mistake_count >= 3 || wp.due_review_count >= 2) severity = 'medium'
      return { ...wp, severity }
    }).sort((a, b) => {
      const sev = { high: 3, medium: 2, low: 1 }
      return (sev[b.severity] - sev[a.severity]) || (b.mistake_count - a.mistake_count)
    })
  }, [data])

  const handleCopy = (text: string, field: string) => {
    navigator.clipboard.writeText(text)
    setCopiedField(field)
    toast.success('已复制到剪贴板')
    setTimeout(() => setCopiedField(null), 2000)
  }

  const handleGenerateVariant = async (idx: number, cluster: WeakPointCluster) => {
    setGeneratingVariant(idx)
    setVariantResult(null)
    try {
      const result = await generateVariant(cluster.knowledge_point, cluster.subject)
      setVariantResult({ idx, data: result })
    } catch (e: any) {
      toast.error('生成变式题失败: ' + (e.message || '未知错误'))
    } finally {
      setGeneratingVariant(null)
    }
  }

  const handleGenerateCard = async (idx: number, cluster: WeakPointCluster) => {
    setGeneratingCard(idx)
    setCardResult(null)
    try {
      const result = await generateKnowledgeCard(cluster.knowledge_point, cluster.subject)
      setCardResult({ idx, data: result })
    } catch (e: any) {
      toast.error('生成知识卡片失败: ' + (e.message || '未知错误'))
    } finally {
      setGeneratingCard(null)
    }
  }

  const handleNavigateWithVariant = (data: any, cluster: WeakPointCluster) => {
    sessionStorage.setItem('ai_prefill_mistake', JSON.stringify({
      title: `变式题：${cluster.knowledge_point}`,
      question: data.question,
      correct_answer: data.correct_answer,
      analysis: data.analysis,
      knowledge_points: data.knowledge_points,
      subject: cluster.subject || data.subject,
      difficulty: data.difficulty,
    }))
    window.open('/write-mistake?ai_prefill=1', '_blank')
  }

  const handleNavigateWithCard = (data: any, cluster: WeakPointCluster) => {
    sessionStorage.setItem('ai_prefill_note', JSON.stringify({
      title: data.title,
      content: data.content,
      knowledge_points: data.knowledge_points,
      subject: cluster.subject || data.subject,
    }))
    window.open('/write-note?ai_prefill=1', '_blank')
  }

  return (
    <div className='rounded-2xl border border-white/40 bg-white/60 backdrop-blur-sm'>
      <div className='flex items-center justify-between border-b border-white/20 px-5 py-4'>
        <div className='flex items-center gap-2'>
          <Brain className='h-5 w-5 text-[var(--color-brand)]' />
          <h2 className='font-medium'>薄弱点诊断</h2>
          {data && <span className='text-xs text-gray-400'>近{days}天 · {clusters.length}个薄弱点</span>}
        </div>
        <div className='flex gap-1'>
          {([7, 30] as TimeRange[]).map(d => (
            <button
              key={d}
              onClick={() => { setDays(d); setExpandedIdx(null) }}
              className={cn(
                'rounded-lg px-3 py-1 text-xs transition-colors',
                days === d ? 'bg-[var(--color-brand)] text-white' : 'bg-white/60 text-gray-500 hover:bg-white/80'
              )}
            >
              {d}天
            </button>
          ))}
        </div>
      </div>

      <div className='p-5'>
        {isLoading ? (
          <div className='py-10 text-center text-sm text-gray-400'>诊断中...</div>
        ) : error ? (
          <div className='py-10 text-center text-sm text-gray-400'>诊断数据暂时不可用</div>
        ) : clusters.length === 0 ? (
          <div className='py-10 text-center'>
            <Target className='mx-auto mb-2 h-10 w-10 text-gray-300' />
            <p className='text-sm text-gray-400'>暂无薄弱点数据</p>
            <p className='text-xs text-gray-300'>记录更多错题后会自动生成诊断</p>
          </div>
        ) : (
          <div className='space-y-3'>
            {clusters.map((cluster, idx) => (
              <div
                key={idx}
                className={cn(
                  'overflow-hidden rounded-xl border transition-colors',
                  SEVERITY_COLORS[cluster.severity],
                  expandedIdx === idx && 'ring-1 ring-[var(--color-brand)]/20'
                )}
              >
                <button
                  onClick={() => setExpandedIdx(expandedIdx === idx ? null : idx)}
                  className='flex w-full items-start gap-3 p-4 text-left'
                >
                  <div className='mt-0.5 shrink-0'>
                    {expandedIdx === idx ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
                  </div>
                  <div className='min-w-0 flex-1'>
                    <div className='flex flex-wrap items-center gap-2'>
                      <span className='font-medium'>{cluster.knowledge_point}</span>
                      {cluster.subject && (
                        <span className='rounded bg-purple-500/10 px-1.5 py-0.5 text-xs text-purple-600'>{cluster.subject}</span>
                      )}
                      <span className={cn('rounded px-1.5 py-0.5 text-xs', SEVERITY_COLORS[cluster.severity])}>
                        严重度: {SEVERITY_LABELS[cluster.severity]}
                      </span>
                    </div>
                    <div className='mt-2 flex flex-wrap gap-2 text-xs'>
                      <span className='rounded bg-red-500/10 px-2 py-0.5 text-red-600'>{cluster.mistake_count} 道错题</span>
                      {cluster.due_review_count > 0 && (
                        <span className='rounded bg-orange-500/10 px-2 py-0.5 text-orange-600'>{cluster.due_review_count} 待复习</span>
                      )}
                      {cluster.recent_error_count > 0 && (
                        <span className='rounded bg-amber-500/10 px-2 py-0.5 text-amber-600'>近期 {cluster.recent_error_count} 次</span>
                      )}
                    </div>
                    {cluster.top_error_reasons.length > 0 && (
                      <div className='mt-2 flex flex-wrap gap-1'>
                        {cluster.top_error_reasons.slice(0, 3).map((reason, j) => (
                          <span key={j} className='rounded-full bg-gray-200/60 px-2 py-0.5 text-[11px] text-gray-600'>{reason}</span>
                        ))}
                      </div>
                    )}
                  </div>
                </button>

                <AnimatePresence>
                  {expandedIdx === idx && (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: 'auto', opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      transition={{ duration: 0.2 }}
                      className='overflow-hidden'
                    >
                      <div className='border-t border-white/20 px-4 pb-4 pt-3'>
                        {cluster.evidence_sources.length > 0 && (
                          <div className='mb-3'>
                            <div className='mb-1.5 text-xs font-medium text-gray-500'>相关错题</div>
                            <div className='flex flex-wrap gap-1.5'>
                              {cluster.evidence_sources.map((src, j) => (
                                src.slug ? (
                                  <Link
                                    key={j}
                                    href={`/notes/${src.slug}`}
                                    className='rounded-lg bg-blue-500/10 px-2 py-1 text-xs text-blue-600 hover:bg-blue-500/20'
                                  >
                                    {src.title || src.slug}
                                  </Link>
                                ) : (
                                  <span key={j} className='rounded-lg bg-blue-500/10 px-2 py-1 text-xs text-blue-600'>{src.title}</span>
                                )
                              ))}
                            </div>
                          </div>
                        )}

                        <div className='mb-3 rounded-lg bg-white/40 p-3'>
                          <div className='mb-1 text-xs font-medium text-gray-500'>AI 诊断</div>
                          <p className='text-sm text-gray-600'>
                            {cluster.top_error_reasons.length > 0
                              ? `主要错误类型: ${cluster.top_error_reasons[0]}。建议针对此知识点进行专项练习。`
                              : '暂无足够数据生成详细诊断。'
                            }
                          </p>
                        </div>

                        {variantResult?.idx === idx && variantResult.data && (
                          <div className='mb-3 rounded-lg border border-purple-200/50 bg-purple-50/30 p-3'>
                            <div className='mb-2 flex items-center justify-between'>
                              <span className='text-xs font-medium text-purple-600'>AI 生成的变式题</span>
                              <div className='flex gap-1'>
                                <button
                                  onClick={() => handleCopy(
                                    `题目: ${variantResult.data.question}\n答案: ${variantResult.data.correct_answer}\n解析: ${variantResult.data.analysis}`,
                                    'variant'
                                  )}
                                  className='rounded p-1 text-gray-400 hover:text-purple-600'
                                  aria-label='复制变式题'
                                >
                                  {copiedField === 'variant' ? <Check size={14} /> : <Copy size={14} />}
                                </button>
                                <button
                                  onClick={() => handleNavigateWithVariant(variantResult.data, cluster)}
                                  className='rounded p-1 text-gray-400 hover:text-purple-600'
                                  aria-label='创建为错题'
                                >
                                  <FileText size={14} />
                                </button>
                              </div>
                            </div>
                            <div className='space-y-2 text-sm'>
                              <div>
                                <span className='font-medium text-gray-700'>题目:</span>
                                <p className='mt-0.5 text-gray-600 whitespace-pre-wrap'>{variantResult.data.question}</p>
                              </div>
                              <div>
                                <span className='font-medium text-gray-700'>答案:</span>
                                <p className='mt-0.5 text-gray-600 whitespace-pre-wrap'>{variantResult.data.correct_answer}</p>
                              </div>
                              <div>
                                <span className='font-medium text-gray-700'>解析:</span>
                                <p className='mt-0.5 text-gray-600 whitespace-pre-wrap'>{variantResult.data.analysis}</p>
                              </div>
                            </div>
                            <button
                              onClick={() => handleNavigateWithVariant(variantResult.data, cluster)}
                              className='mt-2 w-full rounded-lg bg-purple-500/10 px-3 py-1.5 text-xs text-purple-600 hover:bg-purple-500/20'
                            >
                              保存为错题记录
                            </button>
                          </div>
                        )}

                        {cardResult?.idx === idx && cardResult.data && (
                          <div className='mb-3 rounded-lg border border-blue-200/50 bg-blue-50/30 p-3'>
                            <div className='mb-2 flex items-center justify-between'>
                              <span className='text-xs font-medium text-blue-600'>AI 生成的知识卡片</span>
                              <div className='flex gap-1'>
                                <button
                                  onClick={() => handleCopy(
                                    `# ${cardResult.data.title}\n\n${cardResult.data.content}`,
                                    'card'
                                  )}
                                  className='rounded p-1 text-gray-400 hover:text-blue-600'
                                  aria-label='复制知识卡片'
                                >
                                  {copiedField === 'card' ? <Check size={14} /> : <Copy size={14} />}
                                </button>
                                <button
                                  onClick={() => handleNavigateWithCard(cardResult.data, cluster)}
                                  className='rounded p-1 text-gray-400 hover:text-blue-600'
                                  aria-label='创建为笔记'
                                >
                                  <FileText size={14} />
                                </button>
                              </div>
                            </div>
                            <div className='space-y-2 text-sm'>
                              <div className='font-medium text-gray-700'>{cardResult.data.title}</div>
                              <p className='text-gray-600 whitespace-pre-wrap'>{cardResult.data.content}</p>
                            </div>
                            <button
                              onClick={() => handleNavigateWithCard(cardResult.data, cluster)}
                              className='mt-2 w-full rounded-lg bg-blue-500/10 px-3 py-1.5 text-xs text-blue-600 hover:bg-blue-500/20'
                            >
                              保存为知识笔记
                            </button>
                          </div>
                        )}

                        <div className='flex flex-wrap gap-2'>
                          <Link
                            href='/mistakes/review'
                            className='inline-flex items-center gap-1.5 rounded-lg bg-[var(--color-brand)] px-3 py-1.5 text-xs text-white'
                          >
                            <RefreshCw size={12} />
                            开始复习
                          </Link>
                          <button
                            className='inline-flex items-center gap-1.5 rounded-lg bg-purple-500/10 px-3 py-1.5 text-xs text-purple-600 hover:bg-purple-500/20 disabled:opacity-50'
                            onClick={() => handleGenerateVariant(idx, cluster)}
                            disabled={generatingVariant === idx}
                          >
                            {generatingVariant === idx ? (
                              <Loader2 size={12} className='animate-spin' />
                            ) : (
                              <Brain size={12} />
                            )}
                            {generatingVariant === idx ? '生成中...' : 'AI 生成变式题'}
                          </button>
                          <button
                            className='inline-flex items-center gap-1.5 rounded-lg bg-blue-500/10 px-3 py-1.5 text-xs text-blue-600 hover:bg-blue-500/20 disabled:opacity-50'
                            onClick={() => handleGenerateCard(idx, cluster)}
                            disabled={generatingCard === idx}
                          >
                            {generatingCard === idx ? (
                              <Loader2 size={12} className='animate-spin' />
                            ) : (
                              <BookOpen size={12} />
                            )}
                            {generatingCard === idx ? '生成中...' : 'AI 生成知识卡片'}
                          </button>
                          <button
                            className='inline-flex items-center gap-1.5 rounded-lg bg-green-500/10 px-3 py-1.5 text-xs text-green-600 hover:bg-green-500/20'
                            onClick={() => {
                              const plan = `薄弱点补救计划\n知识点: ${cluster.knowledge_point}\n科目: ${cluster.subject || '未知'}\n错题数: ${cluster.mistake_count}\n严重度: ${SEVERITY_LABELS[cluster.severity]}\n主要错误: ${cluster.top_error_reasons.join(', ')}\n\n行动:\n1. 复习相关错题\n2. 针对性练习\n3. 生成变式题巩固`
                              navigator.clipboard.writeText(plan)
                              toast.success('补救计划已复制到剪贴板')
                            }}
                          >
                            <Target size={12} />
                            保存补救计划
                          </button>
                          <button
                            className='inline-flex items-center gap-1.5 rounded-lg bg-white/60 px-3 py-1.5 text-xs text-gray-600 hover:bg-white/80'
                            onClick={() => {
                              navigator.clipboard.writeText(cluster.knowledge_point)
                              toast.success('知识点已复制')
                            }}
                          >
                            <FileText size={12} />
                            复制知识点
                          </button>
                        </div>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
