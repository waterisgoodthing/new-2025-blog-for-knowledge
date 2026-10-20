'use client'

import { useCallback, useEffect, useRef, useState, type ReactNode } from 'react'
import { createPortal } from 'react-dom'

export interface Uiv2TooltipProps {
	children: ReactNode
	content: string
	/** Hover-intent delay in ms. */
	delay?: number
}

/**
 * Delayed hover tooltip (VSC overlay migration).
 *
 * Behavioural and visual parity with the legacy `DelayedTooltip`: a fixed,
 * centred dark pill below the trigger, rendered after a hover-intent delay.
 * Unlike the legacy component it also exposes `role="tooltip"`.
 */
export function Uiv2Tooltip({ children, content, delay = 600 }: Uiv2TooltipProps) {
	const [show, setShow] = useState(false)
	const [position, setPosition] = useState({ x: 0, y: 0 })
	const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null)
	const wrapperRef = useRef<HTMLDivElement>(null)

	const clearTimer = useCallback(() => {
		if (timerRef.current) {
			clearTimeout(timerRef.current)
			timerRef.current = null
		}
	}, [])

	const handleMouseEnter = useCallback(() => {
		clearTimer()
		timerRef.current = setTimeout(() => {
			if (wrapperRef.current) {
				const rect = wrapperRef.current.getBoundingClientRect()
				setPosition({ x: rect.left + rect.width / 2, y: rect.bottom + 4 })
			}
			setShow(true)
		}, delay)
	}, [delay, clearTimer])

	const handleMouseLeave = useCallback(() => {
		clearTimer()
		setShow(false)
	}, [clearTimer])

	useEffect(() => clearTimer, [clearTimer])

	return (
		<div
			ref={wrapperRef}
			onMouseEnter={handleMouseEnter}
			onMouseLeave={handleMouseLeave}
			className='inline-flex'
			style={{ pointerEvents: 'auto' }}>
			{children}
			{show &&
				createPortal(
					<div
						role='tooltip'
						data-testid='uiv2-tooltip'
						style={{
							position: 'fixed',
							top: position.y,
							left: position.x,
							transform: 'translateX(-50%)',
							zIndex: 200,
							pointerEvents: 'none'
						}}
						className='whitespace-nowrap rounded-lg bg-gray-800 px-2.5 py-1.5 text-[11px] text-white shadow-lg'>
						{content}
					</div>,
					document.body
				)}
		</div>
	)
}
