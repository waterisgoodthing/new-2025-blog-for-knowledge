'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { motion } from 'motion/react'
import { createNote, uploadImage } from '@/lib/api/notes'
import { analyzeMistake, analyzeText, type AnalyzeResponse } from '@/lib/api/ai'
import { listSubjects, type Subject } from '@/lib/api/meta'
import { toast } from 'sonner'
import { cn } from '@/lib/utils'
import { getContentDetailHref } from '@/lib/content-routes'

export default function WriteMistakePage() {
	const router = useRouter()
	const [saving, setSaving] = useState(false)
	const [analyzing, setAnalyzing] = useState(false)
	const [uploadedImages, setUploadedImages] = useState<string[]>([])
	const [pasteText, setPasteText] = useState('')
	const [subjects, setSubjects] = useState<Subject[]>([])
	const [form, setForm] = useState({
		slug: '',
		title: '',
		question: '',
		my_answer: '',
		correct_answer: '',
		analysis: '',
		knowledge_points: '',
		subject: '',
		difficulty: 'medium' as 'easy' | 'medium' | 'hard',
		tags: [] as string[],
		tagInput: '',
	})
	const [aiMetadata, setAiMetadata] = useState<Record<string, unknown> | null>(null)

	const update = (k: string, v: any) => setForm(f => ({ ...f, [k]: v }))

	useEffect(() => {
		listSubjects().then(setSubjects).catch(() => {})
	}, [])

	const addTag = () => {
		const tag = form.tagInput.trim()
		if (tag && !form.tags.includes(tag)) {
			update('tags', [...form.tags, tag])
			update('tagInput', '')
		}
	}

	const buildAnalysisText = (result: AnalyzeResponse) => {
		const sections = [
			result.analysis && `### 详细解析\n\n${result.analysis}`,
			result.error_reason && `### 错误原因\n\n${result.error_reason}`,
			result.key_step && `### 关键步骤\n\n${result.key_step}`,
			(result.similar_traps?.length ?? 0) > 0 && `### 相似易错点\n\n${result.similar_traps!.map(item => `- ${item}`).join('\n')}`,
			result.generalization && `### 举一反三\n\n${result.generalization}`,
			result.review_advice && `### 复习建议\n\n${result.review_advice}`,
			(result.variant_questions?.length ?? 0) > 0 && `### 变式题\n\n${result.variant_questions!.map((item, index) => `${index + 1}. ${item}`).join('\n')}`,
		]
		return sections.filter(Boolean).join('\n\n')
	}

	const applyResult = (result: AnalyzeResponse) => {
		setForm(f => ({
			...f,
			title: result.title || f.title,
			question: result.question || f.question,
			correct_answer: result.correct_answer || f.correct_answer,
			analysis: buildAnalysisText(result) || f.analysis,
			knowledge_points: result.knowledge_points || f.knowledge_points,
			subject: result.subject || f.subject,
			difficulty: (result.difficulty as any) || f.difficulty,
			tags: [...new Set([...f.tags, ...result.tags])],
		}))
		setAiMetadata({
			error_reason: result.error_reason || '',
			key_step: result.key_step || '',
			similar_traps: result.similar_traps || [],
			generalization: result.generalization || '',
			review_advice: result.review_advice || '',
			variant_questions: result.variant_questions || [],
			related_notes: result.related_notes || [],
		})
	}

	const uploadAndAnalyzeFiles = async (files: File[]) => {
		setAnalyzing(true)
		try {
			// 1. Upload images to the backend to get hosted URL paths
			const uploadPromises = files.map(async file => {
				const res = await uploadImage(file, { noteType: 'mistake', slug: form.slug || undefined })
				return res.url
			})
			const urls = await Promise.all(uploadPromises)
			setUploadedImages(prev => [...prev, ...urls])
			toast.success(`成功上传 ${urls.length} 张图片`)

			// 2. Read images as base64 for AI analysis
			const base64Promises = files.map(file => {
				return new Promise<{ base64: string; mime_type: string }>((resolve, reject) => {
					const reader = new FileReader()
					reader.onload = () => {
						const base64 = (reader.result as string).split(',')[1]
						resolve({ base64, mime_type: file.type })
					}
					reader.onerror = reject
					reader.readAsDataURL(file)
				})
			})
			const images = await Promise.all(base64Promises)
			const result = await analyzeMistake(images)
			applyResult(result)
		} catch (err: any) {
			toast.error('处理失败: ' + err.message)
		} finally {
			setAnalyzing(false)
		}
	}

	const handleImageUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
		const files = e.target.files
		if (!files || files.length === 0) return
		await uploadAndAnalyzeFiles(Array.from(files))
	}

	const handleDragOver = (e: React.DragEvent) => {
		e.preventDefault()
	}

	const handleDrop = async (e: React.DragEvent) => {
		e.preventDefault()
		const files = e.dataTransfer.files
		if (!files || files.length === 0) return
		await uploadAndAnalyzeFiles(Array.from(files))
	}

	const handleTextAnalyze = async () => {
		const text = pasteText.trim()
		if (!text) return

		setAnalyzing(true)
		try {
			const result = await analyzeText(text)
			applyResult(result)
			setPasteText('')
		} catch (err: any) {
			toast.error('AI 分析失败: ' + err.message)
		} finally {
			setAnalyzing(false)
		}
	}

	const handleSave = async () => {
		if (!form.title.trim()) return toast.warning('请输入标题')

		setSaving(true)
		try {
			const autoSlug = form.title.trim().toLowerCase().replace(/[^\w]+/g, '-').replace(/^-|-$/g, '') || `note-${Date.now()}`
			const slug = form.slug.trim() || autoSlug
			const content = [
				form.question && `## 题目\n\n${form.question}`,
				form.my_answer && `## 我的错误答案\n\n${form.my_answer}`,
				form.correct_answer && `## 正确答案\n\n${form.correct_answer}`,
				form.analysis && `## 分析\n\n${form.analysis}`,
				form.knowledge_points && `## 知识点\n\n${form.knowledge_points}`,
			].filter(Boolean).join('\n\n')

			const created = await createNote({
				slug,
				title: form.title,
				content,
				type: 'mistake',
				tags: form.tags,
				subject: form.subject || undefined,
				difficulty: form.difficulty,
				question: form.question,
				my_answer: form.my_answer,
				correct_answer: form.correct_answer,
				analysis: form.analysis,
				knowledge_points: form.knowledge_points,
				images: uploadedImages,
				ai_metadata: aiMetadata,
			})
			router.push(getContentDetailHref(created.type, created.slug))
		} catch (e: any) {
			toast.error('保存失败: ' + e.message)
		} finally {
			setSaving(false)
		}
	}

	return (
		<div className='mx-auto max-w-3xl px-4 py-8'>
			<motion.h1 initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} className='mb-6 text-2xl font-bold'>
				添加错题
			</motion.h1>

			{analyzing && (
				<motion.div
					initial={{ opacity: 0, y: 10 }}
					animate={{ opacity: 1, y: 0 }}
					className='mb-4 flex items-center gap-3 rounded-xl border border-[var(--color-brand)]/20 bg-[var(--color-brand)]/5 px-4 py-3 backdrop-blur-sm'
				>
					<div className='relative h-5 w-5'>
						<div className='absolute inset-0 rounded-full border-2 border-[var(--color-brand)]/20' />
						<div className='absolute inset-0 animate-spin rounded-full border-2 border-transparent border-t-[var(--color-brand)]' />
					</div>
					<span className='text-sm font-medium text-[var(--color-brand)]'>正在解决你的问题哦</span>
				</motion.div>
			)}

			<div className='space-y-4'>
				<div
					onDragOver={handleDragOver}
					onDrop={handleDrop}
					className='rounded-xl border border-dashed border-[var(--color-brand)]/50 bg-white/40 p-6 text-center backdrop-blur-sm hover:bg-white/60 transition-colors'
				>
					<label className='cursor-pointer block w-full h-full'>
						<input type='file' accept='image/*' multiple onChange={handleImageUpload} className='hidden' />
						<div className='mb-2 text-3xl'>📷</div>
						<div className='text-sm text-gray-600 font-medium'>
							{analyzing ? 'AI 分析中...' : '拖拽或点击上传错题图片，AI 自动生成内容'}
						</div>
						<div className='mt-1 text-xs text-gray-400'>支持 JPG、PNG、WebP，拖入即可上传</div>
					</label>
				</div>

				{uploadedImages.length > 0 && (
					<div className='grid grid-cols-4 gap-3 rounded-xl border border-white/40 bg-white/20 p-3 backdrop-blur-sm sm:grid-cols-6'>
						{uploadedImages.map((url, idx) => (
							<div key={url} className='relative aspect-square rounded-lg overflow-hidden border border-gray-200 bg-gray-50 group shadow-sm'>
								<img src={url} alt={`uploaded-${idx}`} className='h-full w-full object-cover' />
								<button
									type='button'
									onClick={() => setUploadedImages(prev => prev.filter(x => x !== url))}
									aria-label={`删除第 ${idx + 1} 张错题图片`}
									className='absolute top-1 right-1 flex items-center justify-center h-5 w-5 rounded-full bg-black/50 text-white text-xs hover:bg-red-600 transition-colors shadow'
									title="删除图片"
								>
									×
								</button>
							</div>
						))}
					</div>
				)}

				<div className='rounded-xl border border-dashed border-blue-300/50 bg-white/40 p-4 backdrop-blur-sm'>
					<div className='mb-2 text-center text-sm text-gray-600'>📋 粘贴题目文本，AI 自动分析</div>
					<textarea
						value={pasteText}
						onChange={e => setPasteText(e.target.value)}
						placeholder='在此粘贴题目文本...'
						rows={5}
						className='mb-3 w-full rounded-lg border border-white/40 bg-white/60 px-3 py-2 text-sm backdrop-blur-sm outline-none focus:border-[var(--color-brand)]'
					/>
					<button
						onClick={handleTextAnalyze}
						disabled={analyzing || !pasteText.trim()}
						className='w-full rounded-lg bg-[var(--color-brand)] py-2 text-sm text-white transition-transform hover:scale-[1.02] active:scale-[0.98] disabled:opacity-50'
					>
						{analyzing ? '分析中...' : 'AI 分析'}
					</button>
				</div>

				<input
					value={form.title}
					onChange={e => {
						update('title', e.target.value)
						if (!form.slug) {
							const s = e.target.value.toLowerCase().replace(/[^\w]+/g, '-').replace(/^-|-$/g, '')
							update('slug', s || `note-${Date.now()}`)
						}
					}}
					placeholder='标题'
					className='w-full rounded-xl border border-white/40 bg-white/60 px-4 py-3 text-lg backdrop-blur-sm outline-none focus:border-[var(--color-brand)]'
				/>

				<div className='flex gap-3'>
					<select
						value={form.difficulty}
						onChange={e => update('difficulty', e.target.value)}
						className='rounded-lg border border-white/40 bg-white/60 px-3 py-2 text-sm outline-none'
					>
						<option value='easy'>简单</option>
						<option value='medium'>中等</option>
						<option value='hard'>困难</option>
					</select>
				<input
					value={form.subject}
					onChange={e => update('subject', e.target.value)}
					list='subject-options-mistake'
					placeholder='科目'
					className='flex-1 rounded-lg border border-white/40 bg-white/60 px-3 py-2 text-sm outline-none'
				/>
				<datalist id='subject-options-mistake'>
					{subjects.map(s => <option key={s.id} value={s.name} />)}
				</datalist>
				</div>

				<textarea
					value={form.question}
					onChange={e => update('question', e.target.value)}
					placeholder='题目内容...'
					rows={4}
					className='w-full rounded-xl border border-white/40 bg-white/60 px-4 py-3 text-sm backdrop-blur-sm outline-none focus:border-[var(--color-brand)]'
				/>

				<textarea
					value={form.my_answer}
					onChange={e => update('my_answer', e.target.value)}
					placeholder='我的错误答案...'
					rows={3}
					className='w-full rounded-xl border border-red-200/50 bg-red-50/30 px-4 py-3 text-sm outline-none focus:border-red-400'
				/>

				<textarea
					value={form.correct_answer}
					onChange={e => update('correct_answer', e.target.value)}
					placeholder='正确答案...'
					rows={3}
					className='w-full rounded-xl border border-green-200/50 bg-green-50/30 px-4 py-3 text-sm outline-none focus:border-green-400'
				/>

				<textarea
					value={form.analysis}
					onChange={e => update('analysis', e.target.value)}
					placeholder='分析与反思...'
					rows={3}
					className='w-full rounded-xl border border-blue-200/50 bg-blue-50/30 px-4 py-3 text-sm outline-none focus:border-blue-400'
				/>

				<input
					value={form.knowledge_points}
					onChange={e => update('knowledge_points', e.target.value)}
					placeholder='知识点总结'
					className='w-full rounded-xl border border-purple-200/50 bg-purple-50/30 px-4 py-3 text-sm outline-none focus:border-purple-400'
				/>

				<div>
					<div className='mb-2 flex gap-2'>
						<input
							value={form.tagInput}
							onChange={e => update('tagInput', e.target.value)}
							onKeyDown={e => e.key === 'Enter' && (e.preventDefault(), addTag())}
							placeholder='添加标签'
							className='flex-1 rounded-lg border border-white/40 bg-white/60 px-3 py-2 text-sm outline-none'
						/>
						<button onClick={addTag} className='rounded-lg bg-white/60 px-3 py-2 text-sm hover:bg-white/80'>添加</button>
					</div>
					<div className='flex flex-wrap gap-2'>
						{form.tags.map(t => (
							<span key={t} className='flex items-center gap-1 rounded-full bg-gray-200/60 px-3 py-1 text-xs'>
								{t}
								<button
									type='button'
									onClick={() => update('tags', form.tags.filter((x: string) => x !== t))}
									aria-label={`删除标签 ${t}`}
									title={`删除标签 ${t}`}
									className='text-gray-400 hover:text-red-500'>
									×
								</button>
							</span>
						))}
					</div>
				</div>

				<div className='flex gap-3 pt-4'>
					<button
						onClick={handleSave}
						disabled={saving}
						className='rounded-xl bg-[var(--color-brand)] px-6 py-2.5 text-sm text-white transition-transform hover:scale-105 active:scale-95 disabled:opacity-50'
					>
						{saving ? '保存中...' : '发布'}
					</button>
					<button onClick={() => router.back()} className='rounded-xl bg-white/60 px-6 py-2.5 text-sm hover:bg-white/80'>取消</button>
				</div>
			</div>
		</div>
	)
}
