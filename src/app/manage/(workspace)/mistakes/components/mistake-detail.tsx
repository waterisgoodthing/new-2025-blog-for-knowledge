'use client'

import Link from 'next/link'
import { FormEvent, useEffect, useState } from 'react'
import { Archive, ArrowLeft, CheckCircle2, XCircle } from 'lucide-react'
import { useRouter } from 'next/navigation'

import {
  archiveMistake,
  convertMistakeDraft,
  getMistake,
  getMistakeDraft,
  rejectMistakeDraft,
  updateMistake,
  updateMistakeDraft,
  type Mistake,
  type MistakeDraft,
  type MistakeReason,
} from '@/lib/api/mistakes'
import { attachmentVisibilityLabel, questionStatusLabel } from '@/lib/manage-display'
import type { Difficulty } from '@/lib/api/questions'
import { ManageFormPanel } from '../../../components/manage-form-panel'
import { KnowledgePointMultiSelect } from '../../../components/knowledge-point-select'

const reasonLabels: Record<MistakeReason, string> = {
  concept: '概念理解',
  calculation: '计算过程',
  reading: '审题阅读',
  careless: '粗心失误',
  unknown: '未分类',
}

function errorMessage(reason: unknown, fallback: string) {
  return reason instanceof Error ? reason.message : fallback
}

export function MistakeDetail({ id, kind }: { id: string; kind: 'draft' | 'mistake' }) {
  const router = useRouter()
  const [draft, setDraft] = useState<MistakeDraft | null>(null)
  const [mistake, setMistake] = useState<Mistake | null>(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    setError(null)
    const load = kind === 'draft' ? getMistakeDraft(id) : getMistake(id)
    load
      .then((record) => {
        if (kind === 'draft') setDraft(record as MistakeDraft)
        else setMistake(record as Mistake)
      })
      .catch((reason: unknown) => setError(errorMessage(reason, '加载错题失败')))
  }, [id, kind])

  const record = kind === 'draft' ? draft : mistake
  if (!record) {
    return (
      <div className='max-w-3xl space-y-5'>
        <BackLink />
        <p className='text-sm text-slate-500'>{error || '正在加载错题…'}</p>
      </div>
    )
  }

  const save = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setBusy(true)
    setError(null)
    try {
      if (kind === 'draft' && draft) {
        setDraft(await updateMistakeDraft(draft.draft_item_id, {
          version: draft.version,
          my_answer: draft.my_answer,
          reason_category: draft.reason_category,
          mistake_reason: draft.mistake_reason,
          difficulty: draft.difficulty,
          knowledge_point_ids: draft.knowledge_point_ids,
        }))
      } else if (mistake) {
        setMistake(await updateMistake(mistake.id, {
          version: mistake.version,
          my_answer: mistake.my_answer,
          analysis: mistake.analysis,
          reason_category: mistake.reason_category,
          mistake_reason: mistake.mistake_reason,
          difficulty: mistake.difficulty,
          knowledge_point_ids: mistake.knowledge_point_ids,
        }))
      }
    } catch (reason) {
      setError(errorMessage(reason, '保存失败'))
    } finally {
      setBusy(false)
    }
  }

  const subjectId = record.subject_id
  const active = kind === 'draft'
    ? draft?.status === 'pending' || draft?.status === 'needs_fix'
    : mistake?.status === 'active'

  return (
    <div className='max-w-4xl space-y-7'>
      <BackLink />
      <header>
        <p className='text-xs font-medium tracking-[0.16em] text-[var(--color-brand)]/75'>
          {kind === 'draft'
            ? `错题草稿 · ${draft?.status === 'pending' ? '待确认' : draft?.status === 'needs_fix' ? '需修正' : draft?.status === 'rejected' ? '已拒绝' : '已入库'}`
            : `正式错题 · ${questionStatusLabel(mistake?.status ?? '')}`} · {attachmentVisibilityLabel(kind === 'mistake' ? mistake?.visibility ?? 'private' : 'private')} · 版本 {record.version}
        </p>
        <h1 className='mt-2 text-2xl font-semibold text-slate-900'>
          {record.title || '未命名错题'}
        </h1>
        <p className='mt-2 text-sm text-slate-500'>
          {kind === 'draft' ? '草稿确认后会原子创建正式错题与复习项。' : `复习项：${mistake?.review_item_id}`}
        </p>
      </header>

      <ManageFormPanel
        variant='heavy'
        onSubmit={save}
        error={error ?? undefined}
        actions={active ? (
          <>
            <div className='mr-auto flex gap-3'>
              {kind === 'draft' && draft ? (
                <>
                  <button
                    type='button'
                    disabled={busy}
                    onClick={async () => {
                      if (!window.confirm('确认将这份错题草稿转为正式错题？系统会同时创建复习项。')) return
                      setBusy(true)
                      setError(null)
                      try {
                        const converted = await convertMistakeDraft(draft.draft_item_id, draft.version)
                        router.replace(`/manage/mistakes/${converted.id}?kind=mistake`)
                      } catch (reason) {
                        setError(errorMessage(reason, '确认草稿失败'))
                        setBusy(false)
                      }
                    }}
                    className='inline-flex items-center gap-2 rounded-lg bg-emerald-600 px-4 py-2 text-sm text-white disabled:opacity-45'
                  >
                    <CheckCircle2 className='h-4 w-4' />确认入错题
                  </button>
                  <button
                    type='button'
                    disabled={busy}
                    onClick={async () => {
                      if (!window.confirm('确认拒绝这份错题草稿？')) return
                      setBusy(true)
                      try {
                        await rejectMistakeDraft(draft.draft_item_id, draft.version)
                        router.push('/manage/mistakes')
                      } catch (reason) {
                        setError(errorMessage(reason, '拒绝草稿失败'))
                        setBusy(false)
                      }
                    }}
                    className='inline-flex items-center gap-2 rounded-lg border border-rose-200 px-4 py-2 text-sm text-rose-700 disabled:opacity-45'
                  >
                    <XCircle className='h-4 w-4' />拒绝
                  </button>
                </>
              ) : null}
              {kind === 'mistake' && mistake ? (
                <button
                  type='button'
                  disabled={busy}
                  onClick={async () => {
                    if (!window.confirm('确认归档这道错题？对应复习项会暂停。')) return
                    setBusy(true)
                    try {
                      await archiveMistake(mistake.id, mistake.version)
                      router.push('/manage/mistakes')
                    } catch (reason) {
                      setError(errorMessage(reason, '归档失败'))
                      setBusy(false)
                    }
                  }}
                  className='inline-flex items-center gap-2 rounded-lg border border-amber-200 px-4 py-2 text-sm text-amber-700 disabled:opacity-45'
                >
                  <Archive className='h-4 w-4' />归档
                </button>
              ) : null}
            </div>
            <button
              disabled={busy}
              className='rounded-lg bg-[var(--color-brand)] px-5 py-2 text-sm text-white disabled:opacity-45'
            >
              {busy ? '处理中…' : '保存'}
            </button>
          </>
        ) : undefined}
      >
        <section className='rounded-lg bg-slate-50 p-4'>
          <h2 className='text-sm font-semibold text-slate-800'>题干快照</h2>
          <p className='mt-2 whitespace-pre-wrap text-sm leading-6 text-slate-600'>{record.question_text}</p>
        </section>

        <div className='grid gap-4 md:grid-cols-2'>
          <label className='block text-sm font-medium text-slate-700'>
            我的答案
            <textarea
              disabled={!active || busy}
              value={record.my_answer ?? ''}
              onChange={(event) => {
                if (kind === 'draft' && draft) setDraft({ ...draft, my_answer: event.target.value || null })
                if (kind === 'mistake' && mistake) setMistake({ ...mistake, my_answer: event.target.value || null })
              }}
              rows={4}
              className='mt-2 w-full rounded-lg border border-slate-200 px-3 py-2.5 text-sm'
            />
          </label>
          <label className='block text-sm font-medium text-slate-700'>
            {kind === 'draft' ? '解析快照' : '解析'}
            <textarea
              disabled={kind === 'draft' || !active || busy}
              value={kind === 'draft' ? draft?.explanation_snapshot ?? '' : mistake?.analysis ?? ''}
              onChange={(event) => {
                if (mistake) setMistake({ ...mistake, analysis: event.target.value || null })
              }}
              rows={4}
              className='mt-2 w-full rounded-lg border border-slate-200 px-3 py-2.5 text-sm disabled:bg-slate-50'
            />
          </label>
        </div>

        <div className='grid gap-4 md:grid-cols-2'>
          <label className='block text-sm font-medium text-slate-700'>
            错因类型
            <select
              disabled={!active || busy}
              value={record.reason_category}
              onChange={(event) => {
                const next = event.target.value as MistakeReason
                if (draft) setDraft({ ...draft, reason_category: next })
                if (mistake) setMistake({ ...mistake, reason_category: next })
              }}
              className='mt-2 w-full rounded-lg border border-slate-200 bg-white px-3 py-2.5 text-sm'
            >
              {Object.entries(reasonLabels).map(([value, label]) => (
                <option key={value} value={value}>{label}</option>
              ))}
            </select>
          </label>
          <label className='block text-sm font-medium text-slate-700'>
            难度
            <select
              disabled={!active || busy}
              value={record.difficulty ?? ''}
              onChange={(event) => {
                const next = (event.target.value || null) as Difficulty | null
                if (draft) setDraft({ ...draft, difficulty: next })
                if (mistake) setMistake({ ...mistake, difficulty: next })
              }}
              className='mt-2 w-full rounded-lg border border-slate-200 bg-white px-3 py-2.5 text-sm'
            >
              <option value=''>未设置</option>
              <option value='easy'>简单</option>
              <option value='medium'>中等</option>
              <option value='hard'>困难</option>
            </select>
          </label>
        </div>

        <label className='block text-sm font-medium text-slate-700'>
          错因说明
          <textarea
            disabled={!active || busy}
            value={record.mistake_reason ?? ''}
            onChange={(event) => {
              const next = event.target.value || null
              if (draft) setDraft({ ...draft, mistake_reason: next })
              if (mistake) setMistake({ ...mistake, mistake_reason: next })
            }}
            rows={4}
            className='mt-2 w-full rounded-lg border border-slate-200 px-3 py-2.5 text-sm'
          />
        </label>

        <KnowledgePointMultiSelect
          disabled={!active || busy}
          subjectId={subjectId}
          values={record.knowledge_point_ids}
          onChange={(values) => {
            if (draft) setDraft({ ...draft, knowledge_point_ids: values })
            if (mistake) setMistake({ ...mistake, knowledge_point_ids: values })
          }}
        />
      </ManageFormPanel>
    </div>
  )
}

function BackLink() {
  return (
    <Link href='/manage/mistakes' className='inline-flex items-center gap-2 text-sm text-slate-500'>
      <ArrowLeft className='h-4 w-4' />
      返回错题
    </Link>
  )
}
