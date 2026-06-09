'use client'

import { useState, useEffect, useRef } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { motion } from 'motion/react'
import { createNote, updateNote, uploadImage, type NoteDetail } from '@/lib/api/notes'
import { analyzeMistake, analyzeText, analyzeMistakeStream, analyzeTextStream, type AnalyzeResponse } from '@/lib/api/ai'
import { listSubjects, type Subject } from '@/lib/api/meta'
import { toast } from 'sonner'
import { cn } from '@/lib/utils'
import { getContentDetailHref } from '@/lib/content-routes'
import { TagSuggestionDialog } from '@/components/tag-suggestion-dialog'
import { resolveImageUrl } from '@/lib/api/images'
import Link from 'next/link'
import { ClipboardPaste, ImageUp, Loader2, Sparkles, ArrowLeft } from 'lucide-react'

interface MistakeFormProps {
	mode: 'create' | 'edit'
	initialData?: NoteDetail
}

export function MistakeForm({ mode, initialData }: MistakeFormProps) {
	const router = useRouter()
	const searchParams = useSearchParams()
	const [saving, setSaving] = useState(false)
	const [analyzing, setAnalyzing] = useState(false)
	const [showTagSuggestion, setShowTagSuggestion] = useState(false)
	const [pendingSave, setPendingSave] = useState<((tags?: string[]) => Promise<void>) | null>(null)
	const [analyzeError, setAnalyzeError] = useState<string | null>(null)
	const [phaseText, setPhaseText] = useState('')
	const abortRef = useRef<AbortController | null>(null)
	const lastAnalyzeRef = useRef<(() => Promise<void>) | null>(null)
	const [uploadedImages, setUploadedImages] = useState<string[]>([])
	const [removedImages, setRemovedImages] = useState<string[]>([])
	const [pasteText, setPasteText] = useState('')
	const [generatingField, setGeneratingField] = useState<'analysis' | 'knowledge_points' | null>(null)
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

	useEffect(() => {
		if (initialData) {
			setForm({
				slug: initialData.slug,
				title: initialData.title,
				question: initialData.question || '',
				my_answer: initialData.my_answer || '',
				correct_answer: initialData.correct_answer || '',
				analysis: initialData.analysis || '',
				knowledge_points: initialData.knowledge_points || '',
				subject: initialData.subject || '',
				difficulty: (initialData.difficulty as 'easy' | 'medium' | 'hard') || 'medium',
				tags: initialData.tags?.map(t => t.name) || [],
				tagInput: '',
			})
			setUploadedImages(initialData.images || [])
			setAiMetadata(initialData.ai_metadata || null)
		}
	}, [initialData])

	useEffect(() => {
		if (searchParams.get('ai_prefill') === '1') {
			try {
				const stored = sessionStorage.getItem('ai_prefill_mistake')
				if (stored) {
					const data = JSON.parse(stored)
					setForm(f => ({
						...f,
						title: data.title || f.title,
						question: data.question || f.question,
						correct_answer: data.correct_answer || f.correct_answer,
						analysis: data.analysis || f.analysis,
						knowledge_points: data.knowledge_points || f.knowledge_points,
						subject: data.subject || f.subject,
						difficulty: data.difficulty || f.difficulty,
					}))
					sessionStorage.removeItem('ai_prefill_mistake')
				}
			} catch {}
		}
	}, [searchParams])

	const update = (k: string, v: any) => setForm(f => ({ ...f, [k]: v }))

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
			diagrams: result.diagrams || [],
		})
	}

	useEffect(() => {
		listSubjects().then(setSubjects).catch(() => {})
	}, [])

	const uploadAndAnalyzeFiles = async (files: File[]) => {
		abortRef.current?.abort()
		const controller = new AbortController()
		abortRef.current = controller

		setAnalyzing(true)
		setAnalyzeError(null)
		setPhaseText('正在上传图片...')
		try {
			const uploadPromises = files.map(async file => {
				const res = await uploadImage(file, { noteType: 'mistake', slug: form.slug || undefined })
				return res.url
			})
			const urls = await Promise.all(uploadPromises)
			setUploadedImages(prev => [...prev, ...urls])
			toast.success(`成功上传 ${urls.length} 张图片`)

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

			await analyzeMistakeStream(images, (event) => {
				if (event.type === 'progress' || event.type === 'received') {
					setPhaseText(event.label)
				} else if (event.type === 'result') {
					applyResult(event.data)
				} else if (event.type === 'error') {
					setAnalyzeError(event.message)
					toast.error('处理失败: ' + event.message)
				} else if (event.type === 'done') {
					// handled by result
				}
			}, controller.signal)
		} catch (err: any) {
			if (err.name === 'AbortError') return
			setAnalyzeError(err.message || '分析失败')
			toast.error('处理失败: ' + err.message)
		} finally {
			setAnalyzing(false)
			setPhaseText('')
			abortRef.current = null
		}
	}

	const handleImageUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
		const files = e.target.files
		if (!files || files.length === 0) return
		lastAnalyzeRef.current = () => uploadAndAnalyzeFiles(Array.from(files))
		await uploadAndAnalyzeFiles(Array.from(files))
	}

	const handleDragOver = (e: React.DragEvent) => { e.preventDefault() }

	const handleDrop = async (e: React.DragEvent) => {
		e.preventDefault()
		const files = e.dataTransfer.files
		if (!files || files.length === 0) return
		lastAnalyzeRef.current = () => uploadAndAnalyzeFiles(Array.from(files))
		await uploadAndAnalyzeFiles(Array.from(files))
	}

	const handleTextAnalyze = async () => {
		const text = pasteText.trim()
		if (!text) return toast.warning('请先粘贴题目文本')
		abortRef.current?.abort()
		const controller = new AbortController()
		abortRef.current = controller

		setAnalyzing(true)
		setAnalyzeError(null)
		setPhaseText('正在分析文本...')
		lastAnalyzeRef.current = async () => { await handleTextAnalyze() }
		try {
			await analyzeTextStream(text, (event) => {
				if (event.type === 'progress' || event.type === 'received') {
					setPhaseText(event.label)
				} else if (event.type === 'result') {
					applyResult(event.data)
					setPasteText('')
					toast.success('AI 分析完成，已填入下方表单')
				} else if (event.type === 'error') {
					setAnalyzeError(event.message)
					toast.error('AI 分析失败: ' + event.message)
				}
			}, controller.signal)
		} catch (err: any) {
			if (err.name === 'AbortError') return
			setAnalyzeError(err.message || 'AI 分析失败')
			toast.error('AI 分析失败: ' + err.message)
		} finally {
			setAnalyzing(false)
			setPhaseText('')
			abortRef.current = null
		}
	}

	const handleRetry = async () => {
		setAnalyzeError(null)
		abortRef.current?.abort()
		if (lastAnalyzeRef.current) await lastAnalyzeRef.current()
	}

	const hasAiInput = pasteText.trim().length > 0

	const handlePartialAnalyze = async (field: 'analysis' | 'knowledge_points') => {
		const text = pasteText.trim()
		if (!text) return toast.warning('请先粘贴题目文本')
		setGeneratingField(field)
		try {
			const result = await analyzeText(text)
			if (field === 'analysis') {
				const analysisText = buildAnalysisText(result)
				if (analysisText) update('analysis', analysisText)
			} else {
				if (result.knowledge_points) update('knowledge_points', result.knowledge_points)
			}
			toast.success(field === 'analysis' ? 'AI 解析已生成' : 'AI 知识点已生成')
		} catch (err: any) {
			toast.error('AI 生成失败: ' + (err.message || '未知错误'))
		} finally {
			setGeneratingField(null)
		}
	}

	const handleRemoveImage = (url: string) => {
		setUploadedImages(prev => prev.filter(x => x !== url))
		if (mode === 'edit' && initialData?.images?.includes(url)) {
			setRemovedImages(prev => [...prev, url])
		}
	}

	const handleSave = async () => {
		if (!form.title.trim()) return toast.warning('请输入标题')
		if (form.tags.length === 0) {
			const skipReminder = localStorage.getItem('skipEmptyTagReminder')
			if (skipReminder === 'true') {
				await performSave()
				return
			}
			setPendingSave(() => performSave)
			setShowTagSuggestion(true)
			return
		}
		await performSave()
	}

	const performSave = async (overrideTags?: string[]) => {
		const tags = overrideTags ?? form.tags
		setSaving(true)
		try {
			const content = [
				form.question && `## 题目\n\n${form.question}`,
				form.my_answer && `## 我的错误答案\n\n${form.my_answer}`,
				form.correct_answer && `## 正确答案\n\n${form.correct_answer}`,
				form.analysis && `## 分析\n\n${form.analysis}`,
				form.knowledge_points && `## 知识点\n\n${form.knowledge_points}`,
			].filter(Boolean).join('\n\n')

			const payload = {
				title: form.title,
				content,
				type: 'mistake' as const,
				tags,
				subject: form.subject || undefined,
				difficulty: form.difficulty,
				question: form.question,
				my_answer: form.my_answer,
				correct_answer: form.correct_answer,
				analysis: form.analysis,
				knowledge_points: form.knowledge_points,
				images: uploadedImages,
				ai_metadata: aiMetadata,
			}

			let result: NoteDetail
			if (mode === 'edit' && initialData) {
				result = await updateNote(initialData.slug, payload)
			} else {
				const autoSlug = form.title.trim().toLowerCase().replace(/[^\w]+/g, '-').replace(/^-|-$/g, '') || `note-${Date.now()}`
				const slug = form.slug.trim() || autoSlug
				result = await createNote({ ...payload, slug })
			}
			router.push(getContentDetailHref(result.type, result.slug))
		} catch (e: any) {
			toast.error('保存失败: ' + e.message)
		} finally {
			setSaving(false)
		}
	}

	return (
		<div className='mx-auto max-w-3xl px-4 py-8'>
			<div className='mb-6 flex items-center gap-4'>
				<Link
					href='/mistakes'
					aria-label='返回错题集'
					className='flex h-9 w-9 items-center justify-center rounded-xl border border-white/40 bg-white/60 text-gray-600 transition-colors hover:bg-white/80 hover:text-gray-800'
				>
					<ArrowLeft size={18} />
				</Link>
				<motion.h1 initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} className='text-2xl font-bold'>
					{mode === 'edit' ? '编辑错题' : '添加错题'}
				</motion.h1>
			</div>

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
					<span className='text-sm font-medium text-[var(--color-brand)]'>{phaseText || '正在处理...'}</span>
				</motion.div>
			)}

			{analyzeError && !analyzing && (
				<motion.div
					initial={{ opacity: 0, y: 10 }}
					animate={{ opacity: 1, y: 0 }}
					className='mb-4 flex items-center justify-between gap-3 rounded-xl border border-red-200 bg-red-50/80 px-4 py-3 backdrop-blur-sm'
				>
					<span className='text-sm text-red-600'>分析失败: {analyzeError}</span>
					<button
						type='button'
						onClick={handleRetry}
						className='shrink-0 rounded-lg bg-red-100 px-3 py-1.5 text-xs font-medium text-red-600 transition-colors hover:bg-red-200'
					>
						重试
					</button>
				</motion.div>
			)}

			<div className='space-y-4'>
				<section className='rounded-2xl border border-[var(--color-brand)]/25 bg-white/55 p-5 shadow-sm backdrop-blur-sm'>
					<div className='mb-4 flex flex-wrap items-center justify-between gap-3'>
						<div className='flex items-center gap-3'>
							<div className='flex h-10 w-10 items-center justify-center rounded-2xl bg-[var(--color-brand)] text-white shadow-sm'>
								<Sparkles className='h-5 w-5' />
							</div>
							<div>
								<h2 className='text-base font-semibold text-gray-800'>AI 分析错题</h2>
								<p className='mt-1 text-xs text-gray-500'>粘贴题目或上传图片，点击按钮自动填充。</p>
							</div>
						</div>
						<span className='rounded-full bg-[var(--color-brand)]/10 px-3 py-1 text-xs font-medium text-[var(--color-brand)]'>错题助手</span>
					</div>

					<div className='grid gap-4 md:grid-cols-[1fr_220px]'>
						<div className='rounded-xl border border-white/50 bg-white/50 p-4'>
							<label htmlFor='mistake-ai-text' className='mb-2 flex items-center gap-2 text-sm font-medium text-gray-700'>
								<ClipboardPaste className='h-4 w-4 text-[var(--color-brand)]' />
								粘贴题目文本
							</label>
							<textarea
								id='mistake-ai-text'
								value={pasteText}
								onChange={e => setPasteText(e.target.value)}
								placeholder='把题干、选项、你的答案或题目要求粘贴到这里...'
								rows={6}
								className='mb-3 w-full rounded-lg border border-white/60 bg-white/75 px-3 py-2 text-sm leading-6 backdrop-blur-sm outline-none focus:border-[var(--color-brand)]'
							/>
							<button
								type='button'
								onClick={handleTextAnalyze}
								disabled={analyzing || !pasteText.trim()}
								title='分析粘贴的题目文本'
								className='inline-flex w-full items-center justify-center gap-2 rounded-xl bg-[var(--color-brand)] px-4 py-2.5 text-sm font-medium text-white shadow-sm transition-transform hover:scale-[1.01] active:scale-[0.99] disabled:cursor-not-allowed disabled:opacity-50'
							>
								{analyzing ? <Loader2 className='h-4 w-4 animate-spin' /> : <Sparkles className='h-4 w-4' />}
								{analyzing ? 'AI 解析中...' : 'AI 智能解析题目'}
							</button>
							<div className='mt-2 grid grid-cols-2 gap-2'>
								<button
									type='button'
									onClick={() => handlePartialAnalyze('analysis')}
									disabled={generatingField !== null || !hasAiInput}
									title='仅生成解析部分'
									className='inline-flex items-center justify-center gap-1.5 rounded-lg border border-white/50 bg-white/60 px-3 py-2 text-xs font-medium text-gray-600 backdrop-blur-sm transition-colors hover:bg-white/80 disabled:cursor-not-allowed disabled:opacity-50'
								>
									{generatingField === 'analysis' ? <Loader2 className='h-3.5 w-3.5 animate-spin' /> : <Sparkles className='h-3.5 w-3.5' />}
									{generatingField === 'analysis' ? '生成中...' : 'AI 生成解析'}
								</button>
								<button
									type='button'
									onClick={() => handlePartialAnalyze('knowledge_points')}
									disabled={generatingField !== null || !hasAiInput}
									title='仅生成知识点部分'
									className='inline-flex items-center justify-center gap-1.5 rounded-lg border border-white/50 bg-white/60 px-3 py-2 text-xs font-medium text-gray-600 backdrop-blur-sm transition-colors hover:bg-white/80 disabled:cursor-not-allowed disabled:opacity-50'
								>
									{generatingField === 'knowledge_points' ? <Loader2 className='h-3.5 w-3.5 animate-spin' /> : <Sparkles className='h-3.5 w-3.5' />}
									{generatingField === 'knowledge_points' ? '生成中...' : 'AI 生成知识点'}
								</button>
							</div>
						</div>

						<div
							onDragOver={handleDragOver}
							onDrop={handleDrop}
							className='rounded-xl border border-dashed border-[var(--color-brand)]/45 bg-[var(--color-brand)]/5 p-4 text-center transition-colors hover:bg-[var(--color-brand)]/10'
						>
							<label className='flex h-full min-h-[184px] cursor-pointer flex-col items-center justify-center gap-3'>
								<input type='file' accept='image/*' multiple onChange={handleImageUpload} className='hidden' />
								<div className='flex h-12 w-12 items-center justify-center rounded-2xl bg-white/80 text-[var(--color-brand)] shadow-sm'>
									<ImageUp className='h-6 w-6' />
								</div>
								<div>
									<div className='text-sm font-semibold text-gray-700'>{analyzing ? '图片分析中...' : '拖拽或点击上传错题图片'}</div>
									<div className='mt-1 text-xs leading-5 text-gray-500'>支持 JPG、PNG、WebP 格式，可一次选择多张</div>
								</div>
							</label>
						</div>
					</div>
				</section>

				{uploadedImages.length > 0 && (
					<div className='grid grid-cols-4 gap-3 rounded-xl border border-white/40 bg-white/20 p-3 backdrop-blur-sm sm:grid-cols-6'>
						{uploadedImages.map((url, idx) => (
							<div key={url} className='relative aspect-square rounded-lg overflow-hidden border border-gray-200 bg-gray-50 group shadow-sm'>
								<img src={resolveImageUrl(url)} alt={`uploaded-${idx}`} className='h-full w-full object-cover' />
								<button
									type='button'
									onClick={() => handleRemoveImage(url)}
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

				<input
					value={form.title}
					onChange={e => {
						update('title', e.target.value)
						if (!form.slug && mode === 'create') {
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

				<textarea value={form.question} onChange={e => update('question', e.target.value)} placeholder='题目内容...' rows={4} className='w-full rounded-xl border border-white/40 bg-white/60 px-4 py-3 text-sm backdrop-blur-sm outline-none focus:border-[var(--color-brand)]' />
				<textarea value={form.my_answer} onChange={e => update('my_answer', e.target.value)} placeholder='我的错误答案...' rows={3} className='w-full rounded-xl border border-red-200/50 bg-red-50/30 px-4 py-3 text-sm outline-none focus:border-red-400' />
				<textarea value={form.correct_answer} onChange={e => update('correct_answer', e.target.value)} placeholder='正确答案...' rows={3} className='w-full rounded-xl border border-green-200/50 bg-green-50/30 px-4 py-3 text-sm outline-none focus:border-green-400' />
				<textarea value={form.analysis} onChange={e => update('analysis', e.target.value)} placeholder='分析与反思...' rows={3} className='w-full rounded-xl border border-blue-200/50 bg-blue-50/30 px-4 py-3 text-sm outline-none focus:border-blue-400' />
				<input value={form.knowledge_points} onChange={e => update('knowledge_points', e.target.value)} placeholder='知识点总结' className='w-full rounded-xl border border-purple-200/50 bg-purple-50/30 px-4 py-3 text-sm outline-none focus:border-purple-400' />

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
								<button type='button' onClick={() => update('tags', form.tags.filter((x: string) => x !== t))} aria-label={`删除标签 ${t}`} title={`删除标签 ${t}`} className='text-gray-400 hover:text-red-500'>×</button>
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
						{saving ? '保存中...' : (mode === 'edit' ? '保存' : '发布')}
					</button>
					<Link href='/mistakes' className='rounded-xl bg-white/60 px-6 py-2.5 text-sm hover:bg-white/80'>取消</Link>
				</div>
			</div>

			<TagSuggestionDialog
				open={showTagSuggestion}
				content={[form.question, form.analysis, form.knowledge_points].filter(Boolean).join('\n')}
				title={form.title}
				existingTags={form.tags}
				onApply={(tags) => {
					setShowTagSuggestion(false)
					const merged = [...new Set([...form.tags, ...tags])]
					update('tags', merged)
					pendingSave?.(merged)
				}}
				onSkip={() => {
					setShowTagSuggestion(false)
					pendingSave?.(form.tags)
				}}
				onDontRemind={() => {
					localStorage.setItem('skipEmptyTagReminder', 'true')
					setShowTagSuggestion(false)
					pendingSave?.(form.tags)
				}}
			/>
		</div>
	)
}
