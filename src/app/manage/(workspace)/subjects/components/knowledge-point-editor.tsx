'use client'

import Link from 'next/link'
import { FormEvent, useEffect, useMemo, useState } from 'react'
import { Archive, ArrowLeft, Trash2 } from 'lucide-react'
import { useRouter } from 'next/navigation'

import {
  archiveKnowledgePoint,
  deleteKnowledgePoint,
  getKnowledgePoint,
  getSubjectKnowledgeTree,
  updateKnowledgePoint,
  type KnowledgePoint,
  type KnowledgePointTreeNode,
} from '@/lib/api/taxonomy'

function flattenTree(nodes: KnowledgePointTreeNode[], depth = 0): Array<KnowledgePointTreeNode & { depth: number }> {
  return nodes.flatMap((node) => [
    { ...node, depth },
    ...flattenTree(node.children, depth + 1),
  ])
}

function collectDescendantIds(nodeId: number, nodes: KnowledgePointTreeNode[]): Set<number> {
  const all = flattenTree(nodes)
  const byParent = new Map<number | null, KnowledgePointTreeNode[]>()
  all.forEach((node) => {
    const siblings = byParent.get(node.parent_id) ?? []
    siblings.push(node)
    byParent.set(node.parent_id, siblings)
  })
  const ids = new Set<number>()
  const visit = (id: number) => {
    ;(byParent.get(id) ?? []).forEach((child) => {
      ids.add(child.id)
      visit(child.id)
    })
  }
  visit(nodeId)
  return ids
}

export function KnowledgePointEditor({ knowledgePointId }: { knowledgePointId: number }) {
  const router = useRouter()
  const [point, setPoint] = useState<KnowledgePoint | null>(null)
  const [treeNodes, setTreeNodes] = useState<KnowledgePointTreeNode[]>([])
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)

  const parentOptions = useMemo(() => {
    if (!point) return []
    const descendants = collectDescendantIds(point.id, treeNodes)
    return flattenTree(treeNodes).filter((item) => item.id !== point.id && !descendants.has(item.id))
  }, [point, treeNodes])

  const load = async () => {
    setError(null)
    try {
      const item = await getKnowledgePoint(knowledgePointId)
      const tree = await getSubjectKnowledgeTree(item.subject_id)
      setPoint(item)
      setTreeNodes(tree.nodes)
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : '加载失败')
    }
  }

  useEffect(() => {
    void load()
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
        parent_id: point.parent_id,
        status: point.status,
        sort_order: point.sort_order,
      }))
      await load()
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
        <ArrowLeft className='h-4 w-4' aria-hidden='true' />
        返回所属科目
      </Link>

      <form onSubmit={submit} className='space-y-5 rounded-lg border border-slate-200/70 bg-white/60 p-5'>
        <h1 className='text-2xl font-semibold text-slate-900'>编辑知识点</h1>
        <label className='block text-sm text-slate-600'>
          名称
          <input
            value={point.name}
            onChange={(event) => setPoint({ ...point, name: event.target.value })}
            className='mt-2 w-full rounded-lg border border-slate-200 px-3 py-2.5'
          />
        </label>
        <label className='block text-sm text-slate-600'>
          父级知识点
          <select
            value={point.parent_id ?? ''}
            onChange={(event) => setPoint({ ...point, parent_id: event.target.value ? Number(event.target.value) : null })}
            className='mt-2 w-full rounded-lg border border-slate-200 px-3 py-2.5'
          >
            <option value=''>作为根节点</option>
            {parentOptions.map((option) => (
              <option key={option.id} value={option.id}>
                {'  '.repeat(option.depth)}{option.name}
              </option>
            ))}
          </select>
        </label>
        <label className='block text-sm text-slate-600'>
          说明
          <textarea
            value={point.description ?? ''}
            onChange={(event) => setPoint({ ...point, description: event.target.value || null })}
            rows={4}
            className='mt-2 w-full rounded-lg border border-slate-200 px-3 py-2.5'
          />
        </label>
        <div className='grid gap-4 sm:grid-cols-2'>
          <label className='text-sm text-slate-600'>
            状态
            <select
              value={point.status}
              onChange={(event) => setPoint({ ...point, status: event.target.value as KnowledgePoint['status'] })}
              className='mt-2 w-full rounded-lg border border-slate-200 px-3 py-2.5'
            >
              <option value='active'>启用</option>
              <option value='archived'>归档</option>
            </select>
          </label>
          <label className='text-sm text-slate-600'>
            排序
            <input
              type='number'
              value={point.sort_order}
              onChange={(event) => setPoint({ ...point, sort_order: Number(event.target.value) })}
              className='mt-2 w-full rounded-lg border border-slate-200 px-3 py-2.5'
            />
          </label>
        </div>
        {error ? <p role='alert' className='text-sm text-red-600'>{error}</p> : null}
        <div className='flex flex-wrap justify-between gap-3'>
          <button
            type='button'
            onClick={async () => {
              if (!window.confirm('确认删除这个知识点？有关联或子节点时系统会拒绝删除。')) return
              setBusy(true)
              try {
                await deleteKnowledgePoint(point.id)
                router.push(`/manage/subjects/${point.subject_id}`)
              } catch (reason) {
                setError(reason instanceof Error ? reason.message : '删除失败')
                setBusy(false)
              }
            }}
            className='inline-flex items-center gap-2 rounded-lg border border-red-200 px-3 py-2 text-sm text-red-600'
          >
            <Trash2 className='h-4 w-4' aria-hidden='true' />
            删除
          </button>
          <div className='flex flex-wrap gap-2'>
            <button
              type='button'
              onClick={async () => {
                if (!window.confirm('确认归档这个知识点及全部子节点？')) return
                setBusy(true)
                try {
                  setPoint(await archiveKnowledgePoint(point.id))
                  await load()
                } catch (reason) {
                  setError(reason instanceof Error ? reason.message : '归档失败')
                } finally {
                  setBusy(false)
                }
              }}
              className='inline-flex items-center gap-2 rounded-lg border border-amber-200 px-3 py-2 text-sm text-amber-700'
            >
              <Archive className='h-4 w-4' aria-hidden='true' />
              归档子树
            </button>
            <button disabled={busy || !point.name.trim()} className='rounded-lg bg-[var(--color-brand)] px-5 py-2 text-sm text-white disabled:opacity-45'>
              {busy ? '处理中…' : '保存'}
            </button>
          </div>
        </div>
      </form>
    </div>
  )
}
