'use client'

import { useParams } from 'next/navigation'
import useSWR from 'swr'
import Link from 'next/link'
import { motion } from 'motion/react'
import { getNote, deleteNote, type NoteDetail } from '@/lib/api/notes'
import { useMarkdownRender } from '@/hooks/use-markdown-render'
import { toast } from 'sonner'
import { cn } from '@/lib/utils'
import dayjs from 'dayjs'
import { useState } from 'react'
import { useRouter } from 'next/navigation'

const typeLabels = { note: '笔记', blog: '博客', mistake: '错题' }
const typeColors = { note: 'bg-blue-500/20 text-blue-600', blog: 'bg-green-500/20 text-green-600', mistake: 'bg-red-500/20 text-red-600' }
const diffColors = { easy: 'text-emerald-600', medium: 'text-yellow-600', hard: 'text-red-600' }

export default function NoteDetailPage() {
	const { id } = useParams<{ id: string }>()
	const router = useRouter()
	const [deleting, setDeleting] = useState(false)

	const { data: note, isLoading } = useSWR<NoteDetail>(
		`/api/notes/${id}`,
		() => getNote(id),
		{ revalidateOnFocus: false }
	)

	const { content, loading: rendering } = useMarkdownRender(note?.content || '')

	const handleDelete = async () => {
		if (!confirm('确定删除？')) return
		setDeleting(true)
		try {
			await deleteNote(id)
			router.push(note?.type === 'mistake' ? '/mistakes' : '/notes')
		} catch (e: any) {
			toast.error('删除失败: ' + (e?.message || '未知错误'))
			setDeleting(false)
		}
	}

	if (isLoading) return <div className='py-20 text-center text-gray-400'>加载中...</div>
	if (!note) return <div className='py-20 text-center text-gray-400'>未找到</div>

	return (
		<div className='mx-auto max-w-4xl px-4 py-8'>
			<motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
				<Link href={note.type === 'mistake' ? '/mistakes' : '/notes'} className='mb-4 inline-block text-sm text-gray-500 hover:text-gray-700'>
					← 返回列表
				</Link>

				<div className='mb-6 flex flex-wrap items-center gap-2'>
					<span className={cn('rounded-full px-2 py-0.5 text-xs', typeColors[note.type])}>
						{typeLabels[note.type]}
					</span>
					{note.difficulty && (
						<span className={cn('text-xs font-medium', diffColors[note.difficulty])}>
							{note.difficulty}
						</span>
					)}
					{note.subject && (
						<span className='max-w-[160px] truncate rounded-full bg-purple-500/20 px-2 py-0.5 text-xs text-purple-600'>
							{note.subject}
						</span>
					)}
					<span className='ml-auto text-xs text-gray-400'>
						{dayjs(note.created_at).format('YYYY-MM-DD HH:mm')}
					</span>
				</div>

				{note.type === 'mistake' && (
					<div className='mb-6 rounded-xl border border-orange-200/50 bg-orange-50/50 p-4'>
						<div className='mb-3 grid grid-cols-2 gap-3 text-sm sm:grid-cols-4'>
							<div><span className='text-gray-500'>复习次数:</span> {note.repetitions}</div>
							<div><span className='text-gray-500'>间隔:</span> {note.interval}天</div>
							<div><span className='text-gray-500'>EF:</span> {(note.ef || 2.5).toFixed(2)}</div>
							<div>
								<span className='text-gray-500'>下次复习:</span>{' '}
								{note.next_review ? dayjs(note.next_review).format('YYYY-MM-DD') : '-'}
							</div>
						</div>
						{note.question && (
							<div className='mb-2'>
								<div className='mb-1 text-xs font-medium text-gray-500'>题目</div>
								<div className='break-words whitespace-pre-wrap text-sm'>{note.question}</div>
							</div>
						)}
						{note.my_answer && (
							<div className='mb-2'>
								<div className='mb-1 text-xs font-medium text-red-500'>我的答案</div>
								<div className='break-words whitespace-pre-wrap text-sm'>{note.my_answer}</div>
							</div>
						)}
						{note.correct_answer && (
							<div className='mb-2'>
								<div className='mb-1 text-xs font-medium text-green-500'>正确答案</div>
								<div className='break-words whitespace-pre-wrap text-sm'>{note.correct_answer}</div>
							</div>
						)}
						{note.analysis && (
							<div className='mb-2'>
								<div className='mb-1 text-xs font-medium text-blue-500'>分析</div>
								<div className='break-words whitespace-pre-wrap text-sm'>{note.analysis}</div>
							</div>
						)}
						{note.knowledge_points && (
							<div className='mb-2'>
								<div className='mb-1 text-xs font-medium text-purple-500'>知识点</div>
								<div className='break-words whitespace-pre-wrap text-sm'>{note.knowledge_points}</div>
							</div>
						)}
						{note.images && note.images.length > 0 && (
							<div className='mt-4 border-t border-orange-200/30 pt-3'>
								<div className='mb-2 text-xs font-medium text-gray-500'>图片证据</div>
								<div className='flex flex-wrap gap-3'>
									{note.images.map((url, idx) => (
										<a
											key={url}
											href={url}
											target='_blank'
											rel='noopener noreferrer'
											className='relative h-24 w-24 rounded-lg overflow-hidden border border-orange-200 bg-white shadow-sm hover:scale-105 transition-transform'
										>
											<img src={url} alt={`evidence-${idx}`} className='h-full w-full object-cover' />
										</a>
									))}
								</div>
							</div>
						)}
					</div>
				)}

				<div className='mb-6 rounded-xl border border-white/40 bg-white/60 p-6 backdrop-blur-sm'>
					{rendering ? (
						<div className='py-10 text-center text-gray-400'>渲染中...</div>
					) : (
						<div className='prose prose-sm max-w-none'>{content}</div>
					)}
				</div>

				{note.tags.length > 0 && (
					<div className='mb-6 flex flex-wrap gap-2'>
						{note.tags.map(tag => (
							<span key={tag.id} className='rounded-full bg-gray-200/60 px-3 py-1 text-xs text-gray-600'>
								{tag.name}
							</span>
						))}
					</div>
				)}

				<div className='flex gap-3'>
					<Link
						href={note.type === 'blog' ? `/write/${note.slug}` : `/write-note/${note.slug}`}
						className='rounded-xl bg-[var(--color-brand)] px-4 py-2 text-sm text-white hover:scale-105 active:scale-95'
					>
						编辑
					</Link>
					<button
						onClick={handleDelete}
						disabled={deleting}
						className='rounded-xl bg-red-500/20 px-4 py-2 text-sm text-red-600 hover:bg-red-500/30 disabled:opacity-50'
					>
						{deleting ? '删除中...' : '删除'}
					</button>
				</div>
			</motion.div>
		</div>
	)
}
