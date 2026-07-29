'use client'

import { useState, useEffect, useRef, useCallback, type ReactNode } from 'react'
import { createPortal } from 'react-dom'

export type ContextMenuItem = {
	label: string
	icon?: ReactNode
	onClick: () => void
	variant?: 'default' | 'danger'
	disabled?: boolean
}

type ContextMenuProps = {
	open: boolean
	position: { x: number; y: number }
	items: ContextMenuItem[]
	onClose: () => void
}

export function ContextMenu({ open, position, items, onClose }: ContextMenuProps) {
	const [mounted, setMounted] = useState(false)

	useEffect(() => { setMounted(true) }, [])

	useEffect(() => {
		if (!open) return
		const controller = new AbortController()
		const handleClick = (e: Event) => { onClose() }
		const handleKeydown = (e: KeyboardEvent) => { if (e.key === 'Escape') onClose() }
		document.addEventListener('click', handleClick, { signal: controller.signal })
		document.addEventListener('contextmenu', handleClick, { signal: controller.signal })
		document.addEventListener('keydown', handleKeydown, { signal: controller.signal })
		return () => controller.abort()
	}, [open, onClose])

	if (!open || !mounted || items.length === 0) return null

	return createPortal(
		<div
			style={{
				position: 'fixed',
				top: Math.min(position.y, window.innerHeight - 200),
				left: Math.min(position.x, window.innerWidth - 180),
				zIndex: 100,
			}}
			className='min-w-[160px] rounded-xl border border-white/40 bg-white/95 p-1 shadow-lg backdrop-blur-xl'
			role='menu'
		>
			{items.map((item, i) => (
				<button
					key={i}
					type='button'
					onClick={() => { item.onClick(); onClose() }}
					disabled={item.disabled}
					role='menuitem'
					className={`flex w-full items-center gap-2 rounded-lg px-3 py-2 text-left text-xs transition-colors disabled:opacity-40 ${
						item.variant === 'danger'
							? 'text-red-600 hover:bg-red-50/50'
							: 'text-gray-700 hover:bg-gray-100/50'
					}`}
				>
					{item.icon && <span className='shrink-0 text-gray-500'>{item.icon}</span>}
					<span>{item.label}</span>
				</button>
			))}
		</div>,
		document.body
	)
}
