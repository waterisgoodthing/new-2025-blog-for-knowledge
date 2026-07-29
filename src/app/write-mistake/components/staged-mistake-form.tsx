'use client'

import { useState, useRef } from 'react'
import { useRouter } from 'next/navigation'
import { createNote, uploadImage } from '@/lib/api/notes'
import {
  generateQuestionDraft,
  confirmQuestionDraft,
  generateErrorInterpretation,
  rejectErrorInterpretation,
  generateFinalAnalysis,
  generateDiagram,
  type QuestionDraftResponse,
  type ErrorInterpretationResponse,
  type FinalAnalysisResponse,
  type DiagramResponse,
  type ImageInput,
} from '@/lib/api/ai'
import { toast } from 'sonner'
import { cn } from '@/lib/utils'
import { getContentDetailHref } from '@/lib/content-routes'
import { resolveImageUrl } from '@/lib/api/images'
import Link from 'next/link'
import {
  ArrowLeft,
  Check,
  ChevronRight,
  ClipboardPaste,
  FileQuestion,
  FileText,
  ImageUp,
  Loader2,
  Pencil,
  RefreshCw,
  Save,
  Sparkles,
  X,
  XCircle,
} from 'lucide-react'

function StructuredGraphDiagram({ nodes, edges }: { nodes: { id: string; label: string; highlighted?: boolean; annotation?: string }[]; edges: { source: string; target: string; label?: string; highlighted?: boolean; weight?: string }[] }) {
  const nodeMap = new Map(nodes.map((n, i) => [n.id, { ...n, index: i }]))
  const cols = Math.ceil(Math.sqrt(nodes.length))
  const cellW = 140
  const cellH = 80
  const pad = 40
  const w = cols * cellW + pad * 2
  const rows = Math.ceil(nodes.length / cols)
  const h = rows * cellH + pad * 2

  const getNodePos = (idx: number) => ({
    x: pad + (idx % cols) * cellW + cellW / 2,
    y: pad + Math.floor(idx / cols) * cellH + cellH / 2,
  })

  return (
    <svg viewBox={`0 0 ${w} ${h}`} className="w-full max-w-lg" role="img" aria-label="结构化图解">
      <defs>
        <marker id="arrow" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
          <path d="M 0 0 L 10 5 L 0 10 z" fill="#94a3b8" />
        </marker>
      </defs>
      {edges.map((e, i) => {
        const si = nodeMap.get(e.source)?.index ?? 0
        const ti = nodeMap.get(e.target)?.index ?? 0
        const sp = getNodePos(si)
        const tp = getNodePos(ti)
        const color = e.highlighted ? '#f59e0b' : '#94a3b8'
        return (
          <g key={i}>
            <line x1={sp.x} y1={sp.y} x2={tp.x} y2={tp.y} stroke={color} strokeWidth={e.highlighted ? 2.5 : 1.5} markerEnd="url(#arrow)" />
            {(e.label || e.weight) && (
              <text x={(sp.x + tp.x) / 2} y={(sp.y + tp.y) / 2 - 6} textAnchor="middle" className="text-[10px] fill-slate-600">
                {e.label || e.weight}
              </text>
            )}
          </g>
        )
      })}
      {nodes.map((n, i) => {
        const p = getNodePos(i)
        const fill = n.highlighted ? '#fef3c7' : '#f8fafc'
        const stroke = n.highlighted ? '#f59e0b' : '#cbd5e1'
        return (
          <g key={n.id}>
            <rect x={p.x - 45} y={p.y - 18} width={90} height={36} rx={8} fill={fill} stroke={stroke} strokeWidth={n.highlighted ? 2 : 1} />
            <text x={p.x} y={p.y + 1} textAnchor="middle" dominantBaseline="middle" className={cn('text-[11px] font-medium', n.highlighted ? 'fill-amber-800' : 'fill-slate-700')}>
              {n.label.length > 10 ? n.label.slice(0, 10) + '…' : n.label}
            </text>
            {n.annotation && (
              <text x={p.x} y={p.y + 28} textAnchor="middle" className="text-[9px] fill-amber-600">
                {n.annotation.length > 16 ? n.annotation.slice(0, 16) + '…' : n.annotation}
              </text>
            )}
          </g>
        )
      })}
    </svg>
  )
}

type Stage =
  | 'source'
  | 'draft_review'
  | 'error_reason'
  | 'interpreting'
  | 'interpretation_review'
  | 'analyzing'
  | 'analysis_done'
  | 'diagramming'
  | 'done'

interface UploadedImage {
  base64: string
  mime_type: string
  preview: string
}

export function StagedMistakeForm() {
  const router = useRouter()
  const fileInputRef = useRef<HTMLInputElement>(null)

  const [stage, setStage] = useState<Stage>('source')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [saving, setSaving] = useState(false)

  // Source stage
  const [images, setImages] = useState<UploadedImage[]>([])
  const [pasteText, setPasteText] = useState('')

  // Draft stage
  const [draft, setDraft] = useState<QuestionDraftResponse | null>(null)
  const [draftEditing, setDraftEditing] = useState(false)
  const [draftForm, setDraftForm] = useState<QuestionDraftResponse | null>(null)

  // Error reason stage
  const [userErrorReason, setUserErrorReason] = useState('')

  // Interpretation stage
  const [interpretation, setInterpretation] = useState<ErrorInterpretationResponse | null>(null)
  const [rejectionHistory, setRejectionHistory] = useState<string[]>([])
  const [showRejection, setShowRejection] = useState(false)
  const [rejectionReason, setRejectionReason] = useState('')

  // Final analysis stage
  const [finalAnalysis, setFinalAnalysis] = useState<FinalAnalysisResponse | null>(null)

  // Diagram stage
  const [diagram, setDiagram] = useState<DiagramResponse | null>(null)

  // Saving fields
  const [title, setTitle] = useState('')
  const [subject, setSubject] = useState('')
  const [difficulty, setDifficulty] = useState<'easy' | 'medium' | 'hard'>('medium')
  const [tags, setTags] = useState<string[]>([])
  const [tagInput, setTagInput] = useState('')

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    if (!files?.length) return

    const newImages: UploadedImage[] = []
    for (const file of Array.from(files)) {
      const reader = new FileReader()
      const result = await new Promise<string>((resolve) => {
        reader.onload = () => resolve(reader.result as string)
        reader.readAsDataURL(file)
      })
      const base64 = result.split(',')[1]
      newImages.push({
        base64,
        mime_type: file.type,
        preview: result,
      })
    }
    setImages(prev => [...prev, ...newImages])
  }

  const removeImage = (index: number) => {
    setImages(prev => prev.filter((_, i) => i !== index))
  }

  // Stage 1: Generate question draft
  const handleGenerateDraft = async () => {
    if (!images.length && !pasteText.trim()) {
      setError('请上传图片或粘贴题目文本')
      return
    }

    setLoading(true)
    setError(null)

    try {
      const imageInputs: ImageInput[] = images.map(img => ({
        base64: img.base64,
        mime_type: img.mime_type,
      }))

      const result = await generateQuestionDraft(imageInputs, pasteText)
      setDraft(result)
      setDraftForm(result)
      setTitle(result.title)
      setSubject(result.subject)
      setDifficulty(result.difficulty as 'easy' | 'medium' | 'hard')
      setTags(result.tags)
      setStage('draft_review')
    } catch (err: any) {
      setError(err.message || '识别题目失败')
    } finally {
      setLoading(false)
    }
  }

  // Stage 2: Confirm draft
  const handleConfirmDraft = async () => {
    if (!draftForm) return

    setLoading(true)
    try {
      await confirmQuestionDraft(draftForm)
      setDraft(draftForm)
      setStage('error_reason')
    } catch (err: any) {
      setError(err.message || '确认题目失败')
    } finally {
      setLoading(false)
    }
  }

  // Stage 3: Generate error interpretation
  const handleGenerateInterpretation = async () => {
    if (!draft || !userErrorReason.trim()) {
      setError('请填写你的错因')
      return
    }

    setStage('interpreting')
    setLoading(true)
    setError(null)

    try {
      const result = await generateErrorInterpretation(draft, userErrorReason, rejectionHistory)
      setInterpretation(result)
      setStage('interpretation_review')
    } catch (err: any) {
      setError(err.message || '生成错因理解失败')
      setStage('error_reason')
    } finally {
      setLoading(false)
    }
  }

  // Stage 4a: Accept interpretation
  const handleAcceptInterpretation = () => {
    setStage('analysis_done')
  }

  // Stage 4b: Reject interpretation
  const handleRejectInterpretation = async () => {
    if (!draft || !interpretation || !rejectionReason.trim()) {
      setError('请填写拒绝理由')
      return
    }

    setLoading(true)
    setError(null)

    try {
      const updatedHistory = [...rejectionHistory, rejectionReason]
      const result = await rejectErrorInterpretation(
        draft,
        userErrorReason,
        interpretation,
        rejectionReason,
        rejectionHistory
      )
      setInterpretation(result)
      setRejectionHistory(updatedHistory)
      setShowRejection(false)
      setRejectionReason('')
      setStage('interpretation_review')
    } catch (err: any) {
      setError(err.message || '重新生成失败')
    } finally {
      setLoading(false)
    }
  }

  // Stage 5: Generate final analysis
  const handleGenerateAnalysis = async () => {
    if (!draft || !interpretation) return

    setLoading(true)
    setError(null)

    try {
      const result = await generateFinalAnalysis(draft, userErrorReason, interpretation)
      setFinalAnalysis(result)
    } catch (err: any) {
      setError(err.message || '生成解析失败')
    } finally {
      setLoading(false)
    }
  }

  // Stage 6: Generate diagram
  const handleGenerateDiagram = async () => {
    if (!draft || !interpretation || !finalAnalysis) return

    setStage('diagramming')
    setLoading(true)
    setError(null)

    try {
      const result = await generateDiagram(draft, interpretation, finalAnalysis)
      setDiagram(result)
      setStage('done')
    } catch (err: any) {
      setError(err.message || '生成图解失败')
      setStage('analysis_done')
    } finally {
      setLoading(false)
    }
  }

  // Stage 7: Save
  const handleSave = async () => {
    if (!draft) return

    setSaving(true)
    try {
      // Upload images
      const uploadedUrls: string[] = []
      for (const img of images) {
        const blob = await fetch(img.preview).then(r => r.blob())
        const file = new File([blob], 'image.jpg', { type: img.mime_type })
        const result = await uploadImage(file)
        uploadedUrls.push(result.url)
      }

      // Build content markdown
      let content = `## 题目\n\n${draft.question}\n\n`
      if (draft.options.length) {
        content += `**选项：**\n${draft.options.map((o, i) => `${String.fromCharCode(65 + i)}. ${o}`).join('\n')}\n\n`
      }
      if (userErrorReason) content += `## 我的错因\n\n${userErrorReason}\n\n`
      if (interpretation) {
        content += `## AI 错因理解\n\n**概括：** ${interpretation.summary}\n\n**诊断：** ${interpretation.diagnosis}\n\n**根本原因：** ${interpretation.root_cause}\n\n`
      }
      if (finalAnalysis) {
        content += `## 解析\n\n${finalAnalysis.analysis}\n\n`
        if (finalAnalysis.key_step) content += `**关键步骤：** ${finalAnalysis.key_step}\n\n`
        if (finalAnalysis.similar_traps.length) content += `**相似陷阱：**\n${finalAnalysis.similar_traps.map(t => `- ${t}`).join('\n')}\n\n`
        if (finalAnalysis.generalization) content += `**举一反三：** ${finalAnalysis.generalization}\n\n`
        if (finalAnalysis.review_advice) content += `**复习建议：** ${finalAnalysis.review_advice}\n\n`
      }

      const aiMetadata: Record<string, unknown> = {
        question_ai_draft: draft,
        question_draft_status: 'confirmed',
        user_error_reason: userErrorReason,
        ai_error_interpretation: interpretation ? {
          id: interpretation.interpretation_id,
          version: interpretation.version,
          summary: interpretation.summary,
          diagnosis: interpretation.diagnosis,
          root_cause: interpretation.root_cause,
          knowledge_gap: interpretation.knowledge_gap,
          suggested_correction: interpretation.suggested_correction,
          reasoning_trace: interpretation.reasoning_trace,
        } : null,
        error_interpretation_status: interpretation ? 'accepted' : null,
        final_analysis: finalAnalysis ? {
          analysis: finalAnalysis.analysis,
          error_reason: finalAnalysis.error_reason,
          key_step: finalAnalysis.key_step,
          similar_traps: finalAnalysis.similar_traps,
          generalization: finalAnalysis.generalization,
          review_advice: finalAnalysis.review_advice,
          variant_questions: finalAnalysis.variant_questions,
          accepted_interpretation_id: finalAnalysis.accepted_interpretation_id,
          accepted_interpretation_version: finalAnalysis.accepted_interpretation_version,
        } : null,
        diagram: diagram ? {
          strategy: diagram.strategy,
          strategy_reason: diagram.strategy_reason,
          structured_data: diagram.structured_data,
          image_url: diagram.image_url,
          image_prompt: diagram.image_prompt,
          accepted_interpretation_id: diagram.accepted_interpretation_id,
          accepted_interpretation_version: diagram.accepted_interpretation_version,
          uses_error_interpretation: diagram.uses_error_interpretation,
        } : null,
        diagrams: diagram?.strategy === 'structured' && diagram.structured_data?.mermaid
          ? [{ type: 'flowchart', title: diagram.structured_data.title, mermaid: diagram.structured_data.mermaid }]
          : [],
        visual_context: draft.visual_context,
        image_dependency: draft.image_dependency,
      }

      const slugBase = (title || draft.title || 'mistake')
        .toLowerCase()
        .replace(/[^a-z0-9\u4e00-\u9fff]+/g, '-')
        .replace(/^-|-$/g, '')
        .slice(0, 50)
      const slug = `${slugBase}-${Date.now().toString(36)}`

      await createNote({
        slug,
        type: 'mistake',
        title: title || draft.title,
        content,
        question: draft.question,
        my_answer: userErrorReason,
        correct_answer: draft.candidate_answer,
        analysis: finalAnalysis?.analysis || '',
        knowledge_points: draft.knowledge_points,
        subject: subject || draft.subject,
        difficulty,
        tags,
        images: uploadedUrls,
        ai_metadata: aiMetadata,
      })

      toast.success('错题已保存')
      router.push('/mistakes')
    } catch (err: any) {
      setError(err.message || '保存失败')
    } finally {
      setSaving(false)
    }
  }

  const stageOrder: Stage[] = ['source', 'draft_review', 'error_reason', 'interpreting', 'interpretation_review', 'analysis_done', 'diagramming', 'done']
  const currentStageIndex = stageOrder.indexOf(stage)

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="flex items-center gap-3 mb-8">
        <Link href="/mistakes" className="text-muted-foreground hover:text-foreground">
          <ArrowLeft className="w-5 h-5" />
        </Link>
        <h1 className="text-2xl font-bold">记录错题</h1>
      </div>

      {/* Progress indicator */}
      <div className="flex items-center gap-1 mb-8 overflow-x-auto pb-2">
        {[
          { key: 'source', label: '识别题目' },
          { key: 'draft_review', label: '确认题目' },
          { key: 'error_reason', label: '填写错因' },
          { key: 'interpretation_review', label: 'AI 理解错因' },
          { key: 'analysis_done', label: '生成解析' },
          { key: 'done', label: '生成图解' },
        ].map((s, i) => {
          const stageIdx = stageOrder.indexOf(s.key as Stage)
          const isActive = stageIdx === currentStageIndex
          const isComplete = stageIdx < currentStageIndex
          return (
            <div key={s.key} className="flex items-center">
              <div
                className={cn(
                  'flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium whitespace-nowrap',
                  isActive && 'bg-primary text-primary-foreground',
                  isComplete && 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400',
                  !isActive && !isComplete && 'bg-muted text-muted-foreground'
                )}
              >
                {isComplete ? <Check className="w-3 h-3" /> : <span>{i + 1}</span>}
                <span>{s.label}</span>
              </div>
              {i < 5 && <ChevronRight className="w-4 h-4 text-muted-foreground mx-1 shrink-0" />}
            </div>
          )
        })}
      </div>

      {/* Error display */}
      {error && (
        <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg text-red-700 dark:text-red-400 text-sm">
          {error}
          <button onClick={() => setError(null)} className="ml-2 underline">关闭</button>
        </div>
      )}

      {/* Stage: Source */}
      {stage === 'source' && (
        <div className="space-y-6">
          <div className="bg-card border rounded-xl p-6">
            <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <FileQuestion className="w-5 h-5" />
              题目来源
            </h2>

            {/* Image upload */}
            <div className="mb-4">
              <div
                className="border-2 border-dashed rounded-lg p-8 text-center cursor-pointer hover:border-primary/50 transition-colors"
                onClick={() => fileInputRef.current?.click()}
              >
                <ImageUp className="w-8 h-8 mx-auto mb-2 text-muted-foreground" />
                <p className="text-sm text-muted-foreground">点击上传错题图片</p>
                <p className="text-xs text-muted-foreground mt-1">支持 JPG、PNG 等格式</p>
              </div>
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                multiple
                className="hidden"
                onChange={handleFileSelect}
              />
            </div>

            {/* Image previews */}
            {images.length > 0 && (
              <div className="flex gap-3 mb-4 overflow-x-auto pb-2">
                {images.map((img, i) => (
                  <div key={i} className="relative shrink-0">
                    <img src={img.preview} alt={`图片 ${i + 1}`} className="h-24 rounded-lg object-cover" />
                    <button
                      onClick={() => removeImage(i)}
                      className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full w-5 h-5 flex items-center justify-center"
                    >
                      <X className="w-3 h-3" />
                    </button>
                  </div>
                ))}
              </div>
            )}

            {/* Text input */}
            <div className="mb-4">
              <label className="block text-sm font-medium mb-2">
                <ClipboardPaste className="w-4 h-4 inline mr-1" />
                或粘贴题目文本
              </label>
              <textarea
                value={pasteText}
                onChange={e => setPasteText(e.target.value)}
                placeholder="粘贴题目内容..."
                className="w-full h-32 px-3 py-2 border rounded-lg bg-background resize-none text-sm"
              />
            </div>

            <button
              onClick={handleGenerateDraft}
              disabled={loading || (!images.length && !pasteText.trim())}
              className="w-full py-3 bg-primary text-primary-foreground rounded-lg font-medium disabled:opacity-50 flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  正在识别题目...
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4" />
                  识别题目
                </>
              )}
            </button>
          </div>
        </div>
      )}

      {/* Stage: Draft Review */}
      {stage === 'draft_review' && draftForm && (
        <div className="space-y-6">
          <div className="bg-card border rounded-xl p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold flex items-center gap-2">
                <FileText className="w-5 h-5" />
                AI 识别结果
              </h2>
              <button
                onClick={() => setDraftEditing(!draftEditing)}
                className="text-sm text-primary flex items-center gap-1"
              >
                <Pencil className="w-3 h-3" />
                {draftEditing ? '完成编辑' : '编辑'}
              </button>
            </div>

            <div className="space-y-4">
              {/* Title */}
              <div>
                <label className="block text-xs font-medium text-muted-foreground mb-1">标题</label>
                {draftEditing ? (
                  <input
                    value={draftForm.title}
                    onChange={e => setDraftForm({ ...draftForm, title: e.target.value })}
                    className="w-full px-3 py-2 border rounded-lg bg-background text-sm"
                  />
                ) : (
                  <p className="text-sm font-medium">{draftForm.title}</p>
                )}
              </div>

              {/* Question */}
              <div>
                <label className="block text-xs font-medium text-muted-foreground mb-1">题目内容</label>
                {draftEditing ? (
                  <textarea
                    value={draftForm.question}
                    onChange={e => setDraftForm({ ...draftForm, question: e.target.value })}
                    className="w-full h-24 px-3 py-2 border rounded-lg bg-background resize-none text-sm"
                  />
                ) : (
                  <p className="text-sm whitespace-pre-wrap">{draftForm.question}</p>
                )}
              </div>

              {/* Options */}
              {draftForm.options.length > 0 && (
                <div>
                  <label className="block text-xs font-medium text-muted-foreground mb-1">选项</label>
                  {draftEditing ? (
                    <div className="space-y-2">
                      {draftForm.options.map((opt, i) => (
                        <div key={i} className="flex gap-2">
                          <span className="text-sm font-medium pt-2">{String.fromCharCode(65 + i)}.</span>
                          <input
                            value={opt}
                            onChange={e => {
                              const newOpts = [...draftForm.options]
                              newOpts[i] = e.target.value
                              setDraftForm({ ...draftForm, options: newOpts })
                            }}
                            className="flex-1 px-3 py-1.5 border rounded bg-background text-sm"
                          />
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="space-y-1">
                      {draftForm.options.map((opt, i) => (
                        <p key={i} className="text-sm">{String.fromCharCode(65 + i)}. {opt}</p>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {/* Visual context */}
              {draftForm.visual_context && (
                <div>
                  <label className="block text-xs font-medium text-muted-foreground mb-1">视觉上下文</label>
                  <p className="text-sm text-muted-foreground bg-muted/50 p-3 rounded-lg">{draftForm.visual_context}</p>
                </div>
              )}

              {/* Key conditions */}
              {draftForm.key_conditions.length > 0 && (
                <div>
                  <label className="block text-xs font-medium text-muted-foreground mb-1">关键条件</label>
                  <ul className="list-disc list-inside text-sm">
                    {draftForm.key_conditions.map((c, i) => <li key={i}>{c}</li>)}
                  </ul>
                </div>
              )}

              {/* Meta info */}
              <div className="flex flex-wrap gap-3 text-xs text-muted-foreground">
                {draftForm.subject && <span className="bg-muted px-2 py-1 rounded">{draftForm.subject}</span>}
                {draftForm.knowledge_points && <span className="bg-muted px-2 py-1 rounded">{draftForm.knowledge_points}</span>}
                {draftForm.difficulty && <span className="bg-muted px-2 py-1 rounded">{draftForm.difficulty}</span>}
                {draftForm.question_type && <span className="bg-muted px-2 py-1 rounded">{draftForm.question_type}</span>}
              </div>
            </div>

            <div className="flex gap-3 mt-6">
              <button
                onClick={() => { setStage('source'); setDraft(null); }}
                className="px-4 py-2 border rounded-lg text-sm"
              >
                返回
              </button>
              <button
                onClick={handleConfirmDraft}
                disabled={loading}
                className="flex-1 py-2 bg-primary text-primary-foreground rounded-lg font-medium disabled:opacity-50 flex items-center justify-center gap-2"
              >
                <Check className="w-4 h-4" />
                确认题目
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Stage: Error Reason */}
      {stage === 'error_reason' && (
        <div className="space-y-6">
          <div className="bg-card border rounded-xl p-6">
            <h2 className="text-lg font-semibold mb-4">我的错因</h2>
            <p className="text-sm text-muted-foreground mb-4">
              当时为什么做错了？请如实写下你的思考过程。
            </p>

            <textarea
              value={userErrorReason}
              onChange={e => setUserErrorReason(e.target.value)}
              placeholder="例如：没有结合 cost 来看，只按 TTL/跳数判断了。"
              className="w-full h-32 px-3 py-2 border rounded-lg bg-background resize-none text-sm"
            />

            <div className="flex gap-3 mt-4">
              <button
                onClick={() => setStage('draft_review')}
                className="px-4 py-2 border rounded-lg text-sm"
              >
                返回
              </button>
              <button
                onClick={handleGenerateInterpretation}
                disabled={loading || !userErrorReason.trim()}
                className="flex-1 py-2 bg-primary text-primary-foreground rounded-lg font-medium disabled:opacity-50 flex items-center justify-center gap-2"
              >
                <Sparkles className="w-4 h-4" />
                生成错因理解
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Stage: Interpreting */}
      {stage === 'interpreting' && (
        <div className="flex items-center justify-center py-20">
          <div className="text-center">
            <Loader2 className="w-8 h-8 animate-spin mx-auto mb-4 text-primary" />
            <p className="text-muted-foreground">AI 正在理解你的错因...</p>
          </div>
        </div>
      )}

      {/* Stage: Interpretation Review */}
      {stage === 'interpretation_review' && interpretation && (
        <div className="space-y-6">
          <div className="bg-card border rounded-xl p-6">
            <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <Sparkles className="w-5 h-5" />
              AI 对错因的理解
            </h2>

            <div className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-muted-foreground mb-1">概括</label>
                <p className="text-sm">{interpretation.summary}</p>
              </div>
              <div>
                <label className="block text-xs font-medium text-muted-foreground mb-1">诊断</label>
                <p className="text-sm">{interpretation.diagnosis}</p>
              </div>
              <div>
                <label className="block text-xs font-medium text-muted-foreground mb-1">根本原因</label>
                <p className="text-sm">{interpretation.root_cause}</p>
              </div>
              {interpretation.knowledge_gap && (
                <div>
                  <label className="block text-xs font-medium text-muted-foreground mb-1">知识缺口</label>
                  <p className="text-sm">{interpretation.knowledge_gap}</p>
                </div>
              )}
              {interpretation.suggested_correction && (
                <div>
                  <label className="block text-xs font-medium text-muted-foreground mb-1">纠正方向</label>
                  <p className="text-sm">{interpretation.suggested_correction}</p>
                </div>
              )}
            </div>

            {/* Rejection history */}
            {rejectionHistory.length > 0 && (
              <div className="mt-4 p-3 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg">
                <label className="block text-xs font-medium mb-2">之前的拒绝理由：</label>
                {rejectionHistory.map((r, i) => (
                  <p key={i} className="text-xs text-muted-foreground mb-1">{i + 1}. {r}</p>
                ))}
              </div>
            )}

            {/* Rejection input */}
            {showRejection && (
              <div className="mt-4 p-4 bg-muted/50 rounded-lg">
                <label className="block text-sm font-medium mb-2">不采纳的理由</label>
                <textarea
                  value={rejectionReason}
                  onChange={e => setRejectionReason(e.target.value)}
                  placeholder="哪里理解得不对？"
                  className="w-full h-20 px-3 py-2 border rounded-lg bg-background resize-none text-sm mb-3"
                />
                <div className="flex gap-2">
                  <button
                    onClick={() => { setShowRejection(false); setRejectionReason('') }}
                    className="px-3 py-1.5 border rounded text-sm"
                  >
                    取消
                  </button>
                  <button
                    onClick={handleRejectInterpretation}
                    disabled={loading || !rejectionReason.trim()}
                    className="px-3 py-1.5 bg-yellow-600 text-white rounded text-sm disabled:opacity-50 flex items-center gap-1"
                  >
                    {loading ? <Loader2 className="w-3 h-3 animate-spin" /> : <RefreshCw className="w-3 h-3" />}
                    重新生成
                  </button>
                </div>
              </div>
            )}

            <div className="flex gap-3 mt-6">
              <button
                onClick={() => setStage('error_reason')}
                className="px-4 py-2 border rounded-lg text-sm"
              >
                返回
              </button>
              {!showRejection && (
                <button
                  onClick={() => setShowRejection(true)}
                  className="px-4 py-2 border border-yellow-500 text-yellow-600 rounded-lg text-sm flex items-center gap-1"
                >
                  <XCircle className="w-4 h-4" />
                  不采纳，重写
                </button>
              )}
              <button
                onClick={handleAcceptInterpretation}
                className="flex-1 py-2 bg-green-600 text-white rounded-lg font-medium flex items-center justify-center gap-2"
              >
                <Check className="w-4 h-4" />
                采纳
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Stage: Analysis Done / Diagram */}
      {stage === 'analysis_done' && (
        <div className="space-y-6">
          <div className="bg-card border rounded-xl p-6">
            <h2 className="text-lg font-semibold mb-4">生成错题卡</h2>

            {/* Generate analysis button */}
            {!finalAnalysis && (
              <button
                onClick={handleGenerateAnalysis}
                disabled={loading}
                className="w-full py-3 bg-primary text-primary-foreground rounded-lg font-medium disabled:opacity-50 flex items-center justify-center gap-2 mb-4"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    正在生成解析...
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4" />
                    生成解析
                  </>
                )}
              </button>
            )}

            {/* Analysis preview */}
            {finalAnalysis && (
              <div className="space-y-4 mb-6">
                <div>
                  <label className="block text-xs font-medium text-muted-foreground mb-1">解析</label>
                  <p className="text-sm whitespace-pre-wrap">{finalAnalysis.analysis}</p>
                </div>
                {finalAnalysis.key_step && (
                  <div>
                    <label className="block text-xs font-medium text-muted-foreground mb-1">关键步骤</label>
                    <p className="text-sm">{finalAnalysis.key_step}</p>
                  </div>
                )}
                {finalAnalysis.similar_traps.length > 0 && (
                  <div>
                    <label className="block text-xs font-medium text-muted-foreground mb-1">相似陷阱</label>
                    <ul className="list-disc list-inside text-sm">
                      {finalAnalysis.similar_traps.map((t, i) => <li key={i}>{t}</li>)}
                    </ul>
                  </div>
                )}

                {/* Generate diagram button */}
                <button
                  onClick={handleGenerateDiagram}
                  disabled={loading}
                  className="w-full py-3 bg-secondary text-secondary-foreground rounded-lg font-medium disabled:opacity-50 flex items-center justify-center gap-2"
                >
                  {loading ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      正在生成图解...
                    </>
                  ) : (
                    <>
                      <Sparkles className="w-4 h-4" />
                      生成图解
                    </>
                  )}
                </button>
              </div>
            )}

            {/* Save section */}
            {finalAnalysis && (
              <div className="border-t pt-4 space-y-4">
                <h3 className="font-medium">保存设置</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-medium text-muted-foreground mb-1">标题</label>
                    <input
                      value={title}
                      onChange={e => setTitle(e.target.value)}
                      className="w-full px-3 py-2 border rounded-lg bg-background text-sm"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-muted-foreground mb-1">学科</label>
                    <input
                      value={subject}
                      onChange={e => setSubject(e.target.value)}
                      className="w-full px-3 py-2 border rounded-lg bg-background text-sm"
                    />
                  </div>
                </div>

                <button
                  onClick={handleSave}
                  disabled={saving}
                  className="w-full py-3 bg-green-600 text-white rounded-lg font-medium disabled:opacity-50 flex items-center justify-center gap-2"
                >
                  {saving ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      保存中...
                    </>
                  ) : (
                    <>
                      <Save className="w-4 h-4" />
                      保存错题
                    </>
                  )}
                </button>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Stage: Diagramming */}
      {stage === 'diagramming' && (
        <div className="flex items-center justify-center py-20">
          <div className="text-center">
            <Loader2 className="w-8 h-8 animate-spin mx-auto mb-4 text-primary" />
            <p className="text-muted-foreground">正在生成图解...</p>
          </div>
        </div>
      )}

      {/* Stage: Done */}
      {stage === 'done' && (
        <div className="space-y-6">
          <div className="bg-card border rounded-xl p-6">
            <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <Check className="w-5 h-5 text-green-600" />
              错题卡完成
            </h2>

            {/* Diagram preview */}
            {diagram && (
              <div className="mb-6 p-4 bg-muted/50 rounded-lg">
                <label className="block text-xs font-medium text-muted-foreground mb-2">
                  图解 ({diagram.strategy === 'structured' ? '结构化' : 'AI 生成图片'})
                </label>
                {diagram.strategy === 'structured' && diagram.structured_data && (
                  <div className="space-y-3">
                    <p className="text-sm font-medium">{diagram.structured_data.title}</p>
                    {diagram.structured_data.caption && (
                      <p className="text-xs text-muted-foreground">{diagram.structured_data.caption}</p>
                    )}
                    {diagram.structured_data.error_reason_annotation && (
                      <p className="text-xs text-yellow-600">错因标注: {diagram.structured_data.error_reason_annotation}</p>
                    )}
                    {diagram.structured_data.nodes.length > 0 && diagram.structured_data.edges.length > 0 && (
                      <StructuredGraphDiagram nodes={diagram.structured_data.nodes} edges={diagram.structured_data.edges} />
                    )}
                    {diagram.structured_data.table && diagram.structured_data.table.headers.length > 0 && (
                      <div className="overflow-x-auto">
                        <table className="w-full text-xs border-collapse">
                          <thead>
                            <tr>{diagram.structured_data.table.headers.map((h, i) => <th key={i} className="border px-2 py-1 bg-muted text-left font-medium">{h}</th>)}</tr>
                          </thead>
                          <tbody>
                            {diagram.structured_data.table.rows.map((row, ri) => (
                              <tr key={ri}>{row.cells.map((c, ci) => <td key={ci} className="border px-2 py-1">{c}</td>)}</tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    )}
                    {diagram.structured_data.mermaid && (
                      <div className="mt-2">
                        <pre className="text-xs bg-muted p-2 rounded overflow-x-auto">{diagram.structured_data.mermaid}</pre>
                      </div>
                    )}
                  </div>
                )}
                {diagram.strategy === 'qwen_image_fallback' && diagram.image_url && (
                  <img src={diagram.image_url} alt="AI 生成图解" className="max-w-full rounded-lg" />
                )}
                {diagram.strategy === 'qwen_image_fallback' && !diagram.image_url && (
                  <p className="text-xs text-muted-foreground">图片生成服务未配置</p>
                )}
              </div>
            )}

            {/* Analysis preview */}
            {finalAnalysis && (
              <div className="mb-6 space-y-3">
                <div>
                  <label className="block text-xs font-medium text-muted-foreground mb-1">解析</label>
                  <p className="text-sm whitespace-pre-wrap">{finalAnalysis.analysis}</p>
                </div>
              </div>
            )}

            {/* Save settings */}
            <div className="border-t pt-4 space-y-4">
              <h3 className="font-medium">保存设置</h3>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-medium text-muted-foreground mb-1">标题</label>
                  <input
                    value={title}
                    onChange={e => setTitle(e.target.value)}
                    className="w-full px-3 py-2 border rounded-lg bg-background text-sm"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-muted-foreground mb-1">学科</label>
                  <input
                    value={subject}
                    onChange={e => setSubject(e.target.value)}
                    className="w-full px-3 py-2 border rounded-lg bg-background text-sm"
                  />
                </div>
              </div>

              <button
                onClick={handleSave}
                disabled={saving}
                className="w-full py-3 bg-green-600 text-white rounded-lg font-medium disabled:opacity-50 flex items-center justify-center gap-2"
              >
                {saving ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    保存中...
                  </>
                ) : (
                  <>
                    <Save className="w-4 h-4" />
                    保存错题
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
