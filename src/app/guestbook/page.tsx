'use client'

import { useState, useEffect, useCallback } from 'react'
import Link from 'next/link'
import { motion } from 'motion/react'
import { cn } from '@/lib/utils'
import {
	createGuestMessage,
	listGuestMessages,
	type GuestMessage,
} from '@/lib/api/guest-messages'
import { EmptyState } from '@/components/empty-state'
import dayjs from 'dayjs'
import { MessageSquare, Send, ExternalLink } from 'lucide-react'
import { toast } from 'sonner'

const attachmentLabels: Record<string, string> = {
	home: '首页',
	blog: '博客',
	note: '笔记',
	mistake: '错题',
}

function getAttachmentHref(type: string | null, slug: string | null): string | null {
	if (!type) return null
	if (type === 'home') return '/'
	if (type === 'blog') return slug ? `/blog/${slug}` : '/blog'
	if (type === 'note') return slug ? `/notes/${slug}` : '/notes'
	if (type === 'mistake') return slug ? `/notes/${slug}` : '/mistakes'
	return null
}

export default function GuestbookPage() {
	const [messages, setMessages] = useState<GuestMessage[]>([])
	const [total, setTotal] = useState(0)
	const [page, setPage] = useState(1)
	const [loading, setLoading] = useState(true)
	const [submitting, setSubmitting] = useState(false)
	const [content, setContent] = useState('')
	const [nickname, setNickname] = useState('')
	const [attachmentType, setAttachmentType] = useState<string>('')
	const [attachmentSlug, setAttachmentSlug] = useState('')
	const [showAttachment, setShowAttachment] = useState(false)

	const loadMessages = useCallback(async (p: number) => {
		setLoading(true)
		try {
			const res = await listGuestMessages({ page: p, size: 20 })
			setMessages(res.items)
			setTotal(res.total)
		} catch {
			// silent
		} finally {
			setLoading(false)
		}
	}, [])

	useEffect(() => {
		loadMessages(1)
	}, [loadMessages])

	const handleSubmit = async (e: React.FormEvent) => {
		e.preventDefault()
		if (!content.trim()) return

		setSubmitting(true)
		try {
			const msg = await createGuestMessage({
				content: content.trim(),
				nickname: nickname.trim() || undefined,
				attachment_type: attachmentType as any || undefined,
				attachment_slug: attachmentSlug.trim() || undefined,
			})
			setMessages(prev => [msg, ...prev])
			setTotal(t => t + 1)
			setContent('')
			setNickname('')
			setAttachmentType('')
			setAttachmentSlug('')
			setShowAttachment(false)
			toast.success('留言已提交')
		} catch (err: any) {
			toast.error(err?.message || '提交失败，请稍后再试')
		} finally {
			setSubmitting(false)
		}
	}

	const handlePageChange = (newPage: number) => {
		setPage(newPage)
		loadMessages(newPage)
	}

	return (
		<div className='mx-auto max-w-3xl px-4 py-8'>
			<motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}>
				<h1 className='mb-2 text-2xl font-bold text-gray-800'>留言板</h1>
				<p className='mb-6 text-sm text-gray-500'>欢迎留下你的想法、建议或反馈</p>
			</motion.div>

			<motion.form
				onSubmit={handleSubmit}
				initial={{ opacity: 0, y: 10 }}
				animate={{ opacity: 1, y: 0 }}
				transition={{ delay: 0.1 }}
				className='mb-8 rounded-xl border border-white/40 bg-white/60 p-5 backdrop-blur-sm'>
				<div className='mb-3 flex gap-3'>
					<input
						value={nickname}
						onChange={e => setNickname(e.target.value)}
						placeholder='昵称（选填）'
						maxLength={100}
						className='w-32 rounded-lg border border-white/40 bg-white/60 px-3 py-2 text-sm outline-none focus:border-[var(--color-brand)] sm:w-48'
					/>
					<button
						type='button'
						onClick={() => setShowAttachment(!showAttachment)}
						className={cn(
							'rounded-lg border px-3 py-2 text-xs transition-colors',
							showAttachment ? 'border-[var(--color-brand)]/30 bg-[var(--color-brand)]/5 text-[var(--color-brand)]' : 'border-white/40 bg-white/40 text-gray-400 hover:text-gray-600'
						)}>
						关联内容
					</button>
				</div>

				{showAttachment && (
					<div className='mb-3 flex flex-wrap gap-2'>
						<select
							value={attachmentType}
							onChange={e => { setAttachmentType(e.target.value); setAttachmentSlug('') }}
							className='rounded-lg border border-white/40 bg-white/60 px-3 py-2 text-sm outline-none focus:border-[var(--color-brand)]'>
							<option value=''>不关联</option>
							<option value='home'>首页</option>
							<option value='blog'>博客</option>
							<option value='note'>笔记</option>
							<option value='mistake'>错题</option>
						</select>
						{attachmentType && attachmentType !== 'home' && (
							<input
								value={attachmentSlug}
								onChange={e => setAttachmentSlug(e.target.value)}
								placeholder='输入具体内容 slug 可直达，留空则链接到列表页'
								className='min-w-0 flex-1 rounded-lg border border-white/40 bg-white/60 px-3 py-2 text-sm outline-none focus:border-[var(--color-brand)]'
							/>
						)}
					</div>
				)}

				<textarea
					value={content}
					onChange={e => setContent(e.target.value)}
					placeholder='写下你想说的话...'
					required
					maxLength={2000}
					rows={3}
					className='mb-3 w-full resize-none rounded-lg border border-white/40 bg-white/60 px-4 py-3 text-sm outline-none focus:border-[var(--color-brand)]'
				/>
				<div className='flex items-center justify-between'>
					<span className='text-xs text-gray-400'>{content.length}/2000</span>
					<button
						type='submit'
						disabled={submitting || !content.trim()}
						className='flex items-center gap-1.5 rounded-lg bg-[var(--color-brand)] px-4 py-2 text-sm text-white transition-transform hover:scale-[1.02] active:scale-[0.98] disabled:opacity-50'>
						<Send className='h-3.5 w-3.5' />
						{submitting ? '提交中...' : '发表留言'}
					</button>
				</div>
			</motion.form>

			{loading ? (
				<div className='py-12 text-center text-gray-400'>加载中...</div>
			) : messages.length === 0 ? (
				<div className='py-12'>
					<EmptyState variant='no-content' title='还没有留言' description='成为第一个留言的人吧' />
				</div>
			) : (
				<div className='space-y-3'>
					{messages.map((msg, idx) => (
						<motion.div
							key={msg.id}
							initial={{ opacity: 0, y: 10 }}
							animate={{ opacity: 1, y: 0 }}
							transition={{ delay: idx * 0.03 }}
							className='rounded-xl border border-white/40 bg-white/60 p-4 backdrop-blur-sm'>
							<div className='mb-2 flex items-center gap-2'>
								<span className='font-medium text-gray-700'>{msg.nickname || '匿名访客'}</span>
								{msg.attachment_type && (
									<span className='rounded-full bg-gray-100 px-2 py-0.5 text-[10px] text-gray-500'>
										{attachmentLabels[msg.attachment_type] || msg.attachment_type}
									</span>
								)}
								<span className='ml-auto text-xs text-gray-400'>
									{dayjs(msg.created_at).format('MM-DD HH:mm')}
								</span>
							</div>
							<p className='whitespace-pre-wrap text-sm text-gray-600'>{msg.content}</p>
							{(() => {
								const href = getAttachmentHref(msg.attachment_type, msg.attachment_slug)
								if (!href) return null
								return (
									<div className='mt-2'>
										<Link
											href={href}
											className='inline-flex items-center gap-1 text-xs text-[var(--color-brand)] hover:underline'>
											<ExternalLink className='h-3 w-3' />
											查看关联内容
										</Link>
									</div>
								)
							})()}
						</motion.div>
					))}
				</div>
			)}

			{total > 20 && (
				<div className='mt-6 flex justify-center gap-2'>
					<button
						disabled={page <= 1}
						onClick={() => handlePageChange(page - 1)}
						className='rounded-lg bg-white/60 px-3 py-1 text-sm disabled:opacity-40'>
						上一页
					</button>
					<span className='px-3 py-1 text-sm text-gray-500'>
						{page} / {Math.ceil(total / 20)}
					</span>
					<button
						disabled={page >= Math.ceil(total / 20)}
						onClick={() => handlePageChange(page + 1)}
						className='rounded-lg bg-white/60 px-3 py-1 text-sm disabled:opacity-40'>
						下一页
					</button>
				</div>
			)}

			<div className='mt-10 flex flex-wrap justify-center gap-3 border-t border-white/20 pt-6'>
				<Link href='/' className='text-sm text-gray-500 hover:text-[var(--color-brand)]'>回到首页</Link>
				<span className='text-gray-300'>·</span>
				<Link href='/discover' className='text-sm text-gray-500 hover:text-[var(--color-brand)]'>发现</Link>
				<span className='text-gray-300'>·</span>
				<Link href='/blog' className='text-sm text-gray-500 hover:text-[var(--color-brand)]'>博客</Link>
				<span className='text-gray-300'>·</span>
				<Link href='/notes' className='text-sm text-gray-500 hover:text-[var(--color-brand)]'>笔记</Link>
			</div>
		</div>
	)
}
