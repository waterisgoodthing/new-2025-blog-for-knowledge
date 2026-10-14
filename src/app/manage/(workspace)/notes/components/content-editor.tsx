'use client'

import { useEffect, useLayoutEffect, useRef, useState } from 'react'
import { createPortal } from 'react-dom'
import { createNote, updateNote, type NoteDetail, type NoteUpdateInput } from '@/lib/api/notes'
import { ApiError } from '@/lib/api/client'
import { listCategories, type Category } from '@/lib/api/meta'
import { Select } from '@/components/select'
import { TagInput } from '@/components/tag-input'
import { useNoteEditor } from '@/hooks/use-note-editor'

export type EditorInitial = Pick<NoteDetail, 'slug' | 'title' | 'content' | 'summary' | 'tags' | 'category' | 'hidden' | 'status' | 'revision'>
export type ContentEditorProps = {
	mode: 'create' | 'edit'
	type: 'note' | 'blog'
	initial?: EditorInitial
}

type SaveState = 'editing' | 'saving' | 'saved' | 'failed'

function slugify(title: string) {
	const slug = title
		.trim()
		.toLowerCase()
		.replace(/\s+/g, '-')
		.replace(/[^\p{L}\p{N}\u4e00-\u9fff-]/gu, '')
		.replace(/-+/g, '-')
		.replace(/^-|-$/g, '')
	return slug || `note-${new Date().toISOString().slice(0, 10)}-${Math.random().toString(36).slice(2, 6)}`
}

export function ContentEditor({ mode, type, initial }: ContentEditorProps) {
	const textareaRef = useRef<HTMLTextAreaElement>(null)
	const attributesButtonRef = useRef<HTMLButtonElement>(null)
	const attributesPanelRef = useRef<HTMLElement>(null)
	const previousFocus = useRef<HTMLElement | null>(null)
	const saveInFlight = useRef(false)
	const queuedSave = useRef(false)
	const intendedStatus = useRef<'draft' | 'published'>(initial?.status || 'draft')
	const hasCanonicalIdentity = useRef(mode === 'edit')
	const slugRef = useRef(initial?.slug || '')
	const revisionRef = useRef(initial?.revision)
	const [title, setTitle] = useState(initial?.title || '')
	const [content, setContent] = useState(initial?.content || '')
	const [summary, setSummary] = useState(initial?.summary || '')
	const [tags, setTags] = useState(initial?.tags?.map(tag => (typeof tag === 'string' ? tag : tag.name)) || [])
	const [category, setCategory] = useState(initial?.category || '')
	const [hidden, setHidden] = useState(initial?.hidden || false)
	const [status, setStatus] = useState<'draft' | 'published'>(initial?.status || 'draft')
	const [saveState, setSaveState] = useState<SaveState>('editing')
	const [error, setError] = useState('')
	const [categories, setCategories] = useState<Category[]>([])
	const [attributesOpen, setAttributesOpen] = useState(false)
	const [attributesInDrawer, setAttributesInDrawer] = useState(false)
	const [publishOpen, setPublishOpen] = useState(false)
	const draftRef = useRef({
		title: initial?.title || '',
		content: initial?.content || '',
		summary: initial?.summary || '',
		tags: initial?.tags?.map(tag => (typeof tag === 'string' ? tag : tag.name)) || [],
		category: initial?.category || '',
		hidden: initial?.hidden || false
	})

	useEffect(() => {
		if (type === 'blog')
			listCategories()
				.then(setCategories)
				.catch(() => setCategories([]))
	}, [type])

	useEffect(() => {
		if (typeof window.matchMedia !== 'function') return
		const media = window.matchMedia('(max-width: 639px)')
		const update = () => setAttributesInDrawer(media.matches)
		update()
		media.addEventListener('change', update)
		return () => media.removeEventListener('change', update)
	}, [])

	useEffect(() => {
		if (!attributesOpen) return
		const onPointerDown = (event: PointerEvent) => {
			const target = event.target as Node
			if (attributesPanelRef.current?.contains(target) || attributesButtonRef.current?.contains(target)) return
			setAttributesOpen(false)
		}
		document.addEventListener('pointerdown', onPointerDown, true)
		return () => document.removeEventListener('pointerdown', onPointerDown, true)
	}, [attributesOpen])

	useEffect(() => {
		if (!attributesOpen || !attributesInDrawer) return
		attributesPanelRef.current?.querySelector<HTMLElement>('input, textarea, button, [tabindex]')?.focus()
	}, [attributesInDrawer, attributesOpen])

	useEffect(() => {
		if (!publishOpen) return
		const dialog = document.querySelector<HTMLElement>('[data-publish-dialog]')
		const focusable = dialog?.querySelector<HTMLElement>('button')
		focusable?.focus()
		const onKeyDown = (event: KeyboardEvent) => {
			if (event.key === 'Escape') setPublishOpen(false)
			if (event.key !== 'Tab' || !dialog) return
			const items = Array.from(dialog.querySelectorAll<HTMLElement>('button'))
			if (!items.length) return
			const index = items.indexOf(document.activeElement as HTMLElement)
			const next = items[(index + (event.shiftKey ? -1 : 1) + items.length) % items.length]
			event.preventDefault()
			next.focus()
		}
		document.addEventListener('keydown', onKeyDown)
		return () => document.removeEventListener('keydown', onKeyDown)
	}, [publishOpen])

	useLayoutEffect(() => {
		if (!publishOpen) previousFocus.current?.focus()
	}, [publishOpen])

	const editor = useNoteEditor({
		textareaRef,
		content,
		onContentChange: value => {
			draftRef.current.content = value
			setContent(value)
			setSaveState('editing')
		}
	})
	const snapshot = () => ({ ...draftRef.current, status: intendedStatus.current })
	const sameSnapshot = (left: ReturnType<typeof snapshot>, right: ReturnType<typeof snapshot>) => JSON.stringify(left) === JSON.stringify(right)

	const save = async (requestedStatus?: 'draft' | 'published') => {
		const targetStatus = requestedStatus ?? intendedStatus.current
		intendedStatus.current = targetStatus
		if (!title.trim() || !content.trim()) {
			setError('标题和正文不能为空')
			return
		}
		if (saveInFlight.current) {
			queuedSave.current = true
			return
		}
		saveInFlight.current = true
		setSaveState('saving')
		setError('')
		const payload = { ...snapshot(), ...draftRef.current, status: targetStatus }
		try {
			let saved: NoteDetail
			if (mode === 'create' && !revisionRef.current) {
				saved = await createNote({
					slug: slugRef.current || slugify(payload.title),
					title: payload.title,
					content: payload.content,
					type,
					status: payload.status,
					hidden: payload.hidden,
					tags: payload.tags,
					summary: type === 'blog' ? payload.summary : undefined,
					category: type === 'blog' ? payload.category : undefined
				})
			} else {
				const data: NoteUpdateInput = {
					expected_revision: revisionRef.current,
					title: payload.title,
					content: payload.content,
					type,
					status: payload.status,
					hidden: payload.hidden,
					tags: payload.tags,
					summary: type === 'blog' ? payload.summary : undefined,
					category: type === 'blog' ? payload.category : undefined
				}
				saved = await updateNote(slugRef.current, data)
			}
			slugRef.current = saved.slug
			revisionRef.current = saved.revision
			setStatus(saved.status)
			if (sameSnapshot(payload, snapshot())) setSaveState('saved')
			else setSaveState('editing')
			setAttributesOpen(false)
			if (!hasCanonicalIdentity.current) {
				window.history.replaceState(window.history.state, '', `/manage/notes/${saved.slug}`)
				hasCanonicalIdentity.current = true
			}
		} catch (reason) {
			setSaveState('failed')
			setError(
				(reason instanceof ApiError && reason.status === 409) || (reason && typeof reason === 'object' && 'status' in reason && reason.status === 409)
					? `保存冲突：${reason instanceof Error ? reason.message : '服务端内容已更新'}`
					: reason instanceof Error
						? reason.message
						: '保存失败'
			)
		} finally {
			saveInFlight.current = false
			if (queuedSave.current) {
				queuedSave.current = false
				void save()
			}
		}
	}

	const openPublish = () => {
		previousFocus.current = document.activeElement as HTMLElement
		setPublishOpen(true)
	}
	const publish = () => {
		setPublishOpen(false)
		intendedStatus.current = 'published'
		setStatus('published')
		void save('published')
	}
	const typeLabel = type === 'blog' ? '博客' : '笔记'
	const attributesPanel = attributesOpen ? (
		<section
			ref={attributesPanelRef}
			aria-label='内容属性'
			className={
				attributesInDrawer
					? 'fixed inset-x-0 bottom-0 z-40 max-h-[70svh] space-y-4 overflow-y-auto border border-slate-200/80 bg-white/95 p-4 shadow-[0_-20px_60px_-35px_rgba(15,23,42,0.55)]'
					: 'max-w-xl space-y-4 border border-slate-200/80 bg-white/55 p-4'
			}>
			<TagInput
				tags={tags}
				onChange={value => {
					draftRef.current.tags = value
					setTags(value)
					setSaveState('editing')
				}}
			/>
			{type === 'blog' ? (
				<>
					<textarea
						value={summary}
						onChange={event => {
							draftRef.current.summary = event.target.value
							setSummary(event.target.value)
							setSaveState('editing')
						}}
						placeholder='摘要'
						className='min-h-20 w-full border border-slate-200 bg-white/60 p-2 text-sm outline-none'
					/>
					<Select
						value={category}
						onChange={value => {
							draftRef.current.category = value
							setCategory(value)
							setSaveState('editing')
						}}
						options={[{ value: '', label: '未分类' }, ...categories.map(item => ({ value: item.name, label: item.name }))]}
						className='w-full'
					/>
				</>
			) : null}
			<label className='flex items-center gap-2 text-sm text-slate-600'>
				<input
					type='checkbox'
					checked={hidden}
					onChange={event => {
						draftRef.current.hidden = event.target.checked
						setHidden(event.target.checked)
						setSaveState('editing')
					}}
				/>
				仅自己可见
			</label>
		</section>
	) : null

	return (
		<div className='space-y-5' data-content-editor>
			<div data-testid='editor-background' aria-hidden={publishOpen || undefined} inert={publishOpen || undefined}>
				<div className='flex flex-wrap items-end justify-between gap-3'>
					<div className='min-w-0 flex-1'>
						<label className='sr-only' htmlFor='content-title'>
							标题
						</label>
						<input
							id='content-title'
							value={title}
							onChange={event => {
								draftRef.current.title = event.target.value
								setTitle(event.target.value)
								setSaveState('editing')
							}}
							placeholder={`${typeLabel}标题`}
							className='w-full border-b border-slate-200 bg-transparent px-0 py-2 text-2xl font-semibold outline-none focus:border-[var(--color-brand)]'
						/>
					</div>
					<div
						className={`border border-slate-200/80 bg-white/55 px-3 py-2 text-xs text-slate-500 ${saveState === 'saving' ? 'animate-pulse motion-reduce:animate-none' : ''}`}
						aria-live='polite'>
						{saveState === 'editing' ? (
							'编辑中'
						) : saveState === 'saving' ? (
							'保存中...'
						) : saveState === 'saved' ? (
							'已保存'
						) : (
							<button type='button' onClick={() => void save()} className='text-red-700 underline'>
								保存失败，重试
							</button>
						)}
					</div>
				</div>
				<textarea
					ref={textareaRef}
					value={content}
					onChange={editor.handleChange}
					onKeyDown={event => {
						if ((event.ctrlKey || event.metaKey) && event.key === 's') {
							event.preventDefault()
							void save()
						}
						editor.handleKeyDown(event)
					}}
					onPaste={editor.handlePaste}
					placeholder='从这里开始写作...'
					className='min-h-[52svh] w-full resize-y border border-slate-200/80 bg-white/40 p-4 font-mono text-sm leading-7 outline-none focus:border-[var(--color-brand)] sm:min-h-[60svh]'
				/>
				{error ? (
					<p role='alert' className='flex items-center justify-between gap-3 border-l-2 border-red-400 bg-red-50/70 px-3 py-2 text-sm text-red-700'>
						<span>{error}</span>
						{saveState !== 'failed' ? (
							<button type='button' onClick={() => void save()} className='shrink-0 underline'>
								保存失败，重试
							</button>
						) : null}
					</p>
				) : null}
				<div className='flex flex-wrap items-center justify-between gap-3'>
					<button
						ref={attributesButtonRef}
						type='button'
						onClick={() => setAttributesOpen(value => !value)}
						className='border border-slate-200/80 bg-white/55 px-3 py-2 text-left text-sm text-slate-600'>
						属性 · {tags.length} 个标签 · {hidden ? '隐藏' : '可见'}
						{type === 'blog' && category ? ` · ${category}` : ''}
					</button>
					<div className='flex flex-wrap gap-2'>
						<button type='button' onClick={() => void save()} disabled={saveState === 'saving'} className='brand-btn disabled:opacity-50'>
							保存草稿
						</button>
						<button
							type='button'
							onClick={openPublish}
							disabled={!title.trim() || !content.trim()}
							className='rounded-lg border border-[var(--color-brand)] px-4 py-2 text-sm text-[var(--color-brand)] disabled:opacity-40'>
							发布
						</button>
					</div>
				</div>
				{attributesInDrawer ? null : attributesPanel}
			</div>
			{attributesInDrawer && attributesPanel ? createPortal(attributesPanel, document.body) : null}
			{publishOpen ? (
				<div className='fixed inset-0 z-50 flex items-center justify-center bg-slate-950/35 p-4' role='presentation'>
					<div
						data-publish-dialog
						role='dialog'
						aria-modal='true'
						aria-labelledby='publish-title'
						className='w-full max-w-sm border border-white/60 bg-white p-5 shadow-xl'>
						<h2 id='publish-title' className='text-lg font-semibold text-slate-900'>
							确认发布？
						</h2>
						<p className='mt-2 text-sm text-slate-500'>发布后内容会按当前可见性设置展示。</p>
						<div className='mt-5 flex justify-end gap-2'>
							<button type='button' onClick={() => setPublishOpen(false)} className='rounded-lg border px-3 py-2 text-sm'>
								取消
							</button>
							<button type='button' onClick={publish} className='brand-btn'>
								确认发布
							</button>
						</div>
					</div>
				</div>
			) : null}
		</div>
	)
}
