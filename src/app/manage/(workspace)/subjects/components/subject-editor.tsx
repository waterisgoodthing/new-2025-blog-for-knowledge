'use client'

import Link from 'next/link'
import { FormEvent, useEffect, useState } from 'react'
import { ArrowLeft, ArrowRight, Plus, Trash2 } from 'lucide-react'
import { useRouter } from 'next/navigation'

import { ApiError } from '@/lib/api/client'
import {
  createChapter,
  createKnowledgePoint,
  deleteChapter,
  deleteSubject,
  getSubject,
  listChapters,
  listKnowledgePoints,
  updateSubject,
  type Chapter,
  type KnowledgePoint,
  type Subject,
} from '@/lib/api/taxonomy'

function messageOf(reason: unknown): string {
  return reason instanceof ApiError || reason instanceof Error ? reason.message : '请求失败'
}

export function SubjectEditor({ subjectId }: { subjectId: number }) {
  const router = useRouter()
  const [subject, setSubject] = useState<Subject | null>(null)
  const [chapters, setChapters] = useState<Chapter[]>([])
  const [points, setPoints] = useState<KnowledgePoint[]>([])
  const [chapterName, setChapterName] = useState('')
  const [pointName, setPointName] = useState('')
  const [pointChapterId, setPointChapterId] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const load = async () => {
    setError(null)
    try {
      const [nextSubject, nextChapters, nextPoints] = await Promise.all([
        getSubject(subjectId),
        listChapters({ subject_id: subjectId }),
        listKnowledgePoints({ subject_id: subjectId }),
      ])
      setSubject(nextSubject)
      setChapters(nextChapters)
      setPoints(nextPoints)
    } catch (reason) {
      setError(messageOf(reason))
    }
  }

  useEffect(() => {
    void load()
  }, [subjectId])

  const saveSubject = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (!subject) return
    setBusy(true)
    try {
      setSubject(await updateSubject(subject.id, {
        name: subject.name,
        description: subject.description,
        is_active: subject.is_active,
        sort_order: subject.sort_order,
      }))
    } catch (reason) {
      setError(messageOf(reason))
    } finally {
      setBusy(false)
    }
  }

  const addChapter = async (event: FormEvent) => {
    event.preventDefault()
    if (!chapterName.trim()) return
    setBusy(true)
    try {
      const created = await createChapter({ subject_id: subjectId, name: chapterName })
      setChapters((current) => [...current, created])
      setChapterName('')
    } catch (reason) {
      setError(messageOf(reason))
    } finally {
      setBusy(false)
    }
  }

  const addPoint = async (event: FormEvent) => {
    event.preventDefault()
    if (!pointName.trim()) return
    setBusy(true)
    try {
      const created = await createKnowledgePoint({
        subject_id: subjectId,
        chapter_id: pointChapterId ? Number(pointChapterId) : null,
        name: pointName,
      })
      setPoints((current) => [...current, created])
      setPointName('')
    } catch (reason) {
      setError(messageOf(reason))
    } finally {
      setBusy(false)
    }
  }

  if (!subject) {
    return (
      <div>
        <Link href='/manage/subjects' className='text-sm text-slate-500'>← 返回科目</Link>
        <p className='mt-8 text-sm text-slate-500'>{error || '正在加载…'}</p>
      </div>
    )
  }

  return (
    <div className='space-y-9'>
      <Link href='/manage/subjects' className='inline-flex items-center gap-2 text-sm text-slate-500 hover:text-slate-800'>
        <ArrowLeft className='h-4 w-4' aria-hidden='true' />返回科目
      </Link>
      <form onSubmit={saveSubject} className='grid gap-4 rounded-2xl border border-slate-200/70 p-5 sm:grid-cols-2'>
        <h1 className='text-2xl font-semibold text-slate-900 sm:col-span-2'>编辑科目</h1>
        <label className='text-sm text-slate-600'>名称
          <input value={subject.name} onChange={(event) => setSubject({ ...subject, name: event.target.value })} className='mt-2 w-full rounded-xl border border-slate-200 px-3 py-2.5' />
        </label>
        <label className='text-sm text-slate-600'>排序
          <input type='number' value={subject.sort_order} onChange={(event) => setSubject({ ...subject, sort_order: Number(event.target.value) })} className='mt-2 w-full rounded-xl border border-slate-200 px-3 py-2.5' />
        </label>
        <label className='text-sm text-slate-600 sm:col-span-2'>说明
          <textarea value={subject.description ?? ''} onChange={(event) => setSubject({ ...subject, description: event.target.value || null })} rows={3} className='mt-2 w-full rounded-xl border border-slate-200 px-3 py-2.5' />
        </label>
        <label className='flex items-center gap-2 text-sm text-slate-600'>
          <input type='checkbox' checked={subject.is_active} onChange={(event) => setSubject({ ...subject, is_active: event.target.checked })} />启用
        </label>
        <div className='flex justify-end gap-3'>
          <button type='button' onClick={async () => {
            if (!window.confirm('确认删除这个科目？有关联数据时系统会拒绝删除。')) return
            setBusy(true)
            try {
              await deleteSubject(subject.id)
              router.push('/manage/subjects')
            } catch (reason) {
              setError(messageOf(reason))
              setBusy(false)
            }
          }} className='inline-flex items-center gap-2 rounded-xl border border-red-200 px-3 py-2 text-sm text-red-600'>
            <Trash2 className='h-4 w-4' />删除
          </button>
          <button disabled={busy} className='rounded-xl bg-[var(--color-brand)] px-4 py-2 text-sm text-white disabled:opacity-50'>保存</button>
        </div>
      </form>

      {error ? <p role='alert' className='rounded-xl bg-red-50 px-4 py-3 text-sm text-red-700'>{error}</p> : null}

      <div className='grid gap-8 lg:grid-cols-2'>
        <section>
          <h2 className='font-medium text-slate-800'>章节</h2>
          <form onSubmit={addChapter} className='mt-3 flex gap-2'>
            <input value={chapterName} onChange={(event) => setChapterName(event.target.value)} placeholder='章节名称' className='min-w-0 flex-1 rounded-xl border border-slate-200 px-3 py-2' />
            <button disabled={busy || !chapterName.trim()} className='rounded-xl border border-slate-200 px-3 disabled:opacity-40' aria-label='新增章节'><Plus className='h-4 w-4' /></button>
          </form>
          {chapters.length === 0 ? <p className='py-5 text-sm text-slate-400'>暂无章节。</p> : null}
          {chapters.map((chapter) => (
            <div key={chapter.id} className='flex items-center border-b border-slate-200/60 py-3 text-sm'>
              <span className='flex-1 text-slate-700'>{chapter.name}</span>
              <button type='button' aria-label={`删除章节 ${chapter.name}`} onClick={async () => {
                if (!window.confirm(`确认删除章节“${chapter.name}”？`)) return
                try {
                  await deleteChapter(chapter.id)
                  setChapters((current) => current.filter((item) => item.id !== chapter.id))
                } catch (reason) {
                  setError(messageOf(reason))
                }
              }} className='p-2 text-slate-400 hover:text-red-600'><Trash2 className='h-4 w-4' /></button>
            </div>
          ))}
        </section>

        <section>
          <h2 className='font-medium text-slate-800'>知识点</h2>
          <form onSubmit={addPoint} className='mt-3 grid gap-2 sm:grid-cols-[1fr_1fr_auto]'>
            <input value={pointName} onChange={(event) => setPointName(event.target.value)} placeholder='知识点名称' className='min-w-0 rounded-xl border border-slate-200 px-3 py-2' />
            <select value={pointChapterId} onChange={(event) => setPointChapterId(event.target.value)} className='min-w-0 rounded-xl border border-slate-200 px-3 py-2 text-sm'>
              <option value=''>不指定章节</option>
              {chapters.map((chapter) => <option key={chapter.id} value={chapter.id}>{chapter.name}</option>)}
            </select>
            <button disabled={busy || !pointName.trim()} className='rounded-xl border border-slate-200 px-3 disabled:opacity-40' aria-label='新增知识点'><Plus className='h-4 w-4' /></button>
          </form>
          {points.length === 0 ? <p className='py-5 text-sm text-slate-400'>暂无知识点。</p> : null}
          {points.map((point) => (
            <Link key={point.id} href={`/manage/knowledge-points/${point.id}`} className='flex items-center border-b border-slate-200/60 py-3 text-sm'>
              <span className='flex-1 text-slate-700'>{point.name}</span>
              <ArrowRight className='h-4 w-4 text-slate-300' />
            </Link>
          ))}
        </section>
      </div>
    </div>
  )
}
