'use client'

import Link from 'next/link'
import { useSearchParams } from 'next/navigation'
import { useNoteIndex } from '@/hooks/use-note-index'
import { deleteNote } from '@/lib/api/notes'
import { getContentDetailHref } from '@/lib/content-routes'
import { FeatureState } from '../../components/feature-state'
import { ManagePageHeader } from '../../components/manage-page-header'
import { useState } from 'react'

export default function NotesPage() {
	const params = useSearchParams()
	const requestedType = params.get('type')
	const type: 'note' | 'blog' | undefined = requestedType === 'blog' || requestedType === 'note' ? requestedType : undefined
	const [page, setPage] = useState(1)
	const { data, error, isLoading, mutate } = useNoteIndex({
		type,
		types: type ? undefined : 'note,blog',
		page,
		size: 30,
	})
	const [deleteError, setDeleteError] = useState('')
	const items = data?.items ?? []
	const total = data?.total ?? 0
	const totalPages = Math.max(1, Math.ceil(total / 30))
	const remove = async (slug: string) => {
		if (!window.confirm('确认删除这条内容？')) return
		setDeleteError('')
		try {
			await deleteNote(slug)
			await mutate()
		} catch (reason) {
			setDeleteError(reason instanceof Error ? reason.message : '删除失败')
		}
	}
	const state = isLoading ? (
		<FeatureState state={{ kind: 'loading', label: '正在加载内容', rows: 4 }} />
	) : error ? (
		<FeatureState
			state={{
				kind: 'error',
				title: '内容加载失败',
				description: '请检查连接后重试。',
				retry: () => {
					void mutate()
				}
			}}
		/>
	) : items.length ? (
		<div className='overflow-x-auto border border-slate-200/70 bg-white/45'>
			<table className='w-full min-w-[620px] text-left text-sm'>
				<thead className='border-b border-slate-200/70 text-xs text-slate-500'>
					<tr>
						<th className='p-3'>标题</th>
						<th className='p-3'>类型</th>
						<th className='p-3'>状态</th>
						<th className='p-3'>更新时间</th>
						<th className='p-3'>操作</th>
					</tr>
				</thead>
				<tbody>
					{items.map(item => (
						<tr key={item.slug} className='border-b border-slate-200/60 last:border-0'>
							<td className='p-3 font-medium'>{item.title || '无标题'}</td>
							<td className='p-3'>{item.type === 'blog' ? '博客' : '笔记'}</td>
							<td className='p-3'>{item.status === 'published' ? '已发布' : '草稿'}</td>
							<td className='p-3 text-slate-500'>{new Date(item.updated_at).toLocaleString('zh-CN')}</td>
							<td className='flex gap-3 p-3'>
								<Link className='text-[var(--color-brand)]' href={`/manage/notes/${item.slug}`}>
									编辑
								</Link>
								<Link className='text-slate-500' href={getContentDetailHref(item.type, item.slug)}>
									查看
								</Link>
								<button type='button' className='text-red-700' onClick={() => void remove(item.slug)}>
									删除
								</button>
							</td>
						</tr>
					))}
				</tbody>
			</table>
		</div>
	) : (
		<FeatureState
			state={{
				kind: 'empty',
				title: '还没有内容',
				description: '新建一条笔记或博客开始整理。',
				action: {
					label: '新建笔记',
					onClick: () => {
						window.location.href = '/manage/notes/new?type=note'
					}
				}
			}}
		/>
	)
	return (
		<div className='space-y-8'>
			<ManagePageHeader eyebrow='内容管理' title='笔记写作' description='统一管理笔记与博客的草稿、发布状态和属性。' />
			<div className='flex flex-wrap gap-2'>
				<Link href='/manage/notes/new?type=note' className='brand-btn'>
					新建笔记
				</Link>
				<Link href='/manage/notes/new?type=blog' className='rounded-lg border border-slate-200 px-4 py-2 text-sm'>
					新建博客
				</Link>
			</div>
			{deleteError ? (
				<p role='alert' className='text-sm text-red-700'>
					{deleteError}
				</p>
			) : null}
			{state}
			{totalPages > 1 ? (
				<div className='mt-6 flex items-center justify-center gap-3 text-sm'>
					<button
						type='button'
						disabled={page <= 1}
						onClick={() => setPage(current => Math.max(1, current - 1))}
						className='rounded-lg border border-slate-200 px-3 py-1 disabled:opacity-40'
					>
						上一页
					</button>
					<span className='text-slate-500'>
						{page} / {totalPages}
					</span>
					<button
						type='button'
						disabled={page >= totalPages}
						onClick={() => setPage(current => Math.min(totalPages, current + 1))}
						className='rounded-lg border border-slate-200 px-3 py-1 disabled:opacity-40'
					>
						下一页
					</button>
				</div>
			) : null}
		</div>
	)
}
