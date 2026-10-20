'use client'

import { useState, useRef, useCallback, useEffect, type ReactNode } from 'react'
import { createPortal } from 'react-dom'

type DelayedTooltipProps = {
	children: ReactNode
	content: string
	delay?: number
}

export function DelayedTooltip({ children, content, delay = 600 }: DelayedTooltipProps) {
	const [show, setShow] = useState(false)
	const [pos, setPos] = useState({ x: 0, y: 0 })
	const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null)
	const wrapperRef = useRef<HTMLDivElement>(null)

	const clearTimer = useCallback(() => {
		if (timerRef.current) { clearTimeout(timerRef.current); timerRef.current = null }
	}, [])

	const handleMouseEnter = useCallback(() => {
		clearTimer()
		timerRef.current = setTimeout(() => {
			if (wrapperRef.current) {
				const rect = wrapperRef.current.getBoundingClientRect()
				setPos({ x: rect.left + rect.width / 2, y: rect.bottom + 4 })
			}
			setShow(true)
		}, delay)
	}, [delay, clearTimer])

	const handleMouseLeave = useCallback(() => {
		clearTimer()
		setShow(false)
	}, [clearTimer])

	useEffect(() => {
		return () => clearTimer()
	}, [clearTimer])

	return (
		<div
			ref={wrapperRef}
			onMouseEnter={handleMouseEnter}
			onMouseLeave={handleMouseLeave}
			className='inline-flex'
			style={{ pointerEvents: 'auto' }}
		>
			{children}
			{show &&
				createPortal(
					<div
						style={{
							position: 'fixed',
							top: pos.y,
							left: pos.x,
							transform: 'translateX(-50%)',
							zIndex: 200,
							pointerEvents: 'none',
						}}
						className='whitespace-nowrap rounded-lg bg-gray-800 px-2.5 py-1.5 text-[11px] text-white shadow-lg'
					>
						{content}
					</div>,
					document.body
				)
			}
		</div>
	)
}
