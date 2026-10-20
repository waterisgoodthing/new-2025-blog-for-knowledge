import Link from 'next/link'
import type { CSSProperties, MouseEventHandler, ReactNode } from 'react'

export interface Uiv2ButtonProps {
	children: ReactNode
	variant?: 'primary' | 'ghost'
	disabled?: boolean
	onClick?: MouseEventHandler<HTMLElement>
	ariaLabel?: string
	/** Renders a Next.js link with button styling instead of a `<button>`. */
	href?: string
	className?: string
	/** Inline overrides; `.uiv2-*` is unlayered and outranks Tailwind utilities. */
	style?: CSSProperties
}

const BASE_CLASS = 'uiv2-btn focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--uiv2-brand)]'
const VARIANT_CLASS: Record<'primary' | 'ghost', string> = {
	primary: 'uiv2-btn-primary',
	ghost: 'uiv2-btn-ghost'
}

/** Minimal V2 button (presentational only, no business logic). */
export function Uiv2Button({ children, variant = 'primary', disabled = false, onClick, href, ariaLabel, className, style }: Uiv2ButtonProps) {
	const classes = [BASE_CLASS, VARIANT_CLASS[variant], className].filter(Boolean).join(' ')

	if (href && !disabled) {
		return (
			<Link href={href} onClick={onClick} aria-label={ariaLabel} data-variant={variant} className={classes} style={style}>
				{children}
			</Link>
		)
	}

	return (
		<button type='button' disabled={disabled} onClick={onClick} aria-label={ariaLabel} data-variant={variant} className={classes} style={style}>
			{children}
		</button>
	)
}
