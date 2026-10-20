'use client'

import Link from 'next/link'
import { FormEvent, useEffect, useMemo, useState } from 'react'
import { Archive, ArrowLeft, Plus } from 'lucide-react'

import { ApiError } from '@/lib/api/client'
import {
  createKnowledgePoint,
  getSubject,
  getSubjectKnowledgeTree,
  updateSubject,
  type KnowledgePointTreeNode,
  type KnowledgeTree,
  type Subject,
} from '@/lib/api/taxonomy'
import { ManageEmptyState } from '../../../components/manage-empty-state'
import { ManageFormPanel } from '../../../components/manage-form-panel'
import { ManagePanel } from '../../../components/manage-panel'
import { ManageStatusBadge } from '../../../components/manage-status-badge'

function messageOf(reason: unknown): string {
  return reason instanceof ApiError || reason instanceof Error
    ? reason.message
    : '请求失败，请稍后重试'
}

function flattenTree(nodes: KnowledgePointTreeNode[], depth = 0): Array<KnowledgePointTreeNode & { depth: number }> {
  return nodes.flatMap((node) => [
    { ...node, depth },
    ...flattenTree(node.children, depth + 1),
  ])
}

function TreeRows({ nodes }: { nodes: KnowledgePointTreeNode[] }) {
  if (nodes.length === 0) {
    return <ManageEmptyState variant='empty' message='还没有知识点。' />
  }

  return (
    <div className='divide-y divide-[var(--admin-border)]/60'>
      {flattenTree(nodes).map((node) => (
        <Link
          key={node.id}
          href={`/manage/knowledge-points/${node.id}`}
          className='flex items-center justify-between gap-3 py-3 text-sm hover:bg-[var(--admin-surface-subtle)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--brand)]/45'
          style={{ paddingLeft: `${node.depth * 18}px` }}
        >
          <span className='min-w-0 truncate text-[var(--admin-text-primary)]'>{node.name}</span>
          <ManageStatusBadge tone={node.status === 'active' ? 'success' : 'neutral'}>
            {node.status === 'active' ? '启用' : '归档'}
          </ManageStatusBadge>
        </Link>
      ))}
    </div>
  )
}

export function SubjectEditor({ subjectId }: { subjectId: number }) {
  const [subject, setSubject] = useState<Subject | null>(null)
  const [tree, setTree] = useState<KnowledgeTree | null>(null)
  const [pointName, setPointName] = useState('')
  const [parentId, setParentId] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)

  const pointOptions = useMemo(
    () => (tree ? flattenTree(tree.nodes) : []),
    [tree],
  )

  const load = async () => {
    setError(null)
    try {
      const [nextSubject, nextTree] = await Promise.all([
        getSubject(subjectId),
        getSubjectKnowledgeTree(subjectId),
      ])
      setSubject(nextSubject)
      setTree(nextTree)
    } catch (reason) {
      setError(messageOf(reason))
    }
  }

  useEffect(() => {
    void load()
  }, [subjectId])

  const saveSubject = async (event: FormEvent) => {
    event.preventDefault()
    if (!subject) return
    setBusy(true)
    setError(null)
    try {
      setSubject(await updateSubject(subject.id, {
        name: subject.name,
        description: subject.description,
        status: subject.status,
        sort_order: subject.sort_order,
      }))
    } catch (reason) {
      setError(messageOf(reason))
    } finally {
      setBusy(false)
    }
  }

  const addPoint = async (event: FormEvent) => {
    event.preventDefault()
    if (!subject || !pointName.trim()) return
    setBusy(true)
    setError(null)
    try {
      await createKnowledgePoint({
        subject_id: subject.id,
        parent_id: parentId ? Number(parentId) : null,
        name: pointName,
      })
      setPointName('')
      setParentId('')
      await load()
    } catch (reason) {
      setError(messageOf(reason))
    } finally {
      setBusy(false)
    }
  }

  if (!subject) {
    return <ManageEmptyState variant={error ? 'error' : 'loading'} message={error || '正在加载科目…'} />
  }

  return (
    <div className='space-y-7'>
      <Link href='/manage/subjects' className='inline-flex items-center gap-2 text-sm text-[var(--admin-text-secondary)]'>
        <ArrowLeft className='h-4 w-4' aria-hidden='true' />
        返回科目列表
      </Link>

      <div className='grid gap-7 lg:grid-cols-[minmax(0,1fr)_22rem]'>
        <div className='space-y-7'>
          <ManageFormPanel title='科目设置' error={error ?? undefined} onSubmit={saveSubject}>
            <label className='block text-sm text-[var(--admin-text-secondary)]'>
              名称
              <input
                value={subject.name}
                onChange={(event) => setSubject({ ...subject, name: event.target.value })}
                maxLength={100}
                className='mt-2 w-full rounded-lg border border-[var(--admin-border)] bg-[var(--admin-surface)] px-3 py-2.5 outline-none focus:border-[var(--brand)]'
              />
            </label>
            <label className='block text-sm text-[var(--admin-text-secondary)]'>
              说明
              <textarea
                value={subject.description ?? ''}
                onChange={(event) => setSubject({ ...subject, description: event.target.value || null })}
                rows={3}
                className='mt-2 w-full rounded-lg border border-[var(--admin-border)] bg-[var(--admin-surface)] px-3 py-2.5 outline-none focus:border-[var(--brand)]'
              />
            </label>
            <div className='grid gap-4 sm:grid-cols-2'>
              <label className='text-sm text-[var(--admin-text-secondary)]'>
                状态
                <select
                  value={subject.status}
                  onChange={(event) => setSubject({ ...subject, status: event.target.value as Subject['status'] })}
                  className='mt-2 w-full rounded-lg border border-[var(--admin-border)] bg-[var(--admin-surface)] px-3 py-2.5'
                >
                  <option value='active'>启用</option>
                  <option value='archived'>归档</option>
                </select>
              </label>
              <label className='text-sm text-[var(--admin-text-secondary)]'>
                排序
                <input
                  type='number'
                  value={subject.sort_order}
                  onChange={(event) => setSubject({ ...subject, sort_order: Number(event.target.value) })}
                  className='mt-2 w-full rounded-lg border border-[var(--admin-border)] bg-[var(--admin-surface)] px-3 py-2.5'
                />
              </label>
            </div>
            <button
              disabled={busy || !subject.name.trim()}
              className='rounded-lg bg-[var(--brand)] px-5 py-2.5 text-sm font-medium text-white disabled:opacity-45'
            >
              {busy ? '保存中…' : '保存科目'}
            </button>
          </ManageFormPanel>

          <ManagePanel title='知识点树' description='当前为嵌套树模型，章节作为知识点节点表达。'>
            {tree ? <TreeRows nodes={tree.nodes} /> : <ManageEmptyState variant='loading' message='正在加载知识点树…' />}
          </ManagePanel>
        </div>

        <ManageFormPanel title='新建知识点' onSubmit={addPoint} className='h-fit'>
          <label className='block text-sm text-[var(--admin-text-secondary)]'>
            名称
            <input
              value={pointName}
              onChange={(event) => setPointName(event.target.value)}
              maxLength={200}
              className='mt-2 w-full rounded-lg border border-[var(--admin-border)] bg-[var(--admin-surface)] px-3 py-2.5 outline-none focus:border-[var(--brand)]'
            />
          </label>
          <label className='block text-sm text-[var(--admin-text-secondary)]'>
            父级知识点
            <select
              value={parentId}
              onChange={(event) => setParentId(event.target.value)}
              className='mt-2 w-full rounded-lg border border-[var(--admin-border)] bg-[var(--admin-surface)] px-3 py-2.5'
            >
              <option value=''>作为根节点</option>
              {pointOptions.map((point) => (
                <option key={point.id} value={point.id}>
                  {'  '.repeat(point.depth)}{point.name}
                </option>
              ))}
            </select>
          </label>
          <button
            type='submit'
            disabled={busy || !pointName.trim()}
            className='inline-flex w-full items-center justify-center gap-2 rounded-lg bg-[var(--brand)] px-4 py-2.5 text-sm font-medium text-white disabled:opacity-45'
          >
            <Plus className='h-4 w-4' aria-hidden='true' />
            {busy ? '创建中…' : '创建知识点'}
          </button>
          <p className='flex items-start gap-2 text-xs leading-5 text-[var(--admin-text-tertiary)]'>
            <Archive className='mt-0.5 h-3.5 w-3.5 shrink-0' aria-hidden='true' />
            归档知识点会在详情页递归归档其子树。
          </p>
        </ManageFormPanel>
      </div>
    </div>
  )
}
