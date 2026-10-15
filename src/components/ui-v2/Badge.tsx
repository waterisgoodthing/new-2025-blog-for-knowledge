export type Uiv2BadgeTone = 'note' | 'blog' | 'mistake' | 'neutral'

export interface Uiv2BadgeProps {
	text: string
	tone?: Uiv2BadgeTone
}

/** Minimal V2 badge skeleton (small-area tone only). */
export function Uiv2Badge({ text, tone = 'neutral' }: Uiv2BadgeProps) {
	return (
		<span data-tone={tone} className="uiv2-badge">
			{text}
		</span>
	)
}
