'use client'

import dynamic from 'next/dynamic'
import { useState, useRef, useEffect } from 'react'
import Link from 'next/link'
import { useRouter, useSearchParams } from 'next/navigation'
import { motion } from 'motion/react'
import { createNote, uploadImage } from '@/lib/api/notes'
import { listCategories, type Category } from '@/lib/api/meta'
import { toast } from 'sonner'
import { cn } from '@/lib/utils'
import { useNoteEditorTab } from './hooks/use-note-editor-tab'
import { useNoteEditor } from './hooks/use-note-editor'
import { NoteToolbar } from './components/note-toolbar'
import { NoteTemplatesDropdown } from './components/note-templates'
import { SlashCommandMenu } from './components/slash-command-menu'
import { AIAssistantPanel } from './components/ai-assistant-panel'
import { TagSuggestionDialog } from '@/components/tag-suggestion-dialog'
import { getContentDetailHref } from '@/lib/content-routes'
import { ArrowLeft } from 'lucide-react'
import { AuthGate } from '@/components/auth-gate'

const NotePreviewContent = dynamic(() => import('./components/note-preview-content').then(m => m.NotePreviewContent), { ssr: false })

export default function WriteNotePage() {
	return (
		<AuthGate>
			<WriteNoteContent />
		</AuthGate>
	)
}

function WriteNoteContent() {
	const router = useRouter()
	const searchParams = useSearchParams()
	const textareaRef = useRef<HTMLTextAreaElement>(null)
	const [saving, setSaving] = useState(false)
	const [showTagSuggestion, setShowTagSuggestion] = useState(false)
	const [pendingSave, setPendingSave] = useState<((tags?: string[]) => Promise<void>) | null>(null)
	const { tab, setTab } = useNoteEditorTab()

	const [categories, setCategories] = useState<Category[]>([])

	useEffect(() => {
		listCategories().then(setCategories).catch((err) => console.error('Failed to load categories:', err))
	}, [])

	const [form, setForm] = useState({
		slug: '',
		title: '',
		content: '',
		type: 'note' as 'note' | 'blog',
		tags: [] as string[],
		tagInput: '',
		summary: '',
		category: '',
		cover: '',
	})

	const update = (k: string, v: any) => setForm(f => ({ ...f, [k]: v }))

	useEffect(() => {
		if (searchParams.get('ai_prefill') === '1') {
			try {
				const stored = sessionStorage.getItem('ai_prefill_note')
				if (stored) {
					const data = JSON.parse(stored)
					setForm(f => ({
						...f,
						title: data.title || f.title,
						content: data.content || f.content,
					}))
					sessionStorage.removeItem('ai_prefill_note')
				}
			} catch {}
		}
	}, [searchParams])

	const addTag = () => {
		const tag = form.tagInput.trim()
		if (tag && !form.tags.includes(tag)) {
			update('tags', [...form.tags, tag])
			update('tagInput', '')
		}
	}

	const removeTag = (t: string) => update('tags', form.tags.filter(x => x !== t))

	const handleContentChange = (content: string) => update('content', content)

	const { handleKeyDown, handleChange, handlePaste, insertText, wrapSelection, slashState, closeSlash, executeSlash } = useNoteEditor({
		textareaRef,
		content: form.content,
		onContentChange: handleContentChange,
		onImageUpload: async (file) => {
			const res = await uploadImage(file, { noteType: form.type, slug: form.slug || undefined })
			return res.url
		},
	})

	const handleSave = async () => {
		if (!form.title.trim()) return toast.warning('请输入标题')
		if (!form.content.trim()) return toast.warning('请输入内容')

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
			const autoSlug = form.title.trim().toLowerCase().replace(/[^\w]+/g, '-').replace(/^-|-$/g, '') || `note-${Date.now()}`
			const slug = form.slug.trim() || autoSlug

			const created = await createNote({
				slug,
				title: form.title,
				content: form.content,
				type: form.type,
				tags,
				summary: form.summary || undefined,
				category: form.category || undefined,
				cover: form.cover || undefined,
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
			<div className='mb-6 flex items-center gap-4'>
				<Link
					href='/notes'
					aria-label='返回笔记'
					className='flex h-9 w-9 items-center justify-center rounded-xl border border-white/40 bg-white/60 text-gray-600 transition-colors hover:bg-white/80 hover:text-gray-800'
				>
					<ArrowLeft size={18} />
				</Link>
				<motion.h1 initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} className='text-2xl font-bold'>
					写笔记
				</motion.h1>
			</div>

			<div className='space-y-4'>
				<div className='flex gap-3'>
					{(['note', 'blog'] as const).map(t => (
						<button
							key={t}
							onClick={() => update('type', t)}
							className={cn(
								'rounded-full px-4 py-1.5 text-sm transition-colors',
								form.type === t ? 'bg-[var(--color-brand)] text-white' : 'bg-white/60 hover:bg-white/80'
							)}
						>
							{{ note: '笔记', blog: '博客' }[t]}
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
					<input
						value={form.summary}
						onChange={e => update('summary', e.target.value)}
						placeholder='摘要'
						className='w-full rounded-xl border border-white/40 bg-white/60 px-4 py-2 text-sm backdrop-blur-sm outline-none focus:border-[var(--color-brand)]'
					/>
				)}

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
							extraButtons={<NoteTemplatesDropdown onInsert={insertText} textareaRef={textareaRef} />}
						/>
						<div className='flex'>
							<div className='relative min-w-0 flex-1'>
								<textarea
									ref={textareaRef}
									value={form.content}
									onChange={handleChange}
									onKeyDown={handleKeyDown}
									onPaste={handlePaste}
									placeholder='Markdown 内容...'
									rows={15}
									className='w-full rounded-xl border border-white/40 bg-white/60 px-4 py-3 font-mono text-sm backdrop-blur-sm outline-none focus:border-[var(--color-brand)]'
								/>
								<SlashCommandMenu slashState={slashState} onClose={closeSlash} onSelect={executeSlash} />
							</div>
							<AIAssistantPanel
								textareaRef={textareaRef}
								content={form.content}
								title={form.title}
								noteType={form.type}
								existingTags={form.tags}
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
								onApplyTitle={(t) => update('title', t)}
								onApplySummary={(s) => update('summary', s)}
								onApplyTags={(tags) => update('tags', [...new Set([...form.tags, ...tags])])}
							onApplyCategory={(c) => update('category', c)}
							/>
						</div>
					</>
				) : (
					<NotePreviewContent content={form.content} />
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
								<button type='button' onClick={() => removeTag(t)} aria-label={`删除标签 ${t}`} title={`删除标签 ${t}`} className='text-gray-400 hover:text-red-500'>×</button>
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
					<Link
						href='/notes'
						className='rounded-xl bg-white/60 px-6 py-2.5 text-sm hover:bg-white/80'
					>
						取消
					</Link>
				</div>
			</div>

			<TagSuggestionDialog
				open={showTagSuggestion}
				content={form.content}
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
