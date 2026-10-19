'use client'

import { useState, useEffect } from 'react'
import { Uiv2Button, Uiv2Modal } from '@/components/ui-v2'
import { createMusicItem, updateMusicItem, type MusicItem, type MusicItemCreate } from '@/lib/api/music'

interface MusicFormModalProps {
	open: boolean
	onClose: () => void
	onSuccess: () => void
	editingItem?: MusicItem | null
}

function extractTrackId(url: string): number | null {
	const iMatch = url.match(/[?&]i=(\d+)/)
	if (iMatch) return parseInt(iMatch[1], 10)
	const idMatch = url.match(/\/id(\d+)/)
	if (idMatch) return parseInt(idMatch[1], 10)
	return null
}

const FIELD_CLASS = 'w-full rounded-xl border px-4 py-2.5 text-sm outline-none'

export function MusicFormModal({ open, onClose, onSuccess, editingItem }: MusicFormModalProps) {
	const [form, setForm] = useState<MusicItemCreate>({
		title: '',
		artist: '',
		apple_music_url: '',
		artwork: '',
		preview_url: '',
		sort_order: 0,
		is_active: true
	})
	const [saving, setSaving] = useState(false)
	const [error, setError] = useState('')

	useEffect(() => {
		if (editingItem) {
			setForm({
				title: editingItem.title,
				artist: editingItem.artist || '',
				apple_music_url: editingItem.apple_music_url,
				artwork: editingItem.artwork || '',
				preview_url: editingItem.preview_url || '',
				track_id: editingItem.track_id || undefined,
				sort_order: editingItem.sort_order,
				is_active: editingItem.is_active
			})
		} else {
			setForm({
				title: '',
				artist: '',
				apple_music_url: '',
				artwork: '',
				preview_url: '',
				sort_order: 0,
				is_active: true
			})
		}
		setError('')
	}, [editingItem, open])

	const handleUrlChange = (url: string) => {
		setForm(f => {
			const trackId = extractTrackId(url)
			return { ...f, apple_music_url: url, track_id: trackId || undefined }
		})
	}

	const handleSubmit = async () => {
		if (!form.title.trim()) {
			setError('请输入歌曲标题')
			return
		}
		if (!form.apple_music_url.trim()) {
			setError('请输入 Apple Music URL')
			return
		}

		setSaving(true)
		setError('')
		try {
			if (editingItem) {
				await updateMusicItem(editingItem.id, form)
			} else {
				await createMusicItem(form)
			}
			onSuccess()
			onClose()
		} catch (e: any) {
			setError(e.message || '保存失败')
		} finally {
			setSaving(false)
		}
	}

	const fieldStyle = {
		borderColor: 'var(--admin-border, rgba(45, 62, 60, 0.12))',
		background: 'var(--admin-surface-subtle, #fafcfc)',
		color: 'var(--admin-text-primary, #2d3e3c)'
	}

	return (
		<Uiv2Modal
			open={open}
			onClose={onClose}
			title={editingItem ? '编辑音乐' : '添加音乐'}
			size='form'
			// A form with unsaved work must not be discarded by a stray backdrop click.
			closeOnBackdropClick={false}
			footer={
				<>
					<Uiv2Button variant='ghost' onClick={onClose}>
						取消
					</Uiv2Button>
					<Uiv2Button onClick={handleSubmit} disabled={saving}>
						{saving ? '保存中...' : '保存'}
					</Uiv2Button>
				</>
			}>
			<div className='space-y-4'>
				<div>
					<label className='mb-1.5 block text-sm font-medium'>歌曲标题 *</label>
					<input
						value={form.title}
						onChange={e => setForm(f => ({ ...f, title: e.target.value }))}
						placeholder='Close To You'
						className={FIELD_CLASS}
						style={fieldStyle}
					/>
				</div>

				<div>
					<label className='mb-1.5 block text-sm font-medium'>Apple Music URL *</label>
					<input
						value={form.apple_music_url}
						onChange={e => handleUrlChange(e.target.value)}
						placeholder='https://music.apple.com/cn/album/...'
						className={FIELD_CLASS}
						style={fieldStyle}
					/>
					{form.track_id ? (
						<p className='mt-1 text-xs' style={{ color: 'var(--admin-text-tertiary, #9eadab)' }}>
							已解析 track ID: {form.track_id}
						</p>
					) : null}
				</div>

				<div>
					<label className='mb-1.5 block text-sm font-medium'>艺术家</label>
					<input
						value={form.artist || ''}
						onChange={e => setForm(f => ({ ...f, artist: e.target.value }))}
						placeholder='Carpenters'
						className={FIELD_CLASS}
						style={fieldStyle}
					/>
				</div>

				<div>
					<label className='mb-1.5 block text-sm font-medium'>封面 URL</label>
					<input
						value={form.artwork || ''}
						onChange={e => setForm(f => ({ ...f, artwork: e.target.value }))}
						placeholder='https://...（可留空，自动抓取）'
						className={FIELD_CLASS}
						style={fieldStyle}
					/>
				</div>

				<div>
					<label className='mb-1.5 block text-sm font-medium'>预览音频 URL</label>
					<input
						value={form.preview_url || ''}
						onChange={e => setForm(f => ({ ...f, preview_url: e.target.value }))}
						placeholder='https://...（可留空，自动抓取）'
						className={FIELD_CLASS}
						style={fieldStyle}
					/>
				</div>

				<div className='flex gap-4'>
					<div className='flex-1'>
						<label className='mb-1.5 block text-sm font-medium'>排序</label>
						<input
							type='number'
							value={form.sort_order ?? 0}
							onChange={e => setForm(f => ({ ...f, sort_order: parseInt(e.target.value) || 0 }))}
							className={FIELD_CLASS}
							style={fieldStyle}
						/>
					</div>
					<div className='flex items-end gap-2 pb-0.5'>
						<input
							type='checkbox'
							id='music-active'
							checked={form.is_active !== false}
							onChange={e => setForm(f => ({ ...f, is_active: e.target.checked }))}
							className='h-4 w-4 rounded'
							style={{ accentColor: 'var(--brand, #3db8a8)' }}
						/>
						<label htmlFor='music-active' className='text-sm font-medium'>
							启用
						</label>
					</div>
				</div>

				{error ? (
					<p className='text-sm' style={{ color: '#c0392b' }} role='alert'>
						{error}
					</p>
				) : null}
			</div>
		</Uiv2Modal>
	)
}
