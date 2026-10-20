'use client'

import { useCallback, useMemo, useState, type DragEvent } from 'react'
import dayjs from 'dayjs'
import type { BlogIndexItem } from '@/hooks/use-blog-index'
import { Uiv2Button, Uiv2Modal } from '@/components/ui-v2'
import { Select } from '@/components/select'
import { X } from 'lucide-react'

interface CategoryModalProps {
	open: boolean
	onClose: () => void
	categoryList: string[]
	newCategory: string
	onNewCategoryChange: (value: string) => void
	onAddCategory: () => void
	onRemoveCategory: (category: string) => void
	onReorderCategories: (nextList: string[]) => void
	editableItems: BlogIndexItem[]
	onAssignCategory: (slug: string, category?: string) => void
}

export function CategoryModal({
	open,
	onClose,
	categoryList,
	newCategory,
	onNewCategoryChange,
	onAddCategory,
	onRemoveCategory,
	onReorderCategories,
	editableItems,
	onAssignCategory
}: CategoryModalProps) {
	const [draggingIndex, setDraggingIndex] = useState<number | null>(null)
	const categoryOptions = useMemo(
		() => [{ value: '', label: '未分类' }, ...categoryList.map(cat => ({ value: cat, label: cat }))],
		[categoryList]
	)

	const handleDragStart = useCallback((index: number) => {
		return () => {
			setDraggingIndex(index)
		}
	}, [])

	const handleDragOver = useCallback((index: number) => {
		return (event: DragEvent<HTMLSpanElement>) => {
			event.preventDefault()
			event.dataTransfer.dropEffect = 'move'
		}
	}, [])

	const handleDrop = useCallback(
		(index: number) => {
			return (event: DragEvent<HTMLSpanElement>) => {
				event.preventDefault()
				if (draggingIndex === null || draggingIndex === index) return

				const next = [...categoryList]
				const [moved] = next.splice(draggingIndex, 1)
				next.splice(index, 0, moved)
				onReorderCategories(next)
				setDraggingIndex(null)
			}
		},
		[categoryList, draggingIndex, onReorderCategories]
	)

	const handleDragEnd = useCallback(() => {
		setDraggingIndex(null)
	}, [])

	// Rows sit on the base elevated surface; the chip/panel containers use the
	// plain surface so elevation order stays consistent in dark mode.
	const panelStyle = { background: 'var(--editorial-surface, #fffef8)' }
	const chipStyle = {
		borderColor: 'var(--editorial-border, rgba(74, 56, 50, 0.12))',
		background: 'color-mix(in srgb, var(--editorial-accent, #b85e4c) 10%, transparent)',
		color: 'var(--editorial-text-primary, #4a3832)'
	}

	return (
		<Uiv2Modal open={open} onClose={onClose} title='文章分类' size='preview' footer={<Uiv2Button onClick={onClose}>完成</Uiv2Button>}>
			<div className='space-y-4'>
				<div className='flex flex-col gap-3 sm:flex-row sm:items-center'>
					<input
						value={newCategory}
						onChange={e => onNewCategoryChange(e.target.value)}
						placeholder='输入分类名称'
						aria-label='新分类名称'
						className='w-full rounded-lg border px-3 py-2 text-sm outline-none'
						style={{
							borderColor: 'var(--editorial-border, rgba(74, 56, 50, 0.12))',
							background: 'var(--editorial-surface, #fffef8)',
							color: 'var(--editorial-text-primary, #4a3832)'
						}}
					/>
					<Uiv2Button onClick={onAddCategory} style={{ whiteSpace: 'nowrap' }}>
						新增分类
					</Uiv2Button>
				</div>

				<div className='flex flex-wrap gap-2 rounded-lg p-3 text-sm' style={panelStyle}>
					{categoryList.length === 0 ? (
						<span style={{ color: 'var(--editorial-text-secondary, #8b7667)' }}>暂无分类</span>
					) : (
						categoryList.map((cat, index) => (
							<span
								key={cat}
								draggable
								onDragStart={handleDragStart(index)}
								onDragOver={handleDragOver(index)}
								onDrop={handleDrop(index)}
								onDragEnd={handleDragEnd}
								className={`flex cursor-move items-center gap-2 rounded-full border py-1 pr-1.5 pl-3 ${
									draggingIndex === index ? 'opacity-60 ring-1' : ''
								}`}
								data-dragging={draggingIndex === index ? 'true' : undefined}
								style={chipStyle}>
								<span className='select-none'>{cat}</span>
								<button
									type='button'
									onClick={() => onRemoveCategory(cat)}
									className='inline-flex h-4 w-4 items-center justify-center'
									aria-label={`移除分类 ${cat}`}
									style={{ color: 'var(--editorial-text-secondary, #8b7667)' }}>
									<X className='h-3 w-3' aria-hidden='true' />
								</button>
							</span>
						))
					)}
				</div>

				<div className='max-h-[360px] space-y-2 overflow-y-auto rounded-xl p-3' style={panelStyle}>
					{editableItems.map(item => (
						<div
							key={item.slug}
							className='flex flex-col gap-2 rounded-lg border px-3 py-2 sm:flex-row sm:items-center sm:justify-between'
							style={{
								borderColor: 'var(--editorial-border, rgba(74, 56, 50, 0.12))',
								background: 'var(--editorial-surface-elevated, #ffffff)',
								boxShadow: draggingIndex === null ? undefined : undefined
							}}>
							<div className='min-w-0 text-sm font-medium'>
								<span className='block truncate'>{item.title || item.slug}</span>
								<span className='ml-2 text-xs' style={{ color: 'var(--editorial-text-tertiary, #b8a393)' }}>
									{dayjs(item.date).format('YYYY-MM-DD')}
								</span>
							</div>
							<Select
								value={item.category || ''}
								onChange={value => onAssignCategory(item.slug, value)}
								options={categoryOptions}
								className='w-full text-sm sm:w-[180px]'
							/>
						</div>
					))}
					{editableItems.length === 0 && (
						<div className='text-sm' style={{ color: 'var(--editorial-text-secondary, #8b7667)' }}>
							暂无文章
						</div>
					)}
				</div>
			</div>
		</Uiv2Modal>
	)
}
