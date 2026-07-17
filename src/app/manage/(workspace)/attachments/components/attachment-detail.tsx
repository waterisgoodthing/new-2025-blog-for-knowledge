'use client'

import Link from 'next/link'
import { FormEvent, useEffect, useMemo, useState } from 'react'
import { Archive, ArrowLeft, ExternalLink } from 'lucide-react'
import { useRouter } from 'next/navigation'

import {
  deleteAttachment,
  createAttachmentLink,
  deleteAttachmentLink,
  getAttachment,
  getAttachmentContentUrl,
  listAttachmentLinks,
  type Attachment,
  type AttachmentCreatePurpose,
  type AttachmentLink,
  type AttachmentTargetType,
} from '@/lib/api/attachments'

function message(reason: unknown, fallback: string) {
  return reason instanceof Error ? reason.message : fallback
}

function formatBytes(value: number) {
  if (value < 1024) return `${value} B`
  if (value < 1024 * 1024) return `${(value / 1024).toFixed(1)} KB`
  return `${(value / 1024 / 1024).toFixed(1)} MB`
}

export function AttachmentDetail({ id }: { id: string }) {
  const router = useRouter()
  const [attachment, setAttachment] = useState<Attachment | null>(null)
  const [links, setLinks] = useState<AttachmentLink[]>([])
  const [targetType, setTargetType] = useState<AttachmentTargetType>('question')
  const [targetId, setTargetId] = useState('')
  const [purpose, setPurpose] = useState<AttachmentCreatePurpose>('source')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function loadLinks() {
    setLinks(await listAttachmentLinks({ attachment_id: id }))
  }

  useEffect(() => {
    Promise.all([getAttachment(id), listAttachmentLinks({ attachment_id: id })])
      .then(([nextAttachment, nextLinks]) => {
        setAttachment(nextAttachment)
        setLinks(nextLinks)
      })
      .catch((reason: unknown) => setError(message(reason, '加载附件失败')))
  }, [id])

  const contentUrl = useMemo(() => getAttachmentContentUrl(id), [id])
  const downloadUrl = useMemo(() => getAttachmentContentUrl(id, 'attachment'), [id])

  if (!attachment) {
    return (
      <div className='max-w-4xl space-y-5'>
        <BackLink />
        <p className='text-sm text-slate-500'>{error || '正在加载附件…'}</p>
      </div>
    )
  }

  const addLink = async (event: FormEvent) => {
    event.preventDefault()
    if (!targetId.trim()) return
    setBusy(true)
    setError(null)
    try {
      await createAttachmentLink({
        attachment_id: attachment.id,
        target_type: targetType,
        target_id: targetId.trim(),
        purpose,
      })
      setTargetId('')
      await loadLinks()
    } catch (reason) {
      setError(message(reason, '创建附件关联失败'))
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className='max-w-5xl space-y-7'>
      <BackLink />
      <header>
        <p className='text-xs font-medium tracking-[0.16em] text-[var(--color-brand)]/75 uppercase'>
          {attachment.status} · {attachment.visibility} · {attachment.storage_provider}
        </p>
        <h1 className='mt-2 break-words text-2xl font-semibold text-slate-900'>{attachment.original_name}</h1>
        <p className='mt-2 text-sm text-slate-500'>{attachment.mime_type} · {formatBytes(attachment.size_bytes)}</p>
      </header>

      <section className='grid gap-5 lg:grid-cols-[minmax(0,1fr)_320px]'>
        <div className='rounded-3xl border border-slate-200/70 bg-white/80 p-5 shadow-sm'>
          <h2 className='font-semibold text-slate-900'>预览</h2>
          <div className='mt-4 overflow-hidden rounded-2xl border border-slate-100 bg-slate-50'>
            <AttachmentPreview attachment={attachment} contentUrl={contentUrl} />
          </div>
        </div>

        <aside className='space-y-5 rounded-3xl border border-slate-200/70 bg-white/80 p-5 shadow-sm'>
          <div>
            <h2 className='font-semibold text-slate-900'>元数据</h2>
            <dl className='mt-4 space-y-3 text-sm'>
              <Meta label='ID' value={attachment.id} />
              <Meta label='MIME' value={attachment.mime_type} />
              <Meta label='大小' value={formatBytes(attachment.size_bytes)} />
              <Meta label='SHA-256' value={attachment.checksum_sha256} />
              <Meta label='创建时间' value={new Date(attachment.created_at).toLocaleString('zh-CN')} />
            </dl>
          </div>
          <a
            href={downloadUrl}
            target='_blank'
            rel='noreferrer'
            className='inline-flex items-center gap-2 rounded-lg border border-slate-200 px-4 py-2 text-sm text-slate-700'
          >
            <ExternalLink className='h-4 w-4' />
            下载附件
          </a>
          {attachment.status !== 'deleted' ? (
            <button
              type='button'
              disabled={busy}
              onClick={async () => {
                if (!window.confirm('确认标记删除这个附件？')) return
                setBusy(true)
                setError(null)
                try {
                  await deleteAttachment(attachment.id)
                  router.push('/manage/attachments')
                } catch (reason) {
                  setError(message(reason, '删除附件失败'))
                  setBusy(false)
                }
              }}
              className='inline-flex items-center gap-2 rounded-lg border border-amber-200 px-4 py-2 text-sm text-amber-700 disabled:opacity-45'
            >
              <Archive className='h-4 w-4' />
              标记删除
            </button>
          ) : null}
          {error ? <p role='alert' className='text-sm text-red-600'>{error}</p> : null}
        </aside>
      </section>

      <section className='rounded-3xl border border-slate-200/70 bg-white/80 p-5 shadow-sm'>
        <h2 className='font-semibold text-slate-900'>业务关联</h2>
        <p className='mt-1 text-sm text-slate-500'>
          第一版通过 attachment links 关联草稿、题目或错题；附件表本身不保存 owner 字段。
        </p>
        <form onSubmit={addLink} className='mt-5 grid gap-3 md:grid-cols-[160px_minmax(0,1fr)_160px_auto]'>
          <label className='text-sm font-medium text-slate-700'>
            目标类型
            <select
              value={targetType}
              disabled={busy || attachment.status !== 'active'}
              onChange={(event) => setTargetType(event.target.value as AttachmentTargetType)}
              className='mt-2 w-full rounded-lg border border-slate-200 bg-white px-3 py-2.5 text-sm'
            >
              <option value='question_draft'>question_draft</option>
              <option value='question'>question</option>
              <option value='mistake'>mistake</option>
            </select>
          </label>
          <label className='text-sm font-medium text-slate-700'>
            目标 ID
            <input
              value={targetId}
              disabled={busy || attachment.status !== 'active'}
              onChange={(event) => setTargetId(event.target.value)}
              placeholder='UUID'
              className='mt-2 w-full rounded-lg border border-slate-200 px-3 py-2.5 text-sm'
            />
          </label>
          <label className='text-sm font-medium text-slate-700'>
            用途
            <select
              value={purpose}
              disabled={busy || attachment.status !== 'active'}
              onChange={(event) => setPurpose(event.target.value as AttachmentCreatePurpose)}
              className='mt-2 w-full rounded-lg border border-slate-200 bg-white px-3 py-2.5 text-sm'
            >
              <option value='source'>source</option>
              <option value='question'>question</option>
              <option value='answer'>answer</option>
              <option value='inline'>inline</option>
            </select>
          </label>
          <button
            disabled={busy || attachment.status !== 'active' || !targetId.trim()}
            className='self-end rounded-lg bg-[var(--color-brand)] px-5 py-2.5 text-sm font-medium text-white disabled:opacity-45'
          >
            关联
          </button>
        </form>

        <div className='mt-5 divide-y divide-slate-100'>
          {links.length === 0 ? <p className='py-4 text-sm text-slate-500'>暂无业务关联。</p> : null}
          {links.map((link) => (
            <div key={link.id} className='flex flex-col gap-3 py-4 sm:flex-row sm:items-center sm:justify-between'>
              <div className='min-w-0 text-sm'>
                <p className='font-medium text-slate-800'>{link.target_type} · {link.purpose}</p>
                <p className='mt-1 break-all text-xs text-slate-400'>{link.target_id}</p>
              </div>
              <button
                type='button'
                disabled={busy}
                onClick={async () => {
                  setBusy(true)
                  setError(null)
                  try {
                    await deleteAttachmentLink(link.id)
                    await loadLinks()
                  } catch (reason) {
                    setError(message(reason, '解除关联失败'))
                  } finally {
                    setBusy(false)
                  }
                }}
                className='rounded-lg border border-slate-200 px-3 py-2 text-sm text-slate-600 disabled:opacity-45'
              >
                解除关联
              </button>
            </div>
          ))}
        </div>
      </section>

      <section className='rounded-3xl border border-dashed border-slate-300 bg-slate-50/80 p-5'>
        <h2 className='font-semibold text-slate-900'>OCR 还没有开启</h2>
        <p className='mt-2 text-sm leading-6 text-slate-500'>
          这个附件可以作为未来 OCR / Capture Router 的输入来源，但当前版本不会自动识别、
          不会拆分 PDF，也不会把识别结果写入草稿或正式题库。
        </p>
        <div className='mt-4 flex flex-wrap gap-2 text-xs text-slate-500'>
          <span className='rounded-full bg-white px-3 py-1.5'>无 OCR 请求</span>
          <span className='rounded-full bg-white px-3 py-1.5'>无后台任务</span>
          <span className='rounded-full bg-white px-3 py-1.5'>无自动写入</span>
        </div>
      </section>
    </div>
  )
}

function AttachmentPreview({
  attachment,
  contentUrl,
}: {
  attachment: Attachment
  contentUrl: string
}) {
  if (attachment.status !== 'active') {
    return <p className='p-6 text-sm text-slate-500'>附件状态为 {attachment.status}，无法预览。</p>
  }
  if (attachment.mime_type.startsWith('image/')) {
    return <img src={contentUrl} alt={attachment.original_name} className='max-h-[560px] w-full object-contain' />
  }
  if (attachment.mime_type === 'application/pdf') {
    return <iframe src={contentUrl} title={attachment.original_name} className='h-[560px] w-full' />
  }
  if (attachment.mime_type === 'text/plain') {
    return <iframe src={contentUrl} title={attachment.original_name} className='h-96 w-full bg-white' />
  }
  return <p className='p-6 text-sm text-slate-500'>该类型暂不支持内嵌预览，请使用“新窗口打开”。</p>
}

function Meta({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <dt className='text-xs text-slate-400'>{label}</dt>
      <dd className='mt-1 break-all text-slate-700'>{value}</dd>
    </div>
  )
}

function BackLink() {
  return (
    <Link href='/manage/attachments' className='inline-flex items-center gap-2 text-sm text-slate-500'>
      <ArrowLeft className='h-4 w-4' />
      返回附件
    </Link>
  )
}
