export interface Uiv2SectionHeaderProps {
	title: string
	description?: string
}

/** Minimal V2 section header. */
export function Uiv2SectionHeader({ title, description }: Uiv2SectionHeaderProps) {
	return (
		<div className="uiv2-section-header">
			<h2>{title}</h2>
			{description ? <p>{description}</p> : null}
		</div>
	)
}
