export interface Uiv2PageHeaderProps {
	title: string
	subtitle?: string
	/** Small uppercase kicker above the title (admin surfaces). */
	eyebrow?: string
}

/** Minimal V2 page header. */
export function Uiv2PageHeader({ title, subtitle, eyebrow }: Uiv2PageHeaderProps) {
	return (
		<header className='uiv2-page-header'>
			{eyebrow ? (
				<p
					className='uiv2-page-eyebrow'
					style={{
						margin: '0 0 4px',
						fontSize: 12,
						fontWeight: 500,
						letterSpacing: '0.16em',
						textTransform: 'uppercase',
						color: 'var(--brand, #3db8a8)'
					}}>
					{eyebrow}
				</p>
			) : null}
			<h1>{title}</h1>
			{subtitle ? <p>{subtitle}</p> : null}
		</header>
	)
}
