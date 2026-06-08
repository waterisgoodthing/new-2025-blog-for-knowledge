'use client'

import { useState, useEffect } from 'react'
import { motion } from 'motion/react'
import { Calendar, BookOpen, AlertCircle, CheckCircle, Save, ChevronDown, ChevronRight } from 'lucide-react'
import { toast } from 'sonner'
import { cn } from '@/lib/utils'
import { getWeeklySummary, type WeeklySummary } from '@/lib/api/knowledge-assistant'
import { createNote } from '@/lib/api/notes'
import dayjs from 'dayjs'

export function WeeklySummaryCard() {
	const [summary, setSummary] = useState<WeeklySummary | null>(null)
	const [loading, setLoading] = useState(true)
	const [saving, setSaving] = useState(false)
	const [expanded, setExpanded] = useState(true)

	useEffect(() => {
		getWeeklySummary()
			.then(setSummary)
			.catch(() => {})
			.finally(() => setLoading(false))
	}, [])

	const handleSaveAsNote = async () => {
		if (!summary) return
		setSaving(true)
		try {
			const weekLabel = `${dayjs(summary.week_start).format('MM-DD')} ~ ${dayjs(summary.week_end).format('MM-DD')}`
			const content = [
				`# 周度学习总结 (${weekLabel})`,
				'',
				'## 本周数据',
				`- 新增笔记: ${summary.new_notes} 篇`,
				`- 新增错题: ${summary.new_mistakes} 道`,
				`- 复习完成: ${summary.reviewed_count} 道`,
				'',
				...(summary.top_subjects.length > 0 ? [
					'## 主要科目',
					...summary.top_subjects.map(s => `- ${s.subject}: ${s.count} 道错题`),
					'',
				] : []),
				...(summary.top_knowledge_points.length > 0 ? [
					'## 高频知识点',
					...summary.top_knowledge_points.map(k => `- ${k.name}: ${k.count} 次`),
					'',
				] : []),
			].join('\n')

			await createNote({
				slug: `weekly-${dayjs(summary.week_start).format('YYYYMMDD')}`,
				title: `周度学习总结 (${weekLabel})`,
				content,
				type: 'note',
				tags: ['周度总结', '自动生成'],
			})
			toast.success('已保存为笔记')
		} catch (e: any) {
			toast.error('保存失败: ' + e.message)
		} finally {
			setSaving(false)
		}
	}

	if (loading || !summary) return null

	const weekLabel = `${dayjs(summary.week_start).format('MM-DD')} ~ ${dayjs(summary.week_end).format('MM-DD')}`

	return (
		<motion.div
			initial={{ opacity: 0, y: 10 }}
			animate={{ opacity: 1, y: 0 }}
			className='rounded-xl border border-white/40 bg-white/60 p-4 backdrop-blur-sm'
		>
			<div className='mb-3 flex items-center justify-between'>
				<button type='button' onClick={() => setExpanded(!expanded)} className='flex items-center gap-2 text-left' aria-label={expanded ? '收起周度总结' : '展开周度总结'}>
					<Calendar size={16} className='text-[var(--color-brand)]' />
					<span className='text-sm font-semibold text-gray-800'>周度总结</span>
					<span className='text-xs text-gray-400'>{weekLabel}</span>
					{expanded ? <ChevronDown size={14} className='text-gray-400' /> : <ChevronRight size={14} className='text-gray-400' />}
				</button>
				<button
					onClick={handleSaveAsNote}
					disabled={saving}
					className='flex items-center gap-1 rounded-lg bg-[var(--color-brand)]/10 px-2 py-1 text-xs text-[var(--color-brand)] transition-colors hover:bg-[var(--color-brand)]/20 disabled:opacity-50'
				>
					<Save size={12} />
					{saving ? '保存中...' : '保存为笔记'}
				</button>
			</div>

			{expanded && (<>
				<div className='mb-3 grid grid-cols-3 gap-2 text-center'>
					<div className='rounded-lg bg-white/50 px-2 py-2'>
						<div className='flex items-center justify-center gap-1'>
							<BookOpen size={12} className='text-blue-500' />
							<span className='text-lg font-semibold text-blue-500'>{summary.new_notes}</span>
						</div>
						<div className='text-[11px] text-gray-500'>新增笔记</div>
					</div>
					<div className='rounded-lg bg-white/50 px-2 py-2'>
						<div className='flex items-center justify-center gap-1'>
							<AlertCircle size={12} className='text-red-500' />
							<span className='text-lg font-semibold text-red-500'>{summary.new_mistakes}</span>
						</div>
						<div className='text-[11px] text-gray-500'>新增错题</div>
					</div>
					<div className='rounded-lg bg-white/50 px-2 py-2'>
						<div className='flex items-center justify-center gap-1'>
							<CheckCircle size={12} className='text-green-500' />
							<span className='text-lg font-semibold text-green-500'>{summary.reviewed_count}</span>
						</div>
						<div className='text-[11px] text-gray-500'>复习完成</div>
					</div>
				</div>

				{summary.top_subjects.length > 0 && (
					<div className='mb-2'>
						<div className='mb-1.5 text-xs font-medium text-gray-500'>主要科目</div>
						<div className='flex flex-wrap gap-1.5'>
							{summary.top_subjects.map(s => (
								<span key={s.subject} className='rounded-full bg-purple-500/15 px-2 py-0.5 text-xs text-purple-600'>
									{s.subject} ({s.count})
								</span>
							))}
						</div>
					</div>
				)}

				{summary.top_knowledge_points.length > 0 && (
					<div>
						<div className='mb-1.5 text-xs font-medium text-gray-500'>高频知识点</div>
						<div className='flex flex-wrap gap-1.5'>
							{summary.top_knowledge_points.map(k => (
								<span key={k.name} className='rounded-full bg-amber-500/15 px-2 py-0.5 text-xs text-amber-600'>
									{k.name} ({k.count})
								</span>
							))}
						</div>
					</div>
				)}
			</>)}
		</motion.div>
	)
}
