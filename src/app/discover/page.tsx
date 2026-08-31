'use client'

import { useState, useEffect, useMemo } from 'react'
import Link from 'next/link'
import { useSearchParams } from 'next/navigation'
import { motion } from 'motion/react'
import { cn } from '@/lib/utils'
import { getShares, getBloggers, type ShareItem, type BloggerItem } from '@/lib/api/content'
import { listNotes, type NoteListItem } from '@/lib/api/notes'
import StarRating from '@/components/star-rating'
import { EmptyState } from '@/components/empty-state'
import dayjs from 'dayjs'
import { Compass, BookOpen, FileText, ExternalLink } from 'lucide-react'
import { Suspense } from 'react'

type DiscoverTab = 'shares' | 'bloggers' | 'notes'

const tabs: { id: DiscoverTab; label: string; icon: React.ElementType }[] = [
	{ id: 'shares', label: '推荐分享', icon: Compass },
	{ id: 'bloggers', label: '优秀博客', icon: BookOpen },
	{ id: 'notes', label: '优秀笔记', icon: FileText },
]

export default function DiscoverPage() {
	return (
		<Suspense fallback={<div className='py-20 text-center text-gray-400'>加载中...</div>}>
			<DiscoverContent />
		</Suspense>
	)
}

function DiscoverContent() {
	const searchParams = useSearchParams()
	const tabParam = searchParams.get('tab')
	const validTabs: DiscoverTab[] = ['shares', 'bloggers', 'notes']
	const initialTab = validTabs.includes(tabParam as DiscoverTab) ? (tabParam as DiscoverTab) : 'shares'
	const [activeTab, setActiveTab] = useState<DiscoverTab>(initialTab)
	const [shares, setShares] = useState<ShareItem[]>([])
	const [bloggers, setBloggers] = useState<BloggerItem[]>([])
	const [notes, setNotes] = useState<NoteListItem[]>([])
	const [loading, setLoading] = useState(true)
	const [search, setSearch] = useState('')

	useEffect(() => {
		setLoading(true)
		Promise.all([
			getShares().catch(() => []),
			getBloggers().catch(() => []),
			listNotes({ type: 'note', featured: true, sort_by: 'sort_order', size: 50 }).then(r => r.items).catch(() => []),
		]).then(([s, b, n]) => {
			setShares(s)
			setBloggers(b)
			setNotes(n)
		}).finally(() => setLoading(false))
	}, [])

	const filteredShares = useMemo(() => {
		const sorted = [...shares].sort((a, b) => (b.stars || 0) - (a.stars || 0))
		if (!search) return sorted
		const q = search.toLowerCase()
		return sorted.filter(s => s.name.toLowerCase().includes(q) || s.description.toLowerCase().includes(q))
	}, [shares, search])

	const filteredBloggers = useMemo(() => {
		const sorted = [...bloggers].sort((a, b) => (b.stars || 0) - (a.stars || 0))
		if (!search) return sorted
		const q = search.toLowerCase()
		return sorted.filter(b => b.name.toLowerCase().includes(q) || b.description.toLowerCase().includes(q))
	}, [bloggers, search])

	const filteredNotes = useMemo(() => {
		if (!search) return notes
		const q = search.toLowerCase()
		return notes.filter(n => n.title.toLowerCase().includes(q) || (n.summary || '').toLowerCase().includes(q))
	}, [notes, search])

	return (
		<div className='mx-auto max-w-5xl px-4 py-8'>
			<motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}>
				<h1 className='mb-2 text-2xl font-bold text-gray-800'>发现</h1>
				<p className='mb-6 text-sm text-gray-500'>探索推荐资源、优秀博主和精选笔记</p>
			</motion.div>

			<div className='mb-6 flex flex-wrap items-center gap-3'>
				<div className='flex gap-1 rounded-xl border border-white/40 bg-white/60 p-1 backdrop-blur-sm'>
					{tabs.map(tab => {
						const Icon = tab.icon
						return (
							<button
								key={tab.id}
								onClick={() => { setActiveTab(tab.id); setSearch('') }}
								className={cn(
									'flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-sm transition-colors',
									activeTab === tab.id ? 'bg-[var(--color-brand)] text-white' : 'text-gray-500 hover:text-gray-700'
								)}>
								<Icon className='h-4 w-4' />
								{tab.label}
							</button>
						)
					})}
				</div>
				<input
					value={search}
					onChange={e => setSearch(e.target.value)}
					placeholder='搜索...'
					className='ml-auto rounded-xl border border-white/40 bg-white/60 px-4 py-2 text-sm backdrop-blur-sm outline-none focus:border-[var(--color-brand)]'
				/>
			</div>

			{loading ? (
				<div className='py-20 text-center text-gray-400'>加载中...</div>
			) : (
				<>
					{activeTab === 'shares' && (
						<div className='grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3'>
							{filteredShares.map(share => (
								<motion.a
									key={share.url}
									href={share.url}
									target='_blank'
									rel='noopener noreferrer'
									initial={{ opacity: 0, scale: 0.95 }}
									animate={{ opacity: 1, scale: 1 }}
									className='group block rounded-xl border border-white/40 bg-white/60 p-4 backdrop-blur-sm transition-all hover:border-[var(--color-brand)]/30 hover:shadow-md'>
									<div className='mb-3 flex items-center gap-3'>
										<img src={share.logo} alt={share.name} className='h-10 w-10 rounded-lg object-cover' />
										<div className='min-w-0 flex-1'>
											<h3 className='truncate font-medium text-gray-800 group-hover:text-[var(--color-brand)]'>{share.name}</h3>
											<StarRating stars={share.stars} />
										</div>
										<ExternalLink className='h-4 w-4 shrink-0 text-gray-300 group-hover:text-[var(--color-brand)]' />
									</div>
									<p className='line-clamp-2 text-xs text-gray-500'>{share.description}</p>
									{share.tags.length > 0 && (
										<div className='mt-2 flex flex-wrap gap-1'>
											{share.tags.slice(0, 3).map(tag => (
												<span key={tag} className='rounded-full bg-gray-100 px-2 py-0.5 text-[10px] text-gray-500'>{tag}</span>
											))}
										</div>
									)}
								</motion.a>
							))}
							{filteredShares.length === 0 && (
								<div className='col-span-full py-12'>
									<EmptyState variant='no-results' title='暂无推荐分享' description='稍后再来看看' />
								</div>
							)}
						</div>
					)}

					{activeTab === 'bloggers' && (
						<div className='grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3'>
							{filteredBloggers.map(blogger => (
								<motion.a
									key={blogger.url}
									href={blogger.url}
									target='_blank'
									rel='noopener noreferrer'
									initial={{ opacity: 0, scale: 0.95 }}
									animate={{ opacity: 1, scale: 1 }}
									className='group block rounded-xl border border-white/40 bg-white/60 p-4 backdrop-blur-sm transition-all hover:border-[var(--color-brand)]/30 hover:shadow-md'>
									<div className='mb-3 flex items-center gap-3'>
										<img src={blogger.avatar} alt={blogger.name} className='h-10 w-10 rounded-full object-cover' />
										<div className='min-w-0 flex-1'>
											<h3 className='truncate font-medium text-gray-800 group-hover:text-[var(--color-brand)]'>{blogger.name}</h3>
											<StarRating stars={blogger.stars} />
										</div>
										<ExternalLink className='h-4 w-4 shrink-0 text-gray-300 group-hover:text-[var(--color-brand)]' />
									</div>
									<p className='line-clamp-2 text-xs text-gray-500'>{blogger.description}</p>
									{blogger.status && (
										<span className={cn(
											'mt-2 inline-block rounded-full px-2 py-0.5 text-[10px]',
											blogger.status === 'recent' ? 'bg-green-100 text-green-600' : 'bg-gray-100 text-gray-500'
										)}>
											{blogger.status === 'recent' ? '近期更新' : '长期失联'}
										</span>
									)}
								</motion.a>
							))}
							{filteredBloggers.length === 0 && (
								<div className='col-span-full py-12'>
									<EmptyState variant='no-results' title='暂无优秀博客' description='稍后再来看看' />
								</div>
							)}
						</div>
					)}

					{activeTab === 'notes' && (
						<div className='grid grid-cols-1 gap-4 md:grid-cols-2'>
							{filteredNotes.map(note => (
								<Link
									key={note.slug}
									href={`/notes/${note.slug}`}
									className='group block rounded-xl border border-white/40 bg-white/60 p-4 backdrop-blur-sm transition-all hover:border-[var(--color-brand)]/30 hover:shadow-md'>
									<h3 className='mb-1 font-medium text-gray-800 group-hover:text-[var(--color-brand)]'>{note.title}</h3>
									{note.summary && <p className='mb-2 line-clamp-2 text-xs text-gray-500'>{note.summary}</p>}
									<div className='flex items-center gap-2'>
										{note.tags.slice(0, 3).map(tag => (
											<span key={tag.id} className='rounded-full bg-gray-100 px-2 py-0.5 text-[10px] text-gray-500'>{tag.name}</span>
										))}
										<span className='ml-auto text-[10px] text-gray-400'>{dayjs(note.updated_at).format('YYYY-MM-DD')}</span>
									</div>
								</Link>
							))}
							{filteredNotes.length === 0 && (
								<div className='col-span-full py-12'>
									<EmptyState variant='no-results' title='暂无精选笔记' description='管理员可在编辑笔记时设置策展权重来标记精选' />
								</div>
							)}
						</div>
					)}
				</>
			)}

			<div className='mt-10 flex flex-wrap justify-center gap-3 border-t border-white/20 pt-6'>
				<Link href='/blog' className='text-sm text-gray-500 hover:text-[var(--color-brand)]'>浏览博客</Link>
				<span className='text-gray-300'>·</span>
				<Link href='/notes' className='text-sm text-gray-500 hover:text-[var(--color-brand)]'>浏览笔记</Link>
				<span className='text-gray-300'>·</span>
				<Link href='/mistakes' className='text-sm text-gray-500 hover:text-[var(--color-brand)]'>浏览错题</Link>
				<span className='text-gray-300'>·</span>
				<Link href='/guestbook' className='text-sm text-gray-500 hover:text-[var(--color-brand)]'>留言板</Link>
			</div>
		</div>
	)
}
