import type { ReactNode } from 'react'

export interface Uiv2CardProps {
	children: ReactNode
	title?: string
}

/** Minimal V2 card skeleton (presentational only). min-w-0 + break-words guard narrow screens (L2). */
export function Uiv2Card({ children, title }: Uiv2CardProps) {
	return (
		<section className="uiv2-card min-w-0 break-words">
			{title ? <h3 className="uiv2-card-title min-w-0 break-words">{title}</h3> : null}
			{children}
		</section>
	)
}
