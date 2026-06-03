'use client'

import { useState, useCallback, type ReactNode } from 'react'
import {
	DndContext,
	DragOverlay,
	closestCenter,
	KeyboardSensor,
	PointerSensor,
	useSensor,
	useSensors,
	type DragStartEvent,
	type DragEndEvent,
	type DragOverEvent,
} from '@dnd-kit/core'
import {
	SortableContext,
	sortableKeyboardCoordinates,
	verticalListSortingStrategy,
} from '@dnd-kit/sortable'

type DragDropProviderProps = {
	children: ReactNode
	onDragEnd?: (activeId: string, overId: string | null) => void
	onDragOver?: (activeId: string, overId: string | null) => void
}

export function DragDropProvider({ children, onDragEnd, onDragOver }: DragDropProviderProps) {
	const sensors = useSensors(
		useSensor(PointerSensor, { activationConstraint: { distance: 8 } }),
		useSensor(KeyboardSensor, { coordinateGetter: sortableKeyboardCoordinates })
	)

	const handleDragEnd = useCallback((event: DragEndEvent) => {
		const { active, over } = event
		onDragEnd?.(String(active.id), over ? String(over.id) : null)
	}, [onDragEnd])

	const handleDragOver = useCallback((event: DragOverEvent) => {
		const { active, over } = event
		onDragOver?.(String(active.id), over ? String(over.id) : null)
	}, [onDragOver])

	return (
		<DndContext
			sensors={sensors}
			collisionDetection={closestCenter}
			onDragEnd={handleDragEnd}
			onDragOver={handleDragOver}
		>
			{children}
		</DndContext>
	)
}

export { useSortable } from '@dnd-kit/sortable'
export { CSS } from '@dnd-kit/utilities'
