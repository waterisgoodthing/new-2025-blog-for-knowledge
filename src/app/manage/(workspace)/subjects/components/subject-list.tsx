'use client'

import Link from 'next/link'
import { FormEvent, useEffect, useState } from 'react'
import { ArrowRight, Plus } from 'lucide-react'

import { ApiError } from '@/lib/api/client'
import {
  createSubject,
  listSubjects,
  type Subject,
} from '@/lib/api/taxonomy'

function messageOf(reason: unknown): string {
  return reason instanceof ApiError || reason instanceof Error
    ? reason.message
    : '请求失败，请稍后重试'
}

export function SubjectList() {
  const [subjects, setSubjects] = useState<Subject[]>([])
  const [name, setName] = useState('')
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const load = async () => {
    setLoading(true)
    setError(null)
    try {
      setSubjects(await listSubjects())
    } catch (reason) {
      setError(messageOf(reason))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void load()
  }, [])

  const submit = async (event: FormEvent) => {
    event.preventDefault()
    if (!name.trim()) return
    setSaving(true)
    setError(null)
    try {
      const created = await createSubject({ name })
      setSubjects((current) => [...current, created])
      setName('')
    } catch (reason) {
      setError(messageOf(reason))
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className='grid gap-8 lg:grid-cols-[minmax(0,1fr)_19rem]'>
      <section aria-labelledby='subject-list-title'>
        <div className='flex items-center justify-between border-b border-slate-200/70 pb-3'>
          <h2 id='subject-list-title' className='font-medium text-slate-800'>全部科目</h2>
          <span className='text-xs text-slate-400'>{subjects.length} 项</span>
        </div>
        {loading ? <p className='py-8 text-sm text-slate-400'>正在加载科目…</p> : null}
        {!loading && subjects.length === 0 ? (
          <p className='py-8 text-sm text-slate-500'>还没有科目，可从右侧开始创建。</p>
        ) : null}
        <div>
          {subjects.map((subject) => (
            <Link
              key={subject.id}
              href={`/manage/subjects/${subject.id}`}
              className='group flex items-center gap-4 border-b border-slate-200/55 py-4 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-brand)]/40'
            >
              <span className='min-w-0 flex-1'>
                <span className='block font-medium text-slate-800'>{subject.name}</span>
                <span className='mt-1 block truncate text-xs text-slate-400'>
                  {subject.description || '暂无说明'} · {subject.is_active ? '启用' : '停用'}
                </span>
              </span>
              <ArrowRight className='h-4 w-4 text-slate-300 group-hover:text-[var(--color-brand)]' aria-hidden='true' />
            </Link>
          ))}
        </div>
      </section>

      <form onSubmit={submit} className='h-fit rounded-2xl border border-slate-200/70 bg-white/55 p-5'>
        <h2 className='font-medium text-slate-800'>新建科目</h2>
        <label className='mt-4 block text-sm text-slate-600'>
          名称
          <input
            value={name}
            onChange={(event) => setName(event.target.value)}
            maxLength={100}
            className='mt-2 w-full rounded-xl border border-slate-200 bg-white px-3 py-2.5 outline-none focus:border-[var(--color-brand)]'
          />
        </label>
        <button
          type='submit'
          disabled={saving || !name.trim()}
          className='mt-4 inline-flex w-full items-center justify-center gap-2 rounded-xl bg-[var(--color-brand)] px-4 py-2.5 text-sm font-medium text-white disabled:opacity-45'
        >
          <Plus className='h-4 w-4' aria-hidden='true' />
          {saving ? '正在创建…' : '创建科目'}
        </button>
        {error ? <p role='alert' className='mt-3 text-sm text-red-600'>{error}</p> : null}
      </form>
    </div>
  )
}
