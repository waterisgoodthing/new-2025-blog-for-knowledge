'use client'

import Link from 'next/link'
import { FormEvent, useEffect, useState } from 'react'
import { ArrowLeft, Trash2 } from 'lucide-react'
import { useRouter } from 'next/navigation'

import {
  deleteKnowledgePoint,
  getKnowledgePoint,
  listChapters,
  updateKnowledgePoint,
  type Chapter,
  type KnowledgePoint,
} from '@/lib/api/taxonomy'

export function KnowledgePointEditor({ knowledgePointId }: { knowledgePointId: number }) {
  const router = useRouter()
  const [point, setPoint] = useState<KnowledgePoint | null>(null)
  const [chapters, setChapters] = useState<Chapter[]>([])
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)

  useEffect(() => {
    getKnowledgePoint(knowledgePointId)
      .then(async (item) => {
        setPoint(item)
        setChapters(await listChapters({ subject_id: item.subject_id }))
      })
      .catch((reason: unknown) => setError(reason instanceof Error ? reason.message : '加载失败'))
  }, [knowledgePointId])

  const submit = async (event: FormEvent) => {
    event.preventDefault()
    if (!point) return
    setBusy(true)
    setError(null)
    try {
      setPoint(await updateKnowledgePoint(point.id, {
        name: point.name,
        description: point.description,
        chapter_id: point.chapter_id,
        is_active: point.is_active,
        sort_order: point.sort_order,
      }))
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : '保存失败')
    } finally {
      setBusy(false)
    }
  }

  if (!point) return <p className='text-sm text-slate-500'>{error || '正在加载知识点…'}</p>

  return (
    <div className='max-w-2xl space-y-7'>
      <Link href={`/manage/subjects/${point.subject_id}`} className='inline-flex items-center gap-2 text-sm text-slate-500'>
        <ArrowLeft className='h-4 w-4' />返回所属科目
      </Link>
      <form onSubmit={submit} className='space-y-5 rounded-2xl border border-slate-200/70 p-5'>
        <h1 className='text-2xl font-semibold text-slate-900'>编辑知识点</h1>
        <label className='block text-sm text-slate-600'>名称
          <input value={point.name} onChange={(event) => setPoint({ ...point, name: event.target.value })} className='mt-2 w-full rounded-xl border border-slate-200 px-3 py-2.5' />
        </label>
        <label className='block text-sm text-slate-600'>章节
          <select value={point.chapter_id ?? ''} onChange={(event) => setPoint({ ...point, chapter_id: event.target.value ? Number(event.target.value) : null })} className='mt-2 w-full rounded-xl border border-slate-200 px-3 py-2.5'>
            <option value=''>不指定章节</option>
            {chapters.map((chapter) => <option key={chapter.id} value={chapter.id}>{chapter.name}</option>)}
          </select>
        </label>
        <label className='block text-sm text-slate-600'>说明
          <textarea value={point.description ?? ''} onChange={(event) => setPoint({ ...point, description: event.target.value || null })} rows={4} className='mt-2 w-full rounded-xl border border-slate-200 px-3 py-2.5' />
        </label>
        <div className='grid gap-4 sm:grid-cols-2'>
          <label className='text-sm text-slate-600'>排序
            <input type='number' value={point.sort_order} onChange={(event) => setPoint({ ...point, sort_order: Number(event.target.value) })} className='mt-2 w-full rounded-xl border border-slate-200 px-3 py-2.5' />
          </label>
          <label className='flex items-end gap-2 pb-3 text-sm text-slate-600'>
            <input type='checkbox' checked={point.is_active} onChange={(event) => setPoint({ ...point, is_active: event.target.checked })} />启用
          </label>
        </div>
        {error ? <p role='alert' className='text-sm text-red-600'>{error}</p> : null}
        <div className='flex justify-between'>
          <button type='button' onClick={async () => {
            if (!window.confirm('确认删除这个知识点？有关联数据时系统会拒绝删除。')) return
            setBusy(true)
            try {
              await deleteKnowledgePoint(point.id)
              router.push(`/manage/subjects/${point.subject_id}`)
            } catch (reason) {
              setError(reason instanceof Error ? reason.message : '删除失败')
              setBusy(false)
            }
          }} className='inline-flex items-center gap-2 rounded-xl border border-red-200 px-3 py-2 text-sm text-red-600'>
            <Trash2 className='h-4 w-4' />删除
          </button>
          <button disabled={busy || !point.name.trim()} className='rounded-xl bg-[var(--color-brand)] px-5 py-2 text-sm text-white disabled:opacity-45'>
            {busy ? '处理中…' : '保存'}
          </button>
        </div>
      </form>
    </div>
  )
}
