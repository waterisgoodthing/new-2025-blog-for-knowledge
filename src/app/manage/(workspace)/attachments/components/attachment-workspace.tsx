'use client'

import Link from 'next/link'
import { FormEvent, useEffect, useState } from 'react'
import { ArrowRight, FileUp, RefreshCcw } from 'lucide-react'

import {
  listAttachments,
  uploadAttachment,
  type Attachment,
  type AttachmentStatus,
} from '@/lib/api/attachments'
import { attachmentStatusLabel, attachmentVisibilityLabel } from '@/lib/manage-display'
import { FeatureState } from '../../../components/feature-state'

function message(reason: unknown, fallback: string) {
  return reason instanceof Error ? reason.message : fallback
}

function formatBytes(value: number) {
  if (value < 1024) return `${value} B`
  if (value < 1024 * 1024) return `${(value / 1024).toFixed(1)} KB`
  return `${(value / 1024 / 1024).toFixed(1)} MB`
}

export function AttachmentWorkspace() {
  const [items, setItems] = useState<Attachment[]>([])
  const [status, setStatus] = useState<AttachmentStatus | ''>('active')
  const [file, setFile] = useState<File | null>(null)
  const [loading, setLoading] = useState(true)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function load(nextStatus = status) {
    setLoading(true)
    setError(null)
    try {
      setItems(await listAttachments(nextStatus ? { status: nextStatus } : {}))
    } catch (reason) {
      setError(message(reason, '加载附件失败'))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void load()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const submit = async (event: FormEvent) => {
    event.preventDefault()
    if (!file) return
    setBusy(true)
    setError(null)
    try {
      await uploadAttachment(file)
      setFile(null)
      const input = document.getElementById('attachment-file') as HTMLInputElement | null
      if (input) input.value = ''
      await load()
    } catch (reason) {
      setError(message(reason, '上传附件失败'))
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className='grid gap-7 xl:grid-cols-[minmax(0,0.85fr)_minmax(0,1.15fr)]'>
      <section className='rounded-3xl border border-slate-200/70 bg-white/80 p-5 shadow-sm'>
        <div className='flex items-center gap-2'>
          <FileUp className='h-5 w-5 text-[var(--color-brand)]' />
          <h2 className='font-semibold text-slate-900'>上传私有附件</h2>
        </div>
        <p className='mt-2 text-sm leading-6 text-slate-500'>
          第一版支持图片、PDF 与纯文本；文件保存在本地上传目录，数据库仅保存不透明存储标识。
        </p>
        <form onSubmit={submit} className='mt-5 space-y-4'>
          <label className='block text-sm font-medium text-slate-700'>
            选择文件
            <input
              id='attachment-file'
              type='file'
              disabled={busy}
              accept='image/png,image/jpeg,image/webp,application/pdf,text/plain'
              onChange={(event) => setFile(event.target.files?.[0] ?? null)}
              className='mt-2 block w-full rounded-lg border border-slate-200 bg-white px-3 py-2.5 text-sm file:mr-3 file:rounded-lg file:border-0 file:bg-slate-100 file:px-3 file:py-1.5 file:text-sm'
            />
          </label>
          {file ? (
            <div className='rounded-2xl bg-slate-50 p-3 text-sm text-slate-600'>
              {file.name} · {file.type || '未知类型'} · {formatBytes(file.size)}
            </div>
          ) : null}
          {error ? <p role='alert' className='text-sm text-red-600'>{error}</p> : null}
          <button
            disabled={busy || !file}
            className='inline-flex items-center gap-2 rounded-lg bg-[var(--color-brand)] px-5 py-2.5 text-sm font-medium text-white disabled:opacity-45'
          >
            <FileUp className='h-4 w-4' />
            {busy ? '上传中…' : '上传附件'}
          </button>
        </form>
      </section>

      <section className='rounded-3xl border border-slate-200/70 bg-white/80 p-5 shadow-sm'>
        <div className='flex flex-col gap-3 border-b border-slate-100 pb-4 sm:flex-row sm:items-center sm:justify-between'>
          <div>
            <h2 className='font-semibold text-slate-900'>附件列表</h2>
            <p className='mt-1 text-sm text-slate-500'>仅管理员可见；公开接口不返回附件。</p>
          </div>
          <div className='flex gap-2'>
            <select
              value={status}
              aria-label='附件状态'
              onChange={(event) => {
                const next = event.target.value as AttachmentStatus | ''
                setStatus(next)
                void load(next)
              }}
              className='rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm'
            >
              <option value='active'>可用</option>
              <option value='missing'>文件缺失</option>
              <option value='deleted'>已删除</option>
              <option value=''>全部</option>
            </select>
            <button
              type='button'
              onClick={() => void load()}
              className='inline-flex items-center gap-2 rounded-lg border border-slate-200 px-3 py-2 text-sm text-slate-600'
            >
              <RefreshCcw className='h-4 w-4' />
              刷新
            </button>
          </div>
        </div>
        {loading ? <FeatureState state={{ kind: 'loading', label: '正在加载附件', rows: 3 }} /> : null}
        {!loading && error && items.length === 0 ? <FeatureState state={{ kind: 'error', title: '附件加载失败', description: error, retry: () => void load() }} /> : null}
        {!loading && !error && items.length === 0 ? <FeatureState state={{ kind: 'empty', title: '暂无附件', description: '上传学习资料后，可将附件关联到题目或错题。' }} /> : null}
        {items.map((item) => (
          <Link key={item.id} href={`/manage/attachments/${item.id}`} className='group flex items-center gap-4 border-b border-slate-100 py-4 last:border-b-0'>
            <span className='min-w-0 flex-1'>
              <span className='block truncate font-medium text-slate-800'>{item.original_name}</span>
              <span className='mt-1 block text-xs text-slate-400'>
                {item.mime_type} · {formatBytes(item.size_bytes)} · {attachmentStatusLabel(item.status)} · {attachmentVisibilityLabel(item.visibility)}
              </span>
            </span>
            <ArrowRight className='h-4 w-4 text-slate-300 group-hover:text-[var(--color-brand)]' />
          </Link>
        ))}
      </section>
    </div>
  )
}
