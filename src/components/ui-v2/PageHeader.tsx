export interface Uiv2PageHeaderProps {
	title: string
	subtitle?: string
}

/** Minimal V2 page header. */
export function Uiv2PageHeader({ title, subtitle }: Uiv2PageHeaderProps) {
	return (
		<header className="uiv2-page-header">
			<h1>{title}</h1>
			{subtitle ? <p>{subtitle}</p> : null}
		</header>
	)
}
