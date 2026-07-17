'use client'

import { FormEvent, useEffect, useState } from 'react'
import { Plus } from 'lucide-react'

import { ApiError } from '@/lib/api/client'
import {
  createSubject,
  listSubjects,
  type Subject,
} from '@/lib/api/taxonomy'

import { ManageEmptyState } from '../../../components/manage-empty-state'
import { ManageFormPanel } from '../../../components/manage-form-panel'
import { ManageStatusBadge } from '../../../components/manage-status-badge'
import {
  ManageListRow,
  ManageTableContainer,
} from '../../../components/manage-table-container'

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

  const submit = async (event: FormEvent<HTMLFormElement>) => {
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
        <ManageTableContainer
          header={
            <h2 id='subject-list-title' className='font-medium text-slate-800'>
              全部科目
            </h2>
          }
          count={subjects.length}
          countLabel='项'
        >
          {loading ? (
            <ManageEmptyState variant='loading' message='正在加载科目…' />
          ) : null}
          {!loading && subjects.length === 0 && !error ? (
            <ManageEmptyState
              variant='empty'
              message='还没有科目，可从右侧开始创建。'
            />
          ) : null}
          {!loading && subjects.length === 0 && error ? (
            <ManageEmptyState variant='error' message={error} />
          ) : null}
          {subjects.map((subject) => (
            <ManageListRow
              key={subject.id}
              href={`/manage/subjects/${subject.id}`}
              title={subject.name}
              meta={subject.description || '暂无说明'}
            >
              <ManageStatusBadge tone={subject.status === 'active' ? 'success' : 'neutral'}>
                {subject.status === 'active' ? '启用' : '归档'}
              </ManageStatusBadge>
            </ManageListRow>
          ))}
        </ManageTableContainer>
      </section>

      <ManageFormPanel
        title='新建科目'
        error={error && subjects.length > 0 ? error : undefined}
        onSubmit={submit}
        className='h-fit'
      >
        <label className='block text-sm text-slate-600'>
          名称
          <input
            value={name}
            onChange={(event) => setName(event.target.value)}
            maxLength={100}
            className='mt-2 w-full rounded-lg border border-slate-200 bg-white px-3 py-2.5 outline-none focus:border-[var(--color-brand)]'
          />
        </label>
        <button
          type='submit'
          disabled={saving || !name.trim()}
          className='inline-flex w-full items-center justify-center gap-2 rounded-lg bg-[var(--color-brand)] px-4 py-2.5 text-sm font-medium text-white disabled:opacity-45'
        >
          <Plus className='h-4 w-4' aria-hidden='true' />
          {saving ? '正在创建…' : '创建科目'}
        </button>
      </ManageFormPanel>
    </div>
  )
}
