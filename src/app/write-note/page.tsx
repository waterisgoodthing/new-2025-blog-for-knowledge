'use client'

import { useState, useRef, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { motion } from 'motion/react'
import { createNote, uploadImage } from '@/lib/api/notes'
import { listCategories, type Category } from '@/lib/api/meta'
import { listSubjects, type Subject } from '@/lib/api/meta'
import { toast } from 'sonner'
import { cn } from '@/lib/utils'
import { useNoteEditorTab } from './hooks/use-note-editor-tab'
import { useNoteEditor } from './hooks/use-note-editor'
import { NoteToolbar } from './components/note-toolbar'
import { NoteTemplatesDropdown } from './components/note-templates'
import { SlashCommandMenu } from './components/slash-command-menu'
import { AIAssistantPanel } from './components/ai-assistant-panel'
import { NotePreviewContent } from './components/note-preview-content'

export default function WriteNotePage() {
	const router = useRouter()
	const textareaRef = useRef<HTMLTextAreaElement>(null)
	const [saving, setSaving] = useState(false)
	const { tab, setTab } = useNoteEditorTab()
	const [uploadedImages, setUploadedImages] = useState<string[]>([])
	const [uploading, setUploading] = useState(false)

	const handleImageUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
		const files = e.target.files
		if (!files || files.length === 0) return
		await uploadFiles(Array.from(files))
	}

	const handleDragOver = (e: React.DragEvent) => {
		e.preventDefault()
	}

	const handleDrop = async (e: React.DragEvent) => {
		e.preventDefault()
		const files = e.dataTransfer.files
		if (!files || files.length === 0) return
		await uploadFiles(Array.from(files))
	}

	const uploadFiles = async (files: File[]) => {
		setUploading(true)
		try {
			const uploadPromises = files.map(async file => {
				const res = await uploadImage(file)
				return res.url
			})
			const urls = await Promise.all(uploadPromises)
			setUploadedImages(prev => [...prev, ...urls])
			toast.success(`成功上传 ${urls.length} 张图片`)
		} catch (err: any) {
			toast.error('上传失败: ' + err.message)
		} finally {
			setUploading(false)
		}
	}
	const [categories, setCategories] = useState<Category[]>([])
	const [subjects, setSubjects] = useState<Subject[]>([])

	useEffect(() => {
		listCategories().then(setCategories).catch((err) => console.error('Failed to load categories:', err))
		listSubjects().then(setSubjects).catch((err) => console.error('Failed to load subjects:', err))
	}, [])
	const [form, setForm] = useState({
		slug: '',
		title: '',
		content: '',
		type: 'note' as 'note' | 'blog' | 'mistake',
		tags: [] as string[],
		tagInput: '',
		summary: '',
		subject: '',
		difficulty: 'medium' as 'easy' | 'medium' | 'hard',
		question: '',
		my_answer: '',
		correct_answer: '',
		analysis: '',
		knowledge_points: '',
		category: '',
		cover: '',
	})

	const update = (k: string, v: any) => setForm(f => ({ ...f, [k]: v }))

	const addTag = () => {
		const tag = form.tagInput.trim()
		if (tag && !form.tags.includes(tag)) {
			update('tags', [...form.tags, tag])
			update('tagInput', '')
		}
	}

	const removeTag = (t: string) => update('tags', form.tags.filter(x => x !== t))

	const handleContentChange = (content: string) => update('content', content)

	const { handleKeyDown, handleChange, insertText, wrapSelection, slashState, closeSlash, executeSlash } = useNoteEditor({
		textareaRef,
		content: form.content,
		onContentChange: handleContentChange,
	})

	const getPreviewContent = () => {
		if (form.type === 'mistake') {
			return [
				form.question && `## 题目\n\n${form.question}`,
				form.my_answer && `## 我的错误答案\n\n${form.my_answer}`,
				form.correct_answer && `## 正确答案\n\n${form.correct_answer}`,
				form.analysis && `## 分析\n\n${form.analysis}`,
				form.knowledge_points && `## 知识点\n\n${form.knowledge_points}`,
			].filter(Boolean).join('\n\n')
		}
		return form.content
	}

	const handleSave = async () => {
		if (!form.title.trim()) return toast.warning('请输入标题')
		if (!form.content.trim() && form.type !== 'mistake') return toast.warning('请输入内容')

		setSaving(true)
		try {
			const autoSlug = form.title.trim().toLowerCase().replace(/[^\w]+/g, '-').replace(/^-|-$/g, '') || `note-${Date.now()}`
			const slug = form.slug.trim() || autoSlug
			const content = form.type === 'mistake'
				? [
					form.question && `## 题目\n\n${form.question}`,
					form.my_answer && `## 我的错误答案\n\n${form.my_answer}`,
					form.correct_answer && `## 正确答案\n\n${form.correct_answer}`,
					form.analysis && `## 分析\n\n${form.analysis}`,
					form.knowledge_points && `## 知识点\n\n${form.knowledge_points}`,
				].filter(Boolean).join('\n\n')
				: form.content

			await createNote({
				slug,
				title: form.title,
				content,
				type: form.type,
				tags: form.tags,
				summary: form.summary || undefined,
				subject: form.subject || undefined,
				difficulty: form.type === 'mistake' ? form.difficulty : undefined,
				question: form.type === 'mistake' ? form.question : undefined,
				my_answer: form.type === 'mistake' ? form.my_answer : undefined,
				correct_answer: form.type === 'mistake' ? form.correct_answer : undefined,
				analysis: form.type === 'mistake' ? form.analysis : undefined,
				knowledge_points: form.type === 'mistake' ? form.knowledge_points : undefined,
				category: form.category || undefined,
				cover: form.cover || undefined,
				images: form.type === 'mistake' ? uploadedImages : undefined,
			})
			router.push('/notes')
		} catch (e: any) {
			toast.error('保存失败: ' + e.message)
		} finally {
			setSaving(false)
		}
	}

	return (
		<div className='mx-auto max-w-3xl px-4 py-8'>
			<motion.h1 initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} className='mb-6 text-2xl font-bold'>
				写笔记
			</motion.h1>

			<div className='space-y-4'>
				<div className='flex gap-3'>
					{(['note', 'blog', 'mistake'] as const).map(t => (
						<button
							key={t}
							onClick={() => update('type', t)}
							className={cn(
								'rounded-full px-4 py-1.5 text-sm transition-colors',
								form.type === t ? 'bg-[var(--color-brand)] text-white' : 'bg-white/60 hover:bg-white/80'
							)}
						>
							{{ note: '笔记', blog: '博客', mistake: '错题' }[t]}
						</button>
					))}
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

				<input
					value={form.slug}
					onChange={e => update('slug', e.target.value)}
					placeholder='slug (自动生成)'
					className='w-full rounded-xl border border-white/40 bg-white/60 px-4 py-2 text-sm backdrop-blur-sm outline-none focus:border-[var(--color-brand)]'
				/>

				{form.type === 'blog' && (
					<>
						<input
							value={form.summary}
							onChange={e => update('summary', e.target.value)}
							placeholder='摘要'
							className='w-full rounded-xl border border-white/40 bg-white/60 px-4 py-2 text-sm backdrop-blur-sm outline-none focus:border-[var(--color-brand)]'
						/>
					</>
				)}

				{form.type === 'mistake' ? (
					<div className='space-y-3 rounded-xl border border-orange-200/50 bg-orange-50/30 p-4'>
						<div
							onDragOver={handleDragOver}
							onDrop={handleDrop}
							className='rounded-xl border border-dashed border-orange-300 bg-white/40 p-5 text-center hover:bg-white/60 transition-colors'
						>
							<label className='cursor-pointer block w-full h-full'>
								<input type='file' accept='image/*' multiple onChange={handleImageUpload} className='hidden' />
								<div className='mb-1 text-2xl'>📷</div>
								<div className='text-xs text-gray-600 font-medium'>
									{uploading ? '正在上传图片...' : '拖拽或点击上传错题图片证据'}
								</div>
								<div className='mt-1 text-[10px] text-gray-400'>支持 JPG, PNG, WebP</div>
							</label>
						</div>

						{uploadedImages.length > 0 && (
							<div className='grid grid-cols-4 gap-2 rounded-lg border border-orange-200/40 bg-white/20 p-2 sm:grid-cols-6'>
								{uploadedImages.map((url, idx) => (
									<div key={url} className='relative aspect-square rounded-md overflow-hidden border border-gray-200 bg-gray-50 group shadow-sm'>
										<img src={url} alt={`uploaded-${idx}`} className='h-full w-full object-cover' />
										<button
											type='button'
											onClick={() => setUploadedImages(prev => prev.filter(x => x !== url))}
											className='absolute top-0.5 right-0.5 flex items-center justify-center h-4 w-4 rounded-full bg-black/50 text-white text-[10px] hover:bg-red-600 transition-colors shadow'
											title="删除图片"
										>
											×
										</button>
									</div>
								))}
							</div>
						)}

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
								list='subject-options-create'
								placeholder='科目'
								className='flex-1 rounded-lg border border-white/40 bg-white/60 px-3 py-2 text-sm outline-none'
							/>
							<datalist id='subject-options-create'>
								{subjects.map(s => <option key={s.id} value={s.name} />)}
							</datalist>
						</div>
						<textarea
							value={form.question}
							onChange={e => update('question', e.target.value)}
							placeholder='题目内容...'
							rows={4}
							className='w-full rounded-lg border border-white/40 bg-white/60 px-3 py-2 text-sm outline-none focus:border-[var(--color-brand)]'
						/>
						<textarea
							value={form.my_answer}
							onChange={e => update('my_answer', e.target.value)}
							placeholder='我的错误答案...'
							rows={3}
							className='w-full rounded-lg border border-red-200/50 bg-red-50/30 px-3 py-2 text-sm outline-none focus:border-red-400'
						/>
						<textarea
							value={form.correct_answer}
							onChange={e => update('correct_answer', e.target.value)}
							placeholder='正确答案...'
							rows={3}
							className='w-full rounded-lg border border-green-200/50 bg-green-50/30 px-3 py-2 text-sm outline-none focus:border-green-400'
						/>
						<textarea
							value={form.analysis}
							onChange={e => update('analysis', e.target.value)}
							placeholder='分析与反思...'
							rows={3}
							className='w-full rounded-lg border border-blue-200/50 bg-blue-50/30 px-3 py-2 text-sm outline-none focus:border-blue-400'
						/>
						<input
							value={form.knowledge_points}
							onChange={e => update('knowledge_points', e.target.value)}
							placeholder='知识点总结'
							className='w-full rounded-lg border border-purple-200/50 bg-purple-50/30 px-3 py-2 text-sm outline-none focus:border-purple-400'
						/>
					</div>
				) : (
					<>
						<div className='flex gap-1 rounded-lg bg-white/40 p-1'>
							<button
								onClick={() => setTab('edit')}
								className={cn('rounded-md px-4 py-1.5 text-sm transition-colors', tab === 'edit' ? 'bg-white shadow-sm font-medium' : 'text-gray-500 hover:text-gray-700')}
							>
								编辑
							</button>
							<button
								onClick={() => setTab('preview')}
								className={cn('rounded-md px-4 py-1.5 text-sm transition-colors', tab === 'preview' ? 'bg-white shadow-sm font-medium' : 'text-gray-500 hover:text-gray-700')}
							>
								预览
							</button>
						</div>

						{tab === 'edit' ? (
							<>
								<NoteToolbar
									textareaRef={textareaRef}
									insertText={insertText}
									wrapSelection={wrapSelection}
									extraButtons={<NoteTemplatesDropdown onInsert={insertText} />}
								/>
								<div className='flex'>
									<div className='relative min-w-0 flex-1'>
										<textarea
											ref={textareaRef}
											value={form.content}
											onChange={handleChange}
											onKeyDown={handleKeyDown}
											placeholder='Markdown 内容...'
											rows={15}
											className='w-full rounded-xl border border-white/40 bg-white/60 px-4 py-3 font-mono text-sm backdrop-blur-sm outline-none focus:border-[var(--color-brand)]'
										/>
										<SlashCommandMenu slashState={slashState} onClose={closeSlash} onSelect={executeSlash} />
									</div>
									<AIAssistantPanel
										textareaRef={textareaRef}
										content={form.content}
										onInsert={insertText}
										onReplaceSelection={(text) => {
											const ta = textareaRef.current
											if (!ta) return
											const { selectionStart, selectionEnd, value } = ta
											const before = value.substring(0, selectionStart)
											const after = value.substring(selectionEnd)
											handleContentChange(before + text + after)
										}}
										getSelectedText={() => {
											const ta = textareaRef.current
											if (!ta) return ''
											return ta.value.substring(ta.selectionStart, ta.selectionEnd)
										}}
									/>
								</div>
							</>
						) : (
							<NotePreviewContent content={form.content} />
						)}
					</>
				)}

				<div>
					<div className='mb-2 flex gap-2'>
						<input
							value={form.tagInput}
							onChange={e => update('tagInput', e.target.value)}
							onKeyDown={e => e.key === 'Enter' && (e.preventDefault(), addTag())}
							placeholder='添加标签'
							className='flex-1 rounded-lg border border-white/40 bg-white/60 px-3 py-2 text-sm outline-none'
						/>
						<button onClick={addTag} className='rounded-lg bg-white/60 px-3 py-2 text-sm hover:bg-white/80'>
							添加
						</button>
					</div>
					<div className='flex flex-wrap gap-2'>
						{form.tags.map(t => (
							<span key={t} className='flex items-center gap-1 rounded-full bg-gray-200/60 px-3 py-1 text-xs'>
								{t}
								<button onClick={() => removeTag(t)} className='text-gray-400 hover:text-red-500'>×</button>
							</span>
						))}
					</div>
				</div>

				<div>
					<select
						value={form.category}
						onChange={e => update('category', e.target.value)}
						className='w-full rounded-lg border border-white/40 bg-white/60 px-3 py-2 text-sm outline-none'
					>
						<option value=''>无分类</option>
						{categories.map(c => <option key={c.id} value={c.name}>{c.name}</option>)}
					</select>
				</div>

				<div>
					<input
						value={form.cover}
						onChange={e => update('cover', e.target.value)}
						placeholder='封面图 URL（可选）'
						className='w-full rounded-xl border border-white/40 bg-white/60 px-4 py-2 text-sm backdrop-blur-sm outline-none focus:border-[var(--color-brand)]'
					/>
				</div>

				<div className='flex gap-3 pt-4'>
					<button
						onClick={handleSave}
						disabled={saving}
						className='rounded-xl bg-[var(--color-brand)] px-6 py-2.5 text-sm text-white transition-transform hover:scale-105 active:scale-95 disabled:opacity-50'
					>
						{saving ? '保存中...' : '发布'}
					</button>
					<button
						onClick={() => router.back()}
						className='rounded-xl bg-white/60 px-6 py-2.5 text-sm hover:bg-white/80'
					>
						取消
					</button>
				</div>
			</div>
		</div>
	)
}
