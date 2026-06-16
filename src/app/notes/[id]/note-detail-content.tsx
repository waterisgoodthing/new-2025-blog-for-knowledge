'use client'

import { useParams, useSearchParams } from 'next/navigation'
import dynamic from 'next/dynamic'
import useSWR from 'swr'
import Link from 'next/link'
import { motion } from 'motion/react'
import { getNote, deleteNote, type NoteDetail } from '@/lib/api/notes'
import { useMarkdownRender } from '@/hooks/use-markdown-render'
import { toast } from 'sonner'
import { cn } from '@/lib/utils'
import { EmptyState } from '@/components/empty-state'
import dayjs from 'dayjs'
import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { getContentEditHref, getContentListHref } from '@/lib/content-routes'
import { resolveImageUrl } from '@/lib/api/images'
import { RichText } from '@/components/rich-text'
import { RelatedKnowledgePanel } from './components/related-knowledge-panel'
import { useAdminAuth } from '@/hooks/use-admin-auth'

const MermaidBlock = dynamic(() => import('@/components/mermaid-block').then(mod => mod.MermaidBlock), { ssr: false })

function StructuredGraphDiagram({ nodes, edges }: { nodes: { id: string; label: string; highlighted?: boolean; annotation?: string }[]; edges: { source: string; target: string; label?: string; highlighted?: boolean; weight?: string }[] }) {
	const nodeMap = new Map(nodes.map((n, i) => [n.id, { ...n, index: i }]))
	const cols = Math.ceil(Math.sqrt(nodes.length))
	const cellW = 140
	const cellH = 80
	const pad = 40
	const w = cols * cellW + pad * 2
	const rows = Math.ceil(nodes.length / cols)
	const h = rows * cellH + pad * 2

	const getNodePos = (idx: number) => ({
		x: pad + (idx % cols) * cellW + cellW / 2,
		y: pad + Math.floor(idx / cols) * cellH + cellH / 2,
	})

	return (
		<svg viewBox={`0 0 ${w} ${h}`} className='w-full max-w-lg' role='img' aria-label='结构化图解'>
			{edges.map((e, i) => {
				const si = nodeMap.get(e.source)?.index ?? 0
				const ti = nodeMap.get(e.target)?.index ?? 0
				const sp = getNodePos(si)
				const tp = getNodePos(ti)
				const color = e.highlighted ? '#f59e0b' : '#94a3b8'
				return (
					<g key={i}>
						<line x1={sp.x} y1={sp.y} x2={tp.x} y2={tp.y} stroke={color} strokeWidth={e.highlighted ? 2.5 : 1.5} markerEnd='url(#arrow)' />
						{(e.label || e.weight) && (
							<text x={(sp.x + tp.x) / 2} y={(sp.y + tp.y) / 2 - 6} textAnchor='middle' className='text-[10px] fill-slate-600'>
								{e.label || e.weight}
							</text>
						)}
					</g>
				)
			})}
			<defs>
				<marker id='arrow' viewBox='0 0 10 10' refX='10' refY='5' markerWidth='6' markerHeight='6' orient='auto-start-reverse'>
					<path d='M 0 0 L 10 5 L 0 10 z' fill='#94a3b8' />
				</marker>
			</defs>
			{nodes.map((n, i) => {
				const p = getNodePos(i)
				const fill = n.highlighted ? '#fef3c7' : '#f8fafc'
				const stroke = n.highlighted ? '#f59e0b' : '#cbd5e1'
				return (
					<g key={n.id}>
						<rect x={p.x - 45} y={p.y - 18} width={90} height={36} rx={8} fill={fill} stroke={stroke} strokeWidth={n.highlighted ? 2 : 1} />
						<text x={p.x} y={p.y + 1} textAnchor='middle' dominantBaseline='middle' className={cn('text-[11px] font-medium', n.highlighted ? 'fill-amber-800' : 'fill-slate-700')}>
							{n.label.length > 10 ? n.label.slice(0, 10) + '…' : n.label}
						</text>
						{n.annotation && (
							<text x={p.x} y={p.y + 28} textAnchor='middle' className='text-[9px] fill-amber-600'>
								{n.annotation.length > 16 ? n.annotation.slice(0, 16) + '…' : n.annotation}
							</text>
						)}
					</g>
				)
			})}
		</svg>
	)
}

const typeLabels = { note: '笔记', blog: '博客', mistake: '错题' }
const typeColors = { note: 'bg-blue-500/20 text-blue-600', blog: 'bg-green-500/20 text-green-600', mistake: 'bg-red-500/20 text-red-600' }
const diffColors = { easy: 'text-emerald-600', medium: 'text-yellow-600', hard: 'text-red-600' }
const diffLabels = { easy: '简单', medium: '中等', hard: '困难' }

export default function NoteDetailContent() {
	const { id } = useParams<{ id: string }>()
	const searchParams = useSearchParams()
	const folderId = searchParams.get('folder_id')
	const router = useRouter()
	const [deleting, setDeleting] = useState(false)
	const { isAdmin } = useAdminAuth()

	const { data: note, isLoading } = useSWR<NoteDetail>(
		`/api/notes/${id}`,
		() => getNote(id),
		{ revalidateOnFocus: false }
	)

	const { content, loading: rendering } = useMarkdownRender(note?.content || '')

	const handleDelete = async () => {
		const label = note ? (typeLabels[note.type as keyof typeof typeLabels] || '内容') : '内容'
		if (!confirm(`确定删除该篇${label}？`)) return
		setDeleting(true)
		try {
			await deleteNote(id)
			router.push(note ? getContentListHref(note.type, folderId) : '/notes')
		} catch (e: any) {
			toast.error('删除失败: ' + (e?.message || '未知错误'))
			setDeleting(false)
		}
	}

	if (isLoading) return <div className='py-20 text-center text-gray-400'>加载中...</div>
	if (!note) return <div className='py-20'><EmptyState variant='load-error' title='未找到内容' description='该笔记可能已被删除或链接无效' action={{ label: '返回笔记列表', href: '/notes' }} /></div>

	const actionBar = isAdmin ? (
		<div className='flex gap-3'>
			<Link
				href={getContentEditHref(note.type, note.slug) + (folderId ? `?folder_id=${encodeURIComponent(folderId)}` : '')}
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
	) : null

	if (note.type === 'mistake') {
		const isDue = note.next_review ? dayjs(note.next_review).isSame(dayjs(), 'day') || dayjs(note.next_review).isBefore(dayjs(), 'day') : false

		return (
			<div className='mx-auto max-w-6xl px-4 py-8'>
				<motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
				<Link href={getContentListHref(note.type, folderId)} className='mb-4 inline-block text-sm text-gray-500 hover:text-gray-700'>
					← 返回错题集
				</Link>

					<div className='mb-5 flex flex-wrap items-center gap-2'>
						<span className={cn('rounded-full px-2 py-0.5 text-xs', typeColors[note.type])}>{typeLabels[note.type]}</span>
						{note.difficulty && <span className={cn('text-xs font-medium', diffColors[note.difficulty])}>{diffLabels[note.difficulty]}</span>}
						{note.subject && <span className='rounded-full bg-purple-500/20 px-2 py-0.5 text-xs text-purple-600'>{note.subject}</span>}
						<span className='ml-auto text-xs text-gray-400'>{dayjs(note.created_at).format('YYYY-MM-DD HH:mm')}</span>
					</div>

					<div className='mb-6 grid gap-4 lg:grid-cols-[1.2fr_0.8fr]'>
						<section className='rounded-xl border border-white/40 bg-white/60 p-5 backdrop-blur-sm'>
							<div className='mb-4 flex flex-wrap items-start justify-between gap-3'>
								<div>
									<h1 className='text-2xl font-bold leading-tight text-gray-900'>{note.title}</h1>
									{isAdmin && <p className='mt-1 text-sm text-gray-500'>先看题目和自己的答案，再对照正确步骤复盘。</p>}
								</div>
								{isAdmin && (
									<Link href='/mistakes/review' className='rounded-lg bg-orange-500 px-3 py-1.5 text-xs text-white transition-transform hover:scale-105 active:scale-95'>
										开始复习
									</Link>
								)}
							</div>

							{note.images && note.images.length > 0 && (
								<div className='mb-4'>
									<div className='mb-2 text-xs font-medium text-gray-500'>图片证据</div>
									<div className='grid grid-cols-2 gap-3 sm:grid-cols-3'>
										{note.images.map((url, idx) => (
											<a
												key={url}
												href={resolveImageUrl(url)}
												target='_blank'
												rel='noopener noreferrer'
												className='block overflow-hidden rounded-lg border border-orange-200 bg-white shadow-sm transition-transform hover:scale-[1.02]'>
												<img src={resolveImageUrl(url)} alt={`错题图片证据 ${idx + 1}`} className='aspect-video w-full object-cover' />
											</a>
										))}
									</div>
								</div>
							)}

							<div className='space-y-3'>
								<StudyBlock title='题目' tone='neutral' content={note.question} fallback={note.content} />
								{(() => {
									const vc = note.ai_metadata?.visual_context ? String(note.ai_metadata.visual_context) : ''
									const id = note.ai_metadata?.image_dependency ? String(note.ai_metadata.image_dependency) : ''
									return vc ? (
										<section className='rounded-xl border border-cyan-200/70 bg-cyan-50/50 p-4'>
											<h2 className='mb-2 text-sm font-semibold text-cyan-800'>视觉上下文</h2>
											<RichText content={vc} className='text-sm leading-6 text-cyan-900' />
											{id && id !== 'none' && (
												<div className='mt-2 text-xs text-cyan-700'>
													图片依赖: {id === 'full' ? '完全依赖图片' : '部分依赖图片'}
												</div>
											)}
										</section>
									) : null
								})()}
								{isAdmin && <StudyBlock title='我的错误思路' tone='danger' content={note.my_answer} />}
								<StudyBlock title='正确答案' tone='success' content={note.correct_answer} />
							</div>
						</section>

						<aside className='self-start space-y-3'>
							{note.tags.length > 0 && (
								<div className='rounded-xl border border-white/40 bg-white/60 p-4 backdrop-blur-sm'>
									<h2 className='mb-3 text-sm font-semibold text-gray-800'>标签</h2>
									<div className='flex flex-wrap gap-2'>
										{note.tags.map(tag => (
											<span key={tag.id} className='rounded-full bg-gray-200/60 px-3 py-1 text-xs text-gray-600'>{tag.name}</span>
										))}
									</div>
								</div>
							)}

							{note.knowledge_points && (
								<div className='rounded-xl border border-purple-200/70 bg-purple-50/50 p-4 backdrop-blur-sm'>
									<h2 className='mb-2 text-sm font-semibold text-purple-800'>知识点归总</h2>
									<RichText content={note.knowledge_points} className='text-sm leading-6 text-purple-900' />
								</div>
							)}

							{isAdmin && (
								<div className='rounded-xl border border-white/40 bg-white/60 p-4 backdrop-blur-sm'>
									<h2 className='mb-3 text-sm font-semibold text-gray-800'>复习状态</h2>
									<div className='grid grid-cols-2 gap-2 text-center'>
										<Metric label='复习次数' value={String(note.repetitions || 0)} />
										<Metric label='记忆系数' value={(note.ef || 2.5).toFixed(2)} />
										<Metric label='间隔' value={`${note.interval || 0} 天`} />
										<Metric label='下次复习' value={note.next_review ? dayjs(note.next_review).format('MM-DD') : '-'} highlight={isDue} />
									</div>
									{note.last_reviewed && <p className='mt-3 text-xs text-gray-500'>上次复习: {dayjs(note.last_reviewed).format('YYYY-MM-DD HH:mm')}</p>}
								</div>
							)}
						</aside>
					</div>

				{isAdmin && (
					<>
						<div className='mb-6'>
							<StudyBlock title='错因与解析' tone='info' content={note.analysis} large />
						</div>

						{note.ai_metadata && (
							<div className='mb-6 space-y-4'>
								<h2 className='text-lg font-bold text-gray-800'>AI 解析</h2>
								{String(note.ai_metadata.user_error_analysis || '') && (
									<section className='rounded-xl border border-orange-200/70 bg-orange-50/50 p-4'>
										<h2 className='mb-2 text-sm font-semibold text-orange-800'>我的思路与错因</h2>
										<RichText content={String(note.ai_metadata.user_error_analysis)} className='text-sm leading-6 text-orange-900' />
									</section>
								)}
								{String(note.ai_metadata.personalized_diagnosis || '') && (
									<section className='rounded-xl border border-rose-200/70 bg-rose-50/50 p-4'>
										<h2 className='mb-2 text-sm font-semibold text-rose-800'>个性化错因诊断</h2>
										<RichText content={String(note.ai_metadata.personalized_diagnosis)} className='text-sm leading-6 text-rose-900' />
										{String(note.ai_metadata.misread_signal || '') && (
											<div className='mt-2 rounded-lg bg-rose-100/50 px-3 py-2 text-xs text-rose-800'>
												<span className='font-medium'>忽略的信号: </span>{String(note.ai_metadata.misread_signal)}
											</div>
										)}
										{(note.ai_metadata.next_time_checklist as string[])?.length > 0 && (
											<div className='mt-2'>
												<div className='text-xs font-medium text-rose-700 mb-1'>下次做题检查清单:</div>
												<ul className='list-disc space-y-0.5 pl-4 text-xs text-rose-800'>
													{(note.ai_metadata.next_time_checklist as string[]).map((item, i) => <li key={i}>{item}</li>)}
												</ul>
											</div>
										)}
									</section>
								)}
								<div className='grid gap-4 lg:grid-cols-2'>
									<StudyBlock title='错误原因' tone='danger' content={note.ai_metadata.error_reason as string} />
									<StudyBlock title='关键步骤' tone='success' content={note.ai_metadata.key_step as string} />
								</div>
								<div className='grid gap-4 lg:grid-cols-2'>
									<StudyBlock title='举一反三' tone='info' content={note.ai_metadata.generalization as string} />
									<StudyBlock title='复习建议' tone='purple' content={note.ai_metadata.review_advice as string} />
								</div>
								{(note.ai_metadata.similar_traps as string[])?.length > 0 && (
									<section className='rounded-xl border border-amber-200/70 bg-amber-50/50 p-4'>
										<h2 className='mb-2 text-sm font-semibold text-amber-800'>易错陷阱</h2>
										<ul className='list-disc space-y-1 pl-5 text-sm text-amber-900'>
											{(note.ai_metadata.similar_traps as string[]).map((t, i) => <li key={i}>{t}</li>)}
										</ul>
									</section>
								)}
								{(note.ai_metadata.variant_questions as string[])?.length > 0 && (
									<section className='rounded-xl border border-indigo-200/70 bg-indigo-50/50 p-4'>
										<h2 className='mb-2 text-sm font-semibold text-indigo-800'>变式题</h2>
										<ol className='list-decimal space-y-1 pl-5 text-sm text-indigo-900'>
											{(note.ai_metadata.variant_questions as string[]).map((q, i) => <li key={i}>{q}</li>)}
										</ol>
									</section>
								)}
								{(note.ai_metadata.related_notes as { slug: string; title: string }[])?.length > 0 && (
									<section className='rounded-xl border border-teal-200/70 bg-teal-50/50 p-4'>
										<h2 className='mb-2 text-sm font-semibold text-teal-800'>关联笔记</h2>
										<div className='flex flex-wrap gap-2'>
											{(note.ai_metadata.related_notes as { slug: string; title: string }[]).map((rn) => (
												<Link key={rn.slug} href={`/notes/${rn.slug}`} className='rounded-lg bg-teal-100 px-3 py-1.5 text-sm text-teal-700 transition-colors hover:bg-teal-200'>
													{rn.title}
												</Link>
											))}
										</div>
									</section>
								)}
							</div>
						)}

						{(() => {
							const diagrams = note.ai_metadata?.diagrams as { type: string; title: string; mermaid: string }[] | undefined
							return diagrams && diagrams.length > 0 ? (
								<div className='mb-6 space-y-4'>
									<h2 className='text-lg font-bold text-gray-800'>图示解析</h2>
									{diagrams.map((diagram, idx) => (
										<div key={idx} className='rounded-xl border border-white/40 bg-white/60 p-4 backdrop-blur-sm'>
											{diagram.title && <h3 className='mb-2 text-sm font-semibold text-gray-700'>{diagram.title}</h3>}
											<MermaidBlock code={diagram.mermaid} />
										</div>
									))}
								</div>
							) : null
						})()}

						{(() => {
							const interp = note.ai_metadata?.ai_error_interpretation as { id: string; version: number; summary?: string; diagnosis?: string; root_cause?: string; knowledge_gap?: string; suggested_correction?: string; reasoning_trace?: string } | null | undefined
							const interpStatus = note.ai_metadata?.error_interpretation_status as string | undefined
							const diagramMeta = note.ai_metadata?.diagram as { strategy: string; strategy_reason?: string; structured_data?: Record<string, unknown>; image_url?: string; image_prompt?: string; accepted_interpretation_id?: string; uses_error_interpretation?: boolean } | null | undefined
							const userReason = note.ai_metadata?.user_error_reason as string | undefined
							const finalMeta = note.ai_metadata?.final_analysis as { analysis?: string; error_reason?: string; key_step?: string; similar_traps?: string[]; generalization?: string; review_advice?: string; accepted_interpretation_id?: string; accepted_interpretation_version?: number } | null | undefined

							if (!interp && !diagramMeta && !userReason && !finalMeta) return null

							return (
								<div className='mb-6 space-y-4'>
									<h2 className='text-lg font-bold text-gray-800'>分阶段错因分析</h2>

									{userReason && (
										<section className='rounded-xl border border-orange-200/70 bg-orange-50/50 p-4'>
											<h2 className='mb-2 text-sm font-semibold text-orange-800'>我自述的错因</h2>
											<p className='text-sm leading-6 text-orange-900'>{userReason}</p>
										</section>
									)}

									{interp && interpStatus === 'accepted' && (
										<section className='rounded-xl border border-green-200/70 bg-green-50/50 p-4'>
											<h2 className='mb-2 text-sm font-semibold text-green-800'>
												AI 错因理解
												<span className='ml-2 text-xs font-normal text-green-600'>已采纳</span>
											</h2>
											<div className='space-y-2 text-sm'>
												{interp.summary && <div><span className='font-medium text-green-700'>概括：</span><span className='text-green-900'>{interp.summary}</span></div>}
												{interp.diagnosis && <div><span className='font-medium text-green-700'>诊断：</span><span className='text-green-900'>{interp.diagnosis}</span></div>}
												{interp.root_cause && <div><span className='font-medium text-green-700'>根本原因：</span><span className='text-green-900'>{interp.root_cause}</span></div>}
												{interp.knowledge_gap && <div><span className='font-medium text-green-700'>知识缺口：</span><span className='text-green-900'>{interp.knowledge_gap}</span></div>}
												{interp.suggested_correction && <div><span className='font-medium text-green-700'>纠正方向：</span><span className='text-green-900'>{interp.suggested_correction}</span></div>}
												{interp.reasoning_trace && <div className='mt-2 p-2 bg-green-100/50 rounded text-xs text-green-800'><span className='font-medium'>推理链：</span>{interp.reasoning_trace}</div>}
											</div>
											<p className='text-xs text-green-600 mt-2'>ID: {interp.id} · 版本: {interp.version}</p>
										</section>
									)}

									{finalMeta && (
										<section className='rounded-xl border border-purple-200/70 bg-purple-50/50 p-4'>
											<h2 className='mb-2 text-sm font-semibold text-purple-800'>最终解析</h2>
											<div className='space-y-2 text-sm'>
												{finalMeta.error_reason && <div><span className='font-medium text-purple-700'>错误原因：</span><span className='text-purple-900'>{finalMeta.error_reason}</span></div>}
												{finalMeta.key_step && <div><span className='font-medium text-purple-700'>关键步骤：</span><span className='text-purple-900'>{finalMeta.key_step}</span></div>}
												{finalMeta.similar_traps && finalMeta.similar_traps.length > 0 && (
													<div><span className='font-medium text-purple-700'>相似陷阱：</span>
														<ul className='list-disc pl-4 text-purple-900'>
															{finalMeta.similar_traps.map((t, i) => <li key={i}>{t}</li>)}
														</ul>
													</div>
												)}
												{finalMeta.generalization && <div><span className='font-medium text-purple-700'>举一反三：</span><span className='text-purple-900'>{finalMeta.generalization}</span></div>}
												{finalMeta.review_advice && <div><span className='font-medium text-purple-700'>复习建议：</span><span className='text-purple-900'>{finalMeta.review_advice}</span></div>}
											</div>
											{finalMeta.accepted_interpretation_id && (
												<p className='text-xs text-purple-600 mt-2'>基于错因理解 v{finalMeta.accepted_interpretation_version}</p>
											)}
										</section>
									)}

									{diagramMeta && (
										<section className='rounded-xl border border-blue-200/70 bg-blue-50/50 p-4'>
											<h2 className='mb-2 text-sm font-semibold text-blue-800'>
												图解
												<span className='ml-2 text-xs font-normal text-blue-600'>
													{diagramMeta.strategy === 'structured' ? '结构化渲染' : 'AI 生成图片'}
												</span>
											</h2>
											{diagramMeta.uses_error_interpretation && (
												<p className='text-xs text-blue-600 mb-2'>使用了已采纳的错因理解</p>
											)}
											{diagramMeta.strategy === 'structured' && diagramMeta.structured_data && (() => {
												const sd = diagramMeta.structured_data as Record<string, unknown>
												const nodes = (sd.nodes || []) as { id: string; label: string; highlighted?: boolean; annotation?: string }[]
												const edges = (sd.edges || []) as { source: string; target: string; label?: string; highlighted?: boolean; weight?: string }[]
												const table = sd.table as { headers: string[]; rows: { cells: string[] }[]; caption?: string } | null
												const mermaid = sd.mermaid as string | undefined
												return (
													<div className='space-y-3'>
														{sd.title ? <p className='text-sm font-medium'>{String(sd.title)}</p> : null}
														{sd.caption ? <p className='text-xs text-muted-foreground'>{String(sd.caption)}</p> : null}
														{sd.error_reason_annotation ? <p className='text-xs text-yellow-600'>错因标注: {String(sd.error_reason_annotation)}</p> : null}

														{nodes.length > 0 && edges.length > 0 && (
															<div className='mt-3'>
																<StructuredGraphDiagram nodes={nodes} edges={edges} />
															</div>
														)}

														{table && table.headers.length > 0 && (
															<div className='mt-3 overflow-x-auto'>
																<table className='w-full text-xs border-collapse'>
																	<thead>
																		<tr>{table.headers.map((h, i) => <th key={i} className='border border-blue-200 px-2 py-1 bg-blue-100/50 text-left font-medium'>{h}</th>)}</tr>
																	</thead>
																	<tbody>
																		{table.rows.map((row, ri) => (
																			<tr key={ri}>{row.cells.map((c, ci) => <td key={ci} className='border border-blue-200 px-2 py-1'>{c}</td>)}</tr>
																		))}
																	</tbody>
																	{table.caption && <caption className='text-xs text-muted-foreground mt-1'>{table.caption}</caption>}
																</table>
															</div>
														)}

														{mermaid && (
															<div className='mt-3'>
																<MermaidBlock code={mermaid} />
															</div>
														)}
													</div>
												)
											})()}
											{diagramMeta.strategy === 'qwen_image_fallback' && diagramMeta.image_url && (
												<img src={diagramMeta.image_url} alt='AI 生成图解' className='max-w-full rounded-lg mt-2' />
											)}
											{diagramMeta.strategy === 'qwen_image_fallback' && !diagramMeta.image_url && diagramMeta.image_prompt && (
												<p className='text-xs text-muted-foreground mt-2'>图片生成服务未配置（prompt 已生成）</p>
											)}
										</section>
									)}
								</div>
							)
						})()}

						<RelatedKnowledgePanel note={note} />
					</>
				)}

				{actionBar}

				{!isAdmin && (
					<div className='mt-8 flex flex-wrap justify-center gap-3 border-t border-white/20 pt-6'>
						<Link href='/discover' className='text-sm text-gray-500 hover:text-[var(--color-brand)]'>发现更多</Link>
						<span className='text-gray-300'>·</span>
						<Link href='/guestbook' className='text-sm text-gray-500 hover:text-[var(--color-brand)]'>留言</Link>
						<span className='text-gray-300'>·</span>
						<Link href='/' className='text-sm text-gray-500 hover:text-[var(--color-brand)]'>回到首页</Link>
					</div>
				)}
				</motion.div>
			</div>
		)
	}

	return (
		<div className='mx-auto max-w-6xl px-4 py-8'>
			<motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
				<Link href={getContentListHref(note.type, folderId)} className='mb-4 inline-block text-sm text-gray-500 hover:text-gray-700'>
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

				<div className='mb-6'>
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

				{actionBar}

				{!isAdmin && (
					<div className='mt-8 flex flex-wrap justify-center gap-3 border-t border-white/20 pt-6'>
						<Link href='/discover' className='text-sm text-gray-500 hover:text-[var(--color-brand)]'>发现更多</Link>
						<span className='text-gray-300'>·</span>
						<Link href='/guestbook' className='text-sm text-gray-500 hover:text-[var(--color-brand)]'>留言</Link>
						<span className='text-gray-300'>·</span>
						<Link href='/' className='text-sm text-gray-500 hover:text-[var(--color-brand)]'>回到首页</Link>
					</div>
				)}
			</motion.div>
		</div>
	)
}

function Metric({ label, value, highlight = false }: { label: string; value: string; highlight?: boolean }) {
	return (
		<div className={cn('rounded-lg bg-white/50 px-2 py-2', highlight && 'bg-red-500/10')}>
			<div className={cn('text-base font-semibold text-gray-800', highlight && 'text-red-500')}>{value}</div>
			<div className='text-[11px] text-gray-500'>{label}</div>
		</div>
	)
}

function StudyBlock({ title, content, fallback, tone, large = false }: { title: string; content?: string | null; fallback?: string | null; tone: 'neutral' | 'danger' | 'success' | 'info' | 'purple'; large?: boolean }) {
	const value = content || fallback
	if (!value) return null
	const toneClass = {
		neutral: 'border-gray-200/70 bg-gray-50/50 text-gray-800',
		danger: 'border-red-200/70 bg-red-50/50 text-red-900',
		success: 'border-green-200/70 bg-green-50/50 text-green-900',
		info: 'border-blue-200/70 bg-blue-50/50 text-blue-950',
		purple: 'border-purple-200/70 bg-purple-50/50 text-purple-950',
	}[tone]

	return (
		<section className={cn('rounded-xl border p-4', toneClass, large && 'min-h-[260px] p-5 sm:p-6')}>
			<h2 className={cn('mb-2 text-sm font-semibold', large && 'mb-5 text-base')}>{title}</h2>
			<RichText content={value} className={cn('text-sm leading-6', large && 'text-base leading-8')} />
		</section>
	)
}
