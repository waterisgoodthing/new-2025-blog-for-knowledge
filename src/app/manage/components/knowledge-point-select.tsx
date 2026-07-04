'use client'

import { useEffect, useId, useState } from 'react'

import {
  listKnowledgePoints,
  type KnowledgePoint,
} from '@/lib/api/taxonomy'

interface KnowledgePointSelectProps {
  value: number | null
  onChange: (value: number | null) => void
  subjectId?: number
  disabled?: boolean
  label?: string
}

interface KnowledgePointMultiSelectProps {
  values: number[]
  onChange: (values: number[]) => void
  subjectId?: number
  disabled?: boolean
  label?: string
}

export function KnowledgePointSelect({
  value,
  onChange,
  subjectId,
  disabled = false,
  label = '知识点',
}: KnowledgePointSelectProps) {
  const selectId = useId()
  const [options, setOptions] = useState<KnowledgePoint[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let active = true
    setLoading(true)
    setError(null)

    listKnowledgePoints({ subject_id: subjectId, is_active: true })
      .then((items) => {
        if (active) setOptions(items)
      })
      .catch((reason: unknown) => {
        if (active) {
          setOptions([])
          setError(reason instanceof Error ? reason.message : '知识点加载失败')
        }
      })
      .finally(() => {
        if (active) setLoading(false)
      })

    return () => {
      active = false
    }
  }, [subjectId])

  return (
    <label htmlFor={selectId} className='block'>
      <span className='mb-2 block text-sm font-medium text-slate-700'>{label}</span>
      <select
        id={selectId}
        value={value ?? ''}
        disabled={disabled || loading}
        onChange={(event) => {
          const nextValue = event.target.value
          onChange(nextValue ? Number(nextValue) : null)
        }}
        className='w-full rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-sm text-slate-900 outline-none transition focus:border-[var(--color-brand)] disabled:cursor-not-allowed disabled:bg-slate-50 disabled:text-slate-400'
      >
        <option value=''>
          {loading ? '正在加载…' : options.length ? '请选择知识点' : '暂无可用知识点'}
        </option>
        {options.map((option) => (
          <option key={option.id} value={option.id}>
            {option.name}
          </option>
        ))}
      </select>
      {error ? <span className='mt-1.5 block text-xs text-red-600'>{error}</span> : null}
    </label>
  )
}

export function KnowledgePointMultiSelect({
  values,
  onChange,
  subjectId,
  disabled = false,
  label = '知识点',
}: KnowledgePointMultiSelectProps) {
  const [options, setOptions] = useState<KnowledgePoint[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let active = true
    setLoading(true)
    setError(null)
    listKnowledgePoints({ subject_id: subjectId, is_active: true })
      .then((items) => {
        if (active) setOptions(items)
      })
      .catch((reason: unknown) => {
        if (active) setError(reason instanceof Error ? reason.message : '知识点加载失败')
      })
      .finally(() => {
        if (active) setLoading(false)
      })
    return () => {
      active = false
    }
  }, [subjectId])

  return (
    <fieldset disabled={disabled || loading}>
      <legend className='mb-2 text-sm font-medium text-slate-700'>{label}</legend>
      <div className='flex flex-wrap gap-2'>
        {options.map((option) => {
          const checked = values.includes(option.id)
          return (
            <label
              key={option.id}
              className='inline-flex cursor-pointer items-center gap-2 rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm text-slate-700'
            >
              <input
                type='checkbox'
                checked={checked}
                onChange={() => {
                  onChange(
                    checked
                      ? values.filter((value) => value !== option.id)
                      : [...values, option.id],
                  )
                }}
              />
              {option.name}
            </label>
          )
        })}
        {!loading && options.length === 0 ? (
          <span className='text-sm text-slate-400'>暂无可选知识点</span>
        ) : null}
      </div>
      {loading ? <p className='mt-2 text-xs text-slate-400'>正在加载知识点…</p> : null}
      {error ? <p className='mt-2 text-xs text-red-600'>{error}</p> : null}
    </fieldset>
  )
}
