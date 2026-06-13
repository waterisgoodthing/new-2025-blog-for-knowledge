'use client'

import { useState, useMemo, useEffect } from 'react'
import Link from 'next/link'
import { Brain, Target, RefreshCw, BookOpen, Loader2, Copy, Check, FileText, ChevronRight } from 'lucide-react'
import { useWeakPoints } from '@/hooks/use-knowledge'
import { cn } from '@/lib/utils'
import { toast } from 'sonner'
import { generateVariant, generateKnowledgeCard } from '@/lib/api/ai'
import { Drawer } from '@/components/drawer'

type TimeRange = 7 | 30

interface WeakPointCluster {
  knowledge_point: string
  canonical_name?: string
  aliases?: string[]
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
  const [drawerOpen, setDrawerOpen] = useState(false)
  const [selectedCluster, setSelectedCluster] = useState<WeakPointCluster | null>(null)
  const { data, isLoading, error } = useWeakPoints(days)
  const [generatingVariant, setGeneratingVariant] = useState(false)
  const [generatingCard, setGeneratingCard] = useState(false)
  const [variantResult, setVariantResult] = useState<any>(null)
  const [cardResult, setCardResult] = useState<any>(null)
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

  const openDrawer = (cluster: WeakPointCluster) => {
    setSelectedCluster(cluster)
    setVariantResult(null)
    setCardResult(null)
    setDrawerOpen(true)
  }

  const handleGenerateVariant = async () => {
    if (!selectedCluster) return
    setGeneratingVariant(true)
    setVariantResult(null)
    try {
      const result = await generateVariant(selectedCluster.knowledge_point, selectedCluster.subject)
      setVariantResult(result)
    } catch (e: any) {
      toast.error('生成变式题失败: ' + (e.message || '未知错误'))
    } finally {
      setGeneratingVariant(false)
    }
  }

  const handleGenerateCard = async () => {
    if (!selectedCluster) return
    setGeneratingCard(true)
    setCardResult(null)
    try {
      const result = await generateKnowledgeCard(selectedCluster.knowledge_point, selectedCluster.subject)
      setCardResult(result)
    } catch (e: any) {
      toast.error('生成知识卡片失败: ' + (e.message || '未知错误'))
    } finally {
      setGeneratingCard(false)
    }
  }

  const topClusters = clusters.slice(0, 3)

  const [isMobile, setIsMobile] = useState(false)
  useEffect(() => {
    const check = () => setIsMobile(window.innerWidth < 768)
    check()
    window.addEventListener('resize', check)
    return () => window.removeEventListener('resize', check)
  }, [])

  const handleNavigateWithVariant = (data: any) => {
    if (!selectedCluster) return
    sessionStorage.setItem('ai_prefill_mistake', JSON.stringify({
      title: `变式题：${selectedCluster.knowledge_point}`,
      question: data.question,
      correct_answer: data.correct_answer,
      analysis: data.analysis,
      knowledge_points: data.knowledge_points,
      subject: selectedCluster.subject || data.subject,
      difficulty: data.difficulty,
    }))
    window.open('/write-mistake?ai_prefill=1', '_blank')
  }

  const handleNavigateWithCard = (data: any) => {
    if (!selectedCluster) return
    sessionStorage.setItem('ai_prefill_note', JSON.stringify({
      title: data.title,
      content: data.content,
      knowledge_points: data.knowledge_points,
      subject: selectedCluster.subject || data.subject,
    }))
    window.open('/write-note?ai_prefill=1', '_blank')
  }

  return (
    <>
      <div className='rounded-2xl border border-white/40 bg-white/60 backdrop-blur-sm'>
        <div className='flex items-center justify-between border-b border-white/20 px-5 py-4'>
          <div className='flex items-center gap-2'>
            <Brain className='h-5 w-5 text-[var(--color-brand)]' />
            <h2 className='font-medium'>薄弱点诊断</h2>
            {data && <span className='text-xs text-gray-400'>近{days}天 · {clusters.length}个</span>}
          </div>
          <div className='flex gap-1'>
            {([7, 30] as TimeRange[]).map(d => (
              <button
                key={d}
                onClick={() => { setDays(d); setDrawerOpen(false) }}
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
            <div className='py-6 text-center text-sm text-gray-400'>诊断中...</div>
          ) : error ? (
            <div className='py-6 text-center text-sm text-gray-400'>诊断数据暂时不可用</div>
          ) : clusters.length === 0 ? (
            <div className='py-6 text-center'>
              <Target className='mx-auto mb-2 h-8 w-8 text-gray-300' />
              <p className='text-sm text-gray-400'>暂无薄弱点数据</p>
            </div>
          ) : (
            <div className='space-y-2'>
              {topClusters.map((cluster, idx) => (
                <button
                  key={idx}
                  onClick={() => openDrawer(cluster)}
                  className={cn(
                    'flex w-full items-center gap-3 rounded-xl border p-3 text-left transition-colors hover:ring-1 hover:ring-[var(--color-brand)]/20',
                    SEVERITY_COLORS[cluster.severity]
                  )}
                >
                  <div className='min-w-0 flex-1'>
                    <div className='flex flex-wrap items-center gap-2'>
                      <span className='text-sm font-medium'>{cluster.canonical_name || cluster.knowledge_point}</span>
                      {cluster.subject && (
                        <span className='rounded bg-purple-500/10 px-1.5 py-0.5 text-[10px] text-purple-600'>{cluster.subject}</span>
                      )}
                    </div>
                    <div className='mt-1 flex flex-wrap gap-1.5 text-[11px]'>
                      <span className='text-red-600'>{cluster.mistake_count} 道错题</span>
                      {cluster.due_review_count > 0 && <span className='text-orange-600'>· {cluster.due_review_count} 待复习</span>}
                    </div>
                  </div>
                  <ChevronRight size={16} className='shrink-0 text-gray-400' />
                </button>
              ))}
              {clusters.length > 3 && (
                <button
                  onClick={() => { setSelectedCluster(null); setDrawerOpen(true) }}
                  className='w-full rounded-lg py-2 text-center text-xs text-gray-400 hover:text-gray-600'
                >
                  查看全部 {clusters.length} 个薄弱点
                </button>
              )}
            </div>
          )}
        </div>
      </div>

      <Drawer
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        title={selectedCluster ? (selectedCluster.canonical_name || selectedCluster.knowledge_point) : '薄弱点诊断'}
        side={isMobile ? 'bottom' : 'right'}
      >
        <div className='p-5'>
          {selectedCluster ? (
            <div className='space-y-4'>
              <div className={cn('rounded-xl border p-3', SEVERITY_COLORS[selectedCluster.severity])}>
                <div className='flex flex-wrap items-center gap-2 text-sm'>
                  <span className='font-medium'>{selectedCluster.canonical_name || selectedCluster.knowledge_point}</span>
                  <span className='rounded px-1.5 py-0.5 text-xs'>严重度: {SEVERITY_LABELS[selectedCluster.severity]}</span>
                </div>
                {selectedCluster.aliases && selectedCluster.aliases.length > 0 && (
                  <div className='mt-1.5 flex flex-wrap gap-1'>
                    {selectedCluster.aliases.map((alias, i) => (
                      <span key={i} className='rounded-full bg-white/40 px-2 py-0.5 text-[10px] text-gray-500'>{alias}</span>
                    ))}
                  </div>
                )}
                <div className='mt-2 flex flex-wrap gap-2 text-xs'>
                  <span className='rounded bg-red-500/10 px-2 py-0.5 text-red-600'>{selectedCluster.mistake_count} 道错题</span>
                  {selectedCluster.due_review_count > 0 && (
                    <span className='rounded bg-orange-500/10 px-2 py-0.5 text-orange-600'>{selectedCluster.due_review_count} 待复习</span>
                  )}
                  {selectedCluster.recent_error_count > 0 && (
                    <span className='rounded bg-amber-500/10 px-2 py-0.5 text-amber-600'>近期 {selectedCluster.recent_error_count} 次</span>
                  )}
                </div>
              </div>

              {selectedCluster.evidence_sources.length > 0 && (
                <div>
                  <div className='mb-2 text-xs font-medium text-gray-500'>相关错题</div>
                  <div className='flex flex-wrap gap-1.5'>
                    {selectedCluster.evidence_sources.map((src, j) => (
                      src.slug ? (
                        <Link
                          key={j}
                          href={`/notes/${src.slug}`}
                          onClick={() => setDrawerOpen(false)}
                          className='rounded-lg bg-blue-500/10 px-2.5 py-1.5 text-xs text-blue-600 hover:bg-blue-500/20'
                        >
                          {src.title || src.slug}
                        </Link>
                      ) : (
                        <span key={j} className='rounded-lg bg-blue-500/10 px-2.5 py-1.5 text-xs text-blue-600'>{src.title}</span>
                      )
                    ))}
                  </div>
                </div>
              )}

              {selectedCluster.top_error_reasons.length > 0 && (
                <div className='rounded-lg bg-white/40 p-3'>
                  <div className='mb-1.5 text-xs font-medium text-gray-500'>高频错误模式</div>
                  <div className='space-y-1'>
                    {selectedCluster.top_error_reasons.map((reason, j) => (
                      <div key={j} className='flex items-start gap-2 text-xs text-gray-600'>
                        <span className='mt-0.5 h-1.5 w-1.5 shrink-0 rounded-full bg-amber-400' />
                        {reason}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {variantResult && (
                <div className='rounded-lg border border-purple-200/50 bg-purple-50/30 p-3'>
                  <div className='mb-2 flex items-center justify-between'>
                    <span className='text-xs font-medium text-purple-600'>AI 生成的变式题</span>
                    <div className='flex gap-1'>
                      <button onClick={() => handleCopy(`题目: ${variantResult.question}\n答案: ${variantResult.correct_answer}`, 'variant')} className='rounded p-1 text-gray-400 hover:text-purple-600' aria-label='复制变式题'>
                        {copiedField === 'variant' ? <Check size={14} /> : <Copy size={14} />}
                      </button>
                      <button onClick={() => handleNavigateWithVariant(variantResult)} className='rounded p-1 text-gray-400 hover:text-purple-600' aria-label='创建为错题'>
                        <FileText size={14} />
                      </button>
                    </div>
                  </div>
                  <div className='space-y-2 text-sm'>
                    <div><span className='font-medium text-gray-700'>题目:</span><p className='mt-0.5 text-gray-600 whitespace-pre-wrap'>{variantResult.question}</p></div>
                    <div><span className='font-medium text-gray-700'>答案:</span><p className='mt-0.5 text-gray-600 whitespace-pre-wrap'>{variantResult.correct_answer}</p></div>
                  </div>
                  <button onClick={() => handleNavigateWithVariant(variantResult)} className='mt-2 w-full rounded-lg bg-purple-500/10 px-3 py-1.5 text-xs text-purple-600 hover:bg-purple-500/20'>
                    保存为错题记录
                  </button>
                </div>
              )}

              {cardResult && (
                <div className='rounded-lg border border-blue-200/50 bg-blue-50/30 p-3'>
                  <div className='mb-2 flex items-center justify-between'>
                    <span className='text-xs font-medium text-blue-600'>AI 生成的知识卡片</span>
                    <div className='flex gap-1'>
                      <button onClick={() => handleCopy(`# ${cardResult.title}\n\n${cardResult.content}`, 'card')} className='rounded p-1 text-gray-400 hover:text-blue-600' aria-label='复制知识卡片'>
                        {copiedField === 'card' ? <Check size={14} /> : <Copy size={14} />}
                      </button>
                      <button onClick={() => handleNavigateWithCard(cardResult)} className='rounded p-1 text-gray-400 hover:text-blue-600' aria-label='创建为笔记'>
                        <FileText size={14} />
                      </button>
                    </div>
                  </div>
                  <div className='text-sm font-medium text-gray-700'>{cardResult.title}</div>
                  <p className='mt-1 text-sm text-gray-600 whitespace-pre-wrap'>{cardResult.content}</p>
                  <button onClick={() => handleNavigateWithCard(cardResult)} className='mt-2 w-full rounded-lg bg-blue-500/10 px-3 py-1.5 text-xs text-blue-600 hover:bg-blue-500/20'>
                    保存为知识笔记
                  </button>
                </div>
              )}

              <div className='flex flex-wrap gap-2'>
                <Link
                  href='/mistakes/review'
                  onClick={() => setDrawerOpen(false)}
                  className='inline-flex items-center gap-1.5 rounded-lg bg-[var(--color-brand)] px-3 py-1.5 text-xs text-white'
                >
                  <RefreshCw size={12} /> 开始复习
                </Link>
                <button
                  className='inline-flex items-center gap-1.5 rounded-lg bg-purple-500/10 px-3 py-1.5 text-xs text-purple-600 hover:bg-purple-500/20 disabled:opacity-50'
                  onClick={handleGenerateVariant}
                  disabled={generatingVariant}
                >
                  {generatingVariant ? <Loader2 size={12} className='animate-spin' /> : <Brain size={12} />}
                  {generatingVariant ? '生成中...' : 'AI 生成变式题'}
                </button>
                <button
                  className='inline-flex items-center gap-1.5 rounded-lg bg-blue-500/10 px-3 py-1.5 text-xs text-blue-600 hover:bg-blue-500/20 disabled:opacity-50'
                  onClick={handleGenerateCard}
                  disabled={generatingCard}
                >
                  {generatingCard ? <Loader2 size={12} className='animate-spin' /> : <BookOpen size={12} />}
                  {generatingCard ? '生成中...' : 'AI 生成知识卡片'}
                </button>
              </div>
            </div>
          ) : (
            <div className='space-y-2'>
              {clusters.map((cluster, idx) => (
                <button
                  key={idx}
                  onClick={() => setSelectedCluster(cluster)}
                  className={cn(
                    'flex w-full items-center gap-3 rounded-xl border p-3 text-left transition-colors hover:ring-1 hover:ring-[var(--color-brand)]/20',
                    SEVERITY_COLORS[cluster.severity]
                  )}
                >
                  <div className='min-w-0 flex-1'>
                    <div className='flex flex-wrap items-center gap-2'>
                      <span className='text-sm font-medium'>{cluster.canonical_name || cluster.knowledge_point}</span>
                      {cluster.subject && <span className='rounded bg-purple-500/10 px-1.5 py-0.5 text-[10px] text-purple-600'>{cluster.subject}</span>}
                    </div>
                    <div className='mt-1 flex flex-wrap gap-1.5 text-[11px]'>
                      <span className='text-red-600'>{cluster.mistake_count} 道错题</span>
                      {cluster.due_review_count > 0 && <span className='text-orange-600'>· {cluster.due_review_count} 待复习</span>}
                    </div>
                  </div>
                  <ChevronRight size={16} className='shrink-0 text-gray-400' />
                </button>
              ))}
            </div>
          )}
        </div>
      </Drawer>
    </>
  )
}
