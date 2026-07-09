'use client'

import { forwardRef, useCallback, useEffect, useRef, useState } from 'react'
import { useRouter } from 'next/navigation'
import { toast } from 'sonner'
import {
  Camera,
  CheckCircle2,
  ChevronRight,
  FileText,
  Loader2,
  RefreshCw,
  Upload,
  XCircle,
} from 'lucide-react'

import { ApiError } from '@/lib/api/client'
import { getApiBase } from '@/lib/api/config'
import {
  getAttachmentContentUrl,
  uploadAttachment,
} from '@/lib/api/attachments'
import {
  type Capture,
  type CaptureConvert,
  type CaptureStatus,
  convertCapture,
  createCapture,
  getCapture,
  listCaptures,
  patchCapture,
  triggerDraft,
  triggerRecognition,
} from '@/lib/api/captures'
import { listKnowledgePoints, listSubjects } from '@/lib/api/taxonomy'
import type { Subject, KnowledgePoint } from '@/lib/api/taxonomy'
import { cn } from '@/lib/utils'

const STATUS_LABELS: Record<CaptureStatus, string> = {
  uploaded: '待识别',
  recognizing: '识别中',
  recognized: '已识别',
  drafting: '草稿生成中',
  ready: '待确认',
  failed: '失败',
  converted: '已转换',
  archived: '已归档',
}

const STATUS_COLORS: Record<CaptureStatus, string> = {
  uploaded: 'text-slate-500',
  recognizing: 'text-blue-500',
  recognized: 'text-blue-600',
  drafting: 'text-blue-500',
  ready: 'text-green-600',
  failed: 'text-red-500',
  converted: 'text-purple-600',
  archived: 'text-slate-400',
}

function isBusy(status: CaptureStatus): boolean {
  return status === 'recognizing' || status === 'drafting'
}

async function fetchImageBlob(attachmentId: string): Promise<string> {
  const url = getAttachmentContentUrl(attachmentId)
  const res = await fetch(url, { credentials: 'include' })
  if (!res.ok) throw new Error('Failed to fetch image')
  const blob = await res.blob()
  return URL.createObjectURL(blob)
}

export function CaptureWorkspace() {
  const router = useRouter()
  const fileInputRef = useRef<HTMLInputElement>(null)

  const [captures, setCaptures] = useState<Capture[]>([])
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [selected, setSelected] = useState<Capture | null>(null)
  const [loading, setLoading] = useState(true)
  const [uploading, setUploading] = useState(false)
  const [subjects, setSubjects] = useState<Subject[]>([])
  const [knowledgePoints, setKnowledgePoints] = useState<KnowledgePoint[]>([])

  const refreshCaptures = useCallback(async () => {
    try {
      const list = await listCaptures()
      setCaptures(list)
      if (list.length > 0 && !selectedId) {
        setSelectedId(list[0].id)
      }
    } catch (err) {
      if (err instanceof ApiError && err.kind === 'auth') return
      toast.error('加载采集列表失败')
    } finally {
      setLoading(false)
    }
  }, [selectedId])

  useEffect(() => {
    refreshCaptures()
  }, [refreshCaptures])

  useEffect(() => {
    listSubjects({ is_active: true }).then(setSubjects).catch(() => {})
  }, [])

  useEffect(() => {
    if (!selectedId) {
      setSelected(null)
      return
    }
    getCapture(selectedId)
      .then(setSelected)
      .catch(() => {
        toast.error('加载采集详情失败')
        setSelected(null)
      })
  }, [selectedId])

  useEffect(() => {
    if (!selected?.subject_id) {
      setKnowledgePoints([])
      return
    }
    listKnowledgePoints({ subject_id: selected.subject_id, is_active: true })
      .then(setKnowledgePoints)
      .catch(() => {})
  }, [selected?.subject_id])

  const handleUpload = useCallback(
    async (file: File) => {
      setUploading(true)
      try {
        if (!file.type.startsWith('image/')) {
          toast.error('请上传图片文件')
          return
        }
        const attachment = await uploadAttachment(file)
        const capture = await createCapture(attachment.id)
        setCaptures((prev) => [capture, ...prev])
        setSelectedId(capture.id)
        toast.success('图片已上传，可以开始识别')
      } catch (err) {
        const msg = err instanceof ApiError ? err.message : '上传失败'
        toast.error(msg)
      } finally {
        setUploading(false)
      }
    },
    [],
  )

  const updateSelected = useCallback((capture: Capture) => {
    setSelected(capture)
    setCaptures((prev) =>
      prev.map((c) => (c.id === capture.id ? capture : c)),
    )
  }, [])

  const handleRecognize = useCallback(async () => {
    if (!selected) return
    try {
      const updated = await triggerRecognition(selected.id)
      updateSelected(updated)
      if (updated.status === 'recognized') {
        toast.success('识别完成')
      } else if (updated.status === 'failed') {
        toast.error(`识别失败: ${updated.error_message_safe || '未知错误'}`)
      }
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : '识别请求失败')
    }
  }, [selected, updateSelected])

  const handleDraft = useCallback(async () => {
    if (!selected) return
    try {
      const updated = await triggerDraft(selected.id)
      updateSelected(updated)
      if (updated.status === 'ready') {
        toast.success('草稿生成完成，请确认后转换')
      } else if (updated.status === 'failed') {
        toast.error(`草稿生成失败: ${updated.error_message_safe || '未知错误'}`)
      }
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : '草稿请求失败')
    }
  }, [selected, updateSelected])

  const handlePatch = useCallback(
    async (patch: Parameters<typeof patchCapture>[1]) => {
      if (!selected) return
      try {
        const updated = await patchCapture(selected.id, patch)
        updateSelected(updated)
      } catch (err) {
        toast.error(err instanceof ApiError ? err.message : '保存失败')
      }
    },
    [selected, updateSelected],
  )

  const handleConvert = useCallback(
    async (payload: CaptureConvert) => {
      if (!selected) return
      try {
        const result = await convertCapture(selected.id, payload)
        updateSelected(result.capture)
        toast.success('已转为错题草稿，正在跳转...')
        router.push('/manage/drafts')
      } catch (err) {
        toast.error(err instanceof ApiError ? err.message : '转换失败')
      }
    },
    [selected, updateSelected, router],
  )

  if (loading) {
    return (
      <div className='flex items-center justify-center py-20'>
        <Loader2 className='h-6 w-6 animate-spin text-slate-400' />
      </div>
    )
  }

  return (
    <div className='space-y-6'>
      <UploadArea
        ref={fileInputRef}
        uploading={uploading}
        onUpload={handleUpload}
      />

      {captures.length === 0 ? (
        <EmptyState />
      ) : (
        <div className='grid gap-6 lg:grid-cols-[280px_1fr]'>
          <CaptureList
            captures={captures}
            selectedId={selectedId}
            onSelect={setSelectedId}
          />
          {selected ? (
            <CaptureDetail
              capture={selected}
              subjects={subjects}
              knowledgePoints={knowledgePoints}
              onRecognize={handleRecognize}
              onDraft={handleDraft}
              onPatch={handlePatch}
              onConvert={handleConvert}
            />
          ) : (
            <div className='flex items-center justify-center rounded-2xl border border-white/45 bg-white/48 p-10 text-sm text-slate-400'>
              选择左侧的采集项查看详情
            </div>
          )}
        </div>
      )}
    </div>
  )
}

interface UploadAreaProps {
  uploading: boolean
  onUpload: (file: File) => void
}

const UploadArea = forwardRef<HTMLInputElement, UploadAreaProps>(
  function UploadArea({ uploading, onUpload }, ref) {
    const internalRef = useRef<HTMLInputElement>(null)
    const inputRef = (ref as React.RefObject<HTMLInputElement | null>) ?? internalRef

    return (
      <div
        className={cn(
          'flex flex-col items-center justify-center gap-3 rounded-2xl border-2 border-dashed border-white/50 bg-white/40 p-8 text-center transition-colors',
          uploading && 'opacity-60',
        )}
        onDragOver={(e) => e.preventDefault()}
        onDrop={(e) => {
          e.preventDefault()
          const file = e.dataTransfer.files[0]
          if (file && !uploading) onUpload(file)
        }}
      >
        <input
          ref={inputRef}
          type='file'
          accept='image/*'
          className='hidden'
          onChange={(e) => {
            const file = e.target.files?.[0]
            if (file && !uploading) onUpload(file)
            e.target.value = ''
          }}
        />
        <Camera className='h-8 w-8 text-slate-400' />
        <div>
          <button
            type='button'
            disabled={uploading}
            onClick={() => inputRef.current?.click()}
            className='text-sm font-medium text-[var(--color-brand)] hover:underline disabled:opacity-50'
          >
            {uploading ? '上传中...' : '点击上传图片'}
          </button>
          <span className='text-sm text-slate-400'> 或拖拽到此处</span>
        </div>
        <p className='text-xs text-slate-400'>支持 PNG / JPEG / WebP，最大 10MB</p>
      </div>
    )
  },
)

function EmptyState() {
  return (
    <div className='flex flex-col items-center justify-center gap-3 rounded-2xl border border-white/45 bg-white/48 p-12 text-center'>
      <FileText className='h-8 w-8 text-slate-300' />
      <p className='text-sm text-slate-400'>还没有采集项，上传一张错题图片开始</p>
    </div>
  )
}

interface CaptureListProps {
  captures: Capture[]
  selectedId: string | null
  onSelect: (id: string) => void
}

function CaptureList({ captures, selectedId, onSelect }: CaptureListProps) {
  return (
    <div className='max-h-[600px] space-y-1 overflow-y-auto rounded-2xl border border-white/45 bg-white/48 p-2'>
      {captures.map((capture) => (
        <button
          key={capture.id}
          onClick={() => onSelect(capture.id)}
          className={cn(
            'flex w-full items-center gap-2 rounded-xl px-3 py-2.5 text-left text-sm transition-colors',
            capture.id === selectedId
              ? 'bg-[var(--color-brand)]/14 font-medium text-[var(--color-brand)]'
              : 'text-slate-600 hover:bg-white/65',
          )}
        >
          <span className='truncate flex-1'>
            {capture.question_draft_text
              ? capture.question_draft_text.slice(0, 30)
              : `采集 ${capture.id.slice(0, 8)}`}
          </span>
          <span className={cn('shrink-0 text-xs', STATUS_COLORS[capture.status])}>
            {isBusy(capture.status) && (
              <Loader2 className='mr-1 inline h-3 w-3 animate-spin' />
            )}
            {STATUS_LABELS[capture.status]}
          </span>
        </button>
      ))}
    </div>
  )
}

interface CaptureDetailProps {
  capture: Capture
  subjects: Subject[]
  knowledgePoints: KnowledgePoint[]
  onRecognize: () => void
  onDraft: () => void
  onPatch: (patch: Parameters<typeof patchCapture>[1]) => void
  onConvert: (payload: CaptureConvert) => void
}

function CaptureDetail({
  capture,
  subjects,
  knowledgePoints,
  onRecognize,
  onDraft,
  onPatch,
  onConvert,
}: CaptureDetailProps) {
  return (
    <div className='space-y-5 rounded-2xl border border-white/45 bg-white/48 p-5'>
      <DetailHeader capture={capture} />
      <ImagePreview attachmentId={capture.source_attachment_id} />
      {capture.status === 'failed' && capture.error_message_safe && (
        <ErrorBanner message={capture.error_message_safe} />
      )}
      <RecognizedTextSection
        capture={capture}
        onPatch={onPatch}
      />
      <ErrorContextSection
        capture={capture}
        onPatch={onPatch}
      />
      <DraftFieldsSection
        capture={capture}
        onPatch={onPatch}
      />
      <ActionButtons
        capture={capture}
        onRecognize={onRecognize}
        onDraft={onDraft}
      />
      {capture.status === 'ready' && (
        <ConvertForm
          capture={capture}
          subjects={subjects}
          knowledgePoints={knowledgePoints}
          onConvert={onConvert}
        />
      )}
      {capture.status === 'converted' && (
        <ConvertedBanner mistakeDraftItemId={capture.mistake_draft_item_id} />
      )}
    </div>
  )
}

function DetailHeader({ capture }: { capture: Capture }) {
  return (
    <div className='flex items-center justify-between border-b border-white/40 pb-3'>
      <div>
        <p className='text-xs text-slate-400'>采集 ID</p>
        <p className='font-mono text-sm text-slate-600'>{capture.id.slice(0, 8)}</p>
      </div>
      <div className='text-right'>
        <p className='text-xs text-slate-400'>状态</p>
        <p className={cn('text-sm font-medium', STATUS_COLORS[capture.status])}>
          {isBusy(capture.status) && (
            <Loader2 className='mr-1 inline h-3.5 w-3.5 animate-spin' />
          )}
          {STATUS_LABELS[capture.status]}
          {capture.attempt_count > 0 && (
            <span className='ml-1 text-xs text-slate-400'>
              (第 {capture.attempt_count} 次)
            </span>
          )}
        </p>
      </div>
    </div>
  )
}

function ImagePreview({ attachmentId }: { attachmentId: string }) {
  const [url, setUrl] = useState<string | null>(null)
  const [error, setError] = useState(false)

  useEffect(() => {
    let objectUrl: string | null = null
    setUrl(null)
    setError(false)
    fetchImageBlob(attachmentId)
      .then((u) => {
        objectUrl = u
        setUrl(u)
      })
      .catch(() => setError(true))
    return () => {
      if (objectUrl) URL.revokeObjectURL(objectUrl)
    }
  }, [attachmentId])

  if (error) {
    return (
      <div className='flex items-center justify-center rounded-xl bg-slate-100 p-8 text-sm text-slate-400'>
        图片加载失败
      </div>
    )
  }
  if (!url) {
    return (
      <div className='flex items-center justify-center rounded-xl bg-slate-100 p-8'>
        <Loader2 className='h-5 w-5 animate-spin text-slate-400' />
      </div>
    )
  }
  return (
    <img
      src={url}
      alt='错题原图'
      className='max-h-80 w-full rounded-xl object-contain'
    />
  )
}

function ErrorBanner({ message }: { message: string }) {
  return (
    <div className='flex items-start gap-2 rounded-xl bg-red-50 p-3 text-sm text-red-600'>
      <XCircle className='mt-0.5 h-4 w-4 shrink-0' />
      <span>{message}</span>
    </div>
  )
}

function RecognizedTextSection({
  capture,
  onPatch,
}: {
  capture: Capture
  onPatch: (patch: Parameters<typeof patchCapture>[1]) => void
}) {
  const [text, setText] = useState(capture.recognized_text || '')
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    setText(capture.recognized_text || '')
  }, [capture.recognized_text])

  const handleSave = async () => {
    setSaving(true)
    await onPatch({ recognized_text: text || null })
    setSaving(false)
  }

  const dirty = text !== (capture.recognized_text || '')

  return (
    <section className='space-y-2'>
      <div className='flex items-center justify-between'>
        <h3 className='text-sm font-medium text-slate-700'>识别文字</h3>
        {dirty && (
          <button
            onClick={handleSave}
            disabled={saving}
            className='text-xs text-[var(--color-brand)] hover:underline disabled:opacity-50'
          >
            {saving ? '保存中...' : '保存修改'}
          </button>
        )}
      </div>
      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        rows={4}
        placeholder='识别文字将显示在这里，可手动修正'
        className='w-full resize-y rounded-xl border border-white/50 bg-white/60 p-3 text-sm text-slate-700 placeholder:text-slate-300 focus:border-[var(--color-brand)]/40 focus:outline-none'
      />
    </section>
  )
}

function ErrorContextSection({
  capture,
  onPatch,
}: {
  capture: Capture
  onPatch: (patch: Parameters<typeof patchCapture>[1]) => void
}) {
  const [text, setText] = useState(capture.user_error_context || '')
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    setText(capture.user_error_context || '')
  }, [capture.user_error_context])

  const handleSave = async () => {
    setSaving(true)
    await onPatch({ user_error_context: text || null })
    setSaving(false)
  }

  const dirty = text !== (capture.user_error_context || '')

  return (
    <section className='space-y-2'>
      <div className='flex items-center justify-between'>
        <h3 className='text-sm font-medium text-slate-700'>我当时为什么错</h3>
        {dirty && (
          <button
            onClick={handleSave}
            disabled={saving}
            className='text-xs text-[var(--color-brand)] hover:underline disabled:opacity-50'
          >
            {saving ? '保存中...' : '保存修改'}
          </button>
        )}
      </div>
      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        rows={2}
        placeholder='补充你的错误思路或混淆点（可选，帮助 AI 生成更准确的草稿）'
        className='w-full resize-y rounded-xl border border-white/50 bg-white/60 p-3 text-sm text-slate-700 placeholder:text-slate-300 focus:border-[var(--color-brand)]/40 focus:outline-none'
      />
    </section>
  )
}

function DraftFieldsSection({
  capture,
  onPatch,
}: {
  capture: Capture
  onPatch: (patch: Parameters<typeof patchCapture>[1]) => void
}) {
  const [question, setQuestion] = useState(capture.question_draft_text || '')
  const [analysis, setAnalysis] = useState(capture.analysis_draft_text || '')
  const [errorSummary, setErrorSummary] = useState(capture.error_summary_draft || '')
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    setQuestion(capture.question_draft_text || '')
    setAnalysis(capture.analysis_draft_text || '')
    setErrorSummary(capture.error_summary_draft || '')
  }, [
    capture.question_draft_text,
    capture.analysis_draft_text,
    capture.error_summary_draft,
  ])

  const dirty =
    question !== (capture.question_draft_text || '') ||
    analysis !== (capture.analysis_draft_text || '') ||
    errorSummary !== (capture.error_summary_draft || '')

  const handleSave = async () => {
    setSaving(true)
    await onPatch({
      question_draft_text: question || null,
      analysis_draft_text: analysis || null,
      error_summary_draft: errorSummary || null,
    })
    setSaving(false)
  }

  const show = ['recognized', 'drafting', 'ready', 'failed', 'converted'].includes(
    capture.status,
  )

  if (!show) return null

  return (
    <section className='space-y-3'>
      <div className='flex items-center justify-between'>
        <h3 className='text-sm font-medium text-slate-700'>AI 草稿（可编辑）</h3>
        {dirty && (
          <button
            onClick={handleSave}
            disabled={saving}
            className='text-xs text-[var(--color-brand)] hover:underline disabled:opacity-50'
          >
            {saving ? '保存中...' : '保存修改'}
          </button>
        )}
      </div>
      <div className='space-y-2'>
        <label className='text-xs text-slate-400'>题面</label>
        <textarea
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          rows={3}
          placeholder='题面草稿'
          className='w-full resize-y rounded-xl border border-white/50 bg-white/60 p-3 text-sm text-slate-700 placeholder:text-slate-300 focus:border-[var(--color-brand)]/40 focus:outline-none'
        />
      </div>
      <div className='space-y-2'>
        <label className='text-xs text-slate-400'>解析</label>
        <textarea
          value={analysis}
          onChange={(e) => setAnalysis(e.target.value)}
          rows={3}
          placeholder='解析草稿'
          className='w-full resize-y rounded-xl border border-white/50 bg-white/60 p-3 text-sm text-slate-700 placeholder:text-slate-300 focus:border-[var(--color-brand)]/40 focus:outline-none'
        />
      </div>
      <div className='space-y-2'>
        <label className='text-xs text-slate-400'>错因总结</label>
        <textarea
          value={errorSummary}
          onChange={(e) => setErrorSummary(e.target.value)}
          rows={2}
          placeholder='错因总结草稿'
          className='w-full resize-y rounded-xl border border-white/50 bg-white/60 p-3 text-sm text-slate-700 placeholder:text-slate-300 focus:border-[var(--color-brand)]/40 focus:outline-none'
        />
      </div>
      {capture.knowledge_point_suggestions.length > 0 && (
        <div className='flex flex-wrap gap-1.5'>
          {capture.knowledge_point_suggestions.map((kp, i) => (
            <span
              key={i}
              className='rounded-full bg-slate-100 px-2.5 py-0.5 text-xs text-slate-500'
            >
              {kp.label}
              {kp.confidence != null && ` (${Math.round(kp.confidence * 100)}%)`}
            </span>
          ))}
        </div>
      )}
    </section>
  )
}

function ActionButtons({
  capture,
  onRecognize,
  onDraft,
}: {
  capture: Capture
  onRecognize: () => void
  onDraft: () => void
}) {
  const busy = isBusy(capture.status)
  const canRecognize = !busy && capture.status !== 'converted' && capture.status !== 'archived'
  const canDraft =
    !busy &&
    ['recognized', 'failed', 'ready'].includes(capture.status) &&
    !!capture.recognized_text

  return (
    <div className='flex flex-wrap gap-2'>
      {canRecognize && (
        <button
          onClick={onRecognize}
          disabled={busy}
          className='flex items-center gap-1.5 rounded-xl bg-[var(--color-brand)]/10 px-4 py-2 text-sm font-medium text-[var(--color-brand)] transition-colors hover:bg-[var(--color-brand)]/20 disabled:opacity-50'
        >
          <RefreshCw className='h-4 w-4' />
          {capture.status === 'uploaded' ? '开始识别' : '重新识别'}
        </button>
      )}
      {canDraft && (
        <button
          onClick={onDraft}
          disabled={busy}
          className='flex items-center gap-1.5 rounded-xl bg-[var(--color-brand)]/10 px-4 py-2 text-sm font-medium text-[var(--color-brand)] transition-colors hover:bg-[var(--color-brand)]/20 disabled:opacity-50'
        >
          <RefreshCw className='h-4 w-4' />
          {capture.question_draft_text ? '重新生成草稿' : '生成 AI 草稿'}
        </button>
      )}
    </div>
  )
}

function ConvertForm({
  capture,
  subjects,
  knowledgePoints,
  onConvert,
}: {
  capture: Capture
  subjects: Subject[]
  knowledgePoints: KnowledgePoint[]
  onConvert: (payload: CaptureConvert) => void
}) {
  const [subjectId, setSubjectId] = useState<number | null>(
    capture.subject_id ?? null,
  )
  const [questionText, setQuestionText] = useState(
    capture.question_draft_text || '',
  )
  const [myAnswer, setMyAnswer] = useState('')
  const [mistakeReason, setMistakeReason] = useState(
    capture.error_summary_draft || '',
  )
  const [reasonCategory, setReasonCategory] =
    useState<CaptureConvert['reason_category']>('unknown')
  const [difficulty, setDifficulty] =
    useState<CaptureConvert['difficulty'] | null>(null)
  const [selectedKpIds, setSelectedKpIds] = useState<number[]>([])
  const [converting, setConverting] = useState(false)

  useEffect(() => {
    setSubjectId(capture.subject_id ?? null)
    setQuestionText(capture.question_draft_text || '')
    setMistakeReason(capture.error_summary_draft || '')
  }, [
    capture.subject_id,
    capture.question_draft_text,
    capture.error_summary_draft,
  ])

  const canConvert = subjectId !== null && questionText.trim().length > 0

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!subjectId || !questionText.trim()) return
    setConverting(true)
    await onConvert({
      subject_id: subjectId,
      question_text: questionText.trim(),
      question_type: 'short_answer',
      my_answer: myAnswer || null,
      reason_category: reasonCategory,
      mistake_reason: mistakeReason || null,
      difficulty: difficulty,
      knowledge_point_ids: selectedKpIds,
    })
    setConverting(false)
  }

  return (
    <form
      onSubmit={handleSubmit}
      className='space-y-4 rounded-2xl border border-[var(--color-brand)]/20 bg-[var(--color-brand)]/5 p-4'
    >
      <h3 className='flex items-center gap-2 text-sm font-medium text-slate-700'>
        <CheckCircle2 className='h-4 w-4 text-green-500' />
        确认并转为错题草稿
      </h3>

      <div className='space-y-2'>
        <label className='text-xs text-slate-500'>学科 *</label>
        <select
          value={subjectId ?? ''}
          onChange={(e) => setSubjectId(e.target.value ? Number(e.target.value) : null)}
          className='w-full rounded-xl border border-white/50 bg-white/80 p-2.5 text-sm focus:border-[var(--color-brand)]/40 focus:outline-none'
        >
          <option value=''>选择学科</option>
          {subjects.map((s) => (
            <option key={s.id} value={s.id}>
              {s.name}
            </option>
          ))}
        </select>
      </div>

      <div className='space-y-2'>
        <label className='text-xs text-slate-500'>题面 *</label>
        <textarea
          value={questionText}
          onChange={(e) => setQuestionText(e.target.value)}
          rows={3}
          className='w-full resize-y rounded-xl border border-white/50 bg-white/80 p-3 text-sm focus:border-[var(--color-brand)]/40 focus:outline-none'
        />
      </div>

      <div className='grid gap-3 sm:grid-cols-2'>
        <div className='space-y-2'>
          <label className='text-xs text-slate-500'>我的答案</label>
          <input
            value={myAnswer}
            onChange={(e) => setMyAnswer(e.target.value)}
            className='w-full rounded-xl border border-white/50 bg-white/80 p-2.5 text-sm focus:border-[var(--color-brand)]/40 focus:outline-none'
          />
        </div>
        <div className='space-y-2'>
          <label className='text-xs text-slate-500'>难度</label>
          <select
            value={difficulty ?? ''}
            onChange={(e) =>
              setDifficulty(
                e.target.value
                  ? (e.target.value as CaptureConvert['difficulty'])
                  : null,
              )
            }
            className='w-full rounded-xl border border-white/50 bg-white/80 p-2.5 text-sm focus:border-[var(--color-brand)]/40 focus:outline-none'
          >
            <option value=''>不指定</option>
            <option value='easy'>简单</option>
            <option value='medium'>中等</option>
            <option value='hard'>困难</option>
          </select>
        </div>
      </div>

      <div className='grid gap-3 sm:grid-cols-2'>
        <div className='space-y-2'>
          <label className='text-xs text-slate-500'>错误类型</label>
          <select
            value={reasonCategory}
            onChange={(e) =>
              setReasonCategory(
                e.target.value as CaptureConvert['reason_category'],
              )
            }
            className='w-full rounded-xl border border-white/50 bg-white/80 p-2.5 text-sm focus:border-[var(--color-brand)]/40 focus:outline-none'
          >
            <option value='unknown'>未分类</option>
            <option value='concept'>概念错误</option>
            <option value='calculation'>计算错误</option>
            <option value='reading'>审题错误</option>
            <option value='careless'>粗心失误</option>
          </select>
        </div>
        <div className='space-y-2'>
          <label className='text-xs text-slate-500'>错因说明</label>
          <input
            value={mistakeReason}
            onChange={(e) => setMistakeReason(e.target.value)}
            className='w-full rounded-xl border border-white/50 bg-white/80 p-2.5 text-sm focus:border-[var(--color-brand)]/40 focus:outline-none'
          />
        </div>
      </div>

      {knowledgePoints.length > 0 && (
        <div className='space-y-2'>
          <label className='text-xs text-slate-500'>知识点</label>
          <div className='flex flex-wrap gap-1.5'>
            {knowledgePoints.map((kp) => (
              <button
                key={kp.id}
                type='button'
                onClick={() =>
                  setSelectedKpIds((prev) =>
                    prev.includes(kp.id)
                      ? prev.filter((id) => id !== kp.id)
                      : [...prev, kp.id],
                  )
                }
                className={cn(
                  'rounded-full px-2.5 py-0.5 text-xs transition-colors',
                  selectedKpIds.includes(kp.id)
                    ? 'bg-[var(--color-brand)]/20 text-[var(--color-brand)]'
                    : 'bg-slate-100 text-slate-500 hover:bg-slate-200',
                )}
              >
                {kp.name}
              </button>
            ))}
          </div>
        </div>
      )}

      <button
        type='submit'
        disabled={!canConvert || converting}
        className='flex w-full items-center justify-center gap-2 rounded-xl bg-[var(--color-brand)] px-4 py-2.5 text-sm font-medium text-white transition-colors hover:bg-[var(--color-brand)]/90 disabled:opacity-50'
      >
        {converting ? (
          <Loader2 className='h-4 w-4 animate-spin' />
        ) : (
          <ChevronRight className='h-4 w-4' />
        )}
        转为错题草稿
      </button>
      <p className='text-center text-xs text-slate-400'>
        转换后仍需在错题草稿页面人工确认，才会生成正式错题和复习项
      </p>
    </form>
  )
}

function ConvertedBanner({
  mistakeDraftItemId,
}: {
  mistakeDraftItemId: string | null
}) {
  const router = useRouter()
  if (!mistakeDraftItemId) return null
  return (
    <div className='flex items-center justify-between rounded-2xl bg-green-50 p-4'>
      <div className='flex items-center gap-2'>
        <CheckCircle2 className='h-5 w-5 text-green-500' />
        <span className='text-sm text-green-700'>
          已转为错题草稿，等待人工确认
        </span>
      </div>
      <button
        onClick={() => router.push('/manage/drafts')}
        className='flex items-center gap-1 text-sm font-medium text-green-600 hover:underline'
      >
        去确认 <ChevronRight className='h-4 w-4' />
      </button>
    </div>
  )
}
