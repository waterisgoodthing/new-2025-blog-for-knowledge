import type { ReactNode } from 'react'

export interface Uiv2ButtonProps {
	children: ReactNode
	variant?: 'primary' | 'ghost'
	disabled?: boolean
	onClick?: () => void
}

/** Minimal V2 button skeleton (presentational only, no business logic). */
export function Uiv2Button({ children, variant = 'primary', disabled = false, onClick }: Uiv2ButtonProps) {
		return (
			<button
				type="button"
				disabled={disabled}
				onClick={onClick}
				data-variant={variant}
				className={(variant === 'primary' ? 'uiv2-btn uiv2-btn-primary' : 'uiv2-btn uiv2-btn-ghost') + ' focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--uiv2-brand)]'}
			>
				{children}
			</button>
		)
}
