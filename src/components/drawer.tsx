'use client'

import { useEffect, useState, type ReactNode } from 'react'
import { createPortal } from 'react-dom'
import { AnimatePresence, motion } from 'motion/react'
import { X } from 'lucide-react'
import { cn } from '@/lib/utils'

interface DrawerProps {
	open: boolean
	onClose: () => void
	title?: string
	children: ReactNode
	side?: 'right' | 'bottom'
	width?: string
}

export function Drawer({ open, onClose, title, children, side = 'right', width = '480px' }: DrawerProps) {
	const [mounted, setMounted] = useState(false)

	useEffect(() => { setMounted(true) }, [])

	useEffect(() => {
		if (!open) return
		const previous = document.body.style.overflow
		document.body.style.overflow = 'hidden'
		return () => { document.body.style.overflow = previous }
	}, [open])

	useEffect(() => {
		if (!open) return
		const handler = (e: KeyboardEvent) => { if (e.key === 'Escape') onClose() }
		window.addEventListener('keydown', handler)
		return () => window.removeEventListener('keydown', handler)
	}, [open, onClose])

	if (!mounted) return null

	const isRight = side === 'right'

	return createPortal(
		<AnimatePresence>
			{open && (
				<>
					<motion.div
						initial={{ opacity: 0 }}
						animate={{ opacity: 1 }}
						exit={{ opacity: 0 }}
						className='fixed inset-0 z-50 bg-black/30 backdrop-blur-sm'
						onClick={onClose}
					/>
					<motion.div
						initial={isRight ? { x: '100%' } : { y: '100%' }}
						animate={isRight ? { x: 0 } : { y: 0 }}
						exit={isRight ? { x: '100%' } : { y: '100%' }}
						transition={{ type: 'spring', damping: 30, stiffness: 300 }}
						className={cn(
							'fixed z-50 bg-white/95 backdrop-blur-xl shadow-xl',
							isRight
							 ? 'top-0 right-0 h-full border-l border-white/40'
							 : 'bottom-0 left-0 w-full max-h-[80vh] border-t border-white/40 rounded-t-2xl'
						)}
						style={isRight ? { maxWidth: width, width: '100%' } : undefined}
					>
						<div className='flex items-center justify-between border-b border-white/20 px-5 py-4'>
							{title && <h2 className='text-base font-semibold text-gray-800'>{title}</h2>}
							<button
								onClick={onClose}
								aria-label='关闭'
								className='rounded-lg p-1.5 text-gray-400 hover:bg-white/60 hover:text-gray-600'
							>
								<X size={18} />
							</button>
						</div>
						<div className={cn('overflow-y-auto', isRight ? 'h-[calc(100%-60px)]' : 'max-h-[calc(80vh-60px)]')}>
							{children}
						</div>
					</motion.div>
				</>
			)}
		</AnimatePresence>,
		document.body
	)
}
