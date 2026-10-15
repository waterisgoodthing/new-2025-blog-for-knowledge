export interface Uiv2ProgressProps {
	value: number | null
}

/** Minimal V2 progress. Null => 暂无足够数据 (never fabricate). */
export function Uiv2Progress({ value }: Uiv2ProgressProps) {
	if (value === null) {
		return <p className="uiv2-muted">暂无足够数据</p>
	}
	return (
		<div className="uiv2-progress" role="progressbar" aria-label="掌握度进度" aria-valuenow={value} aria-valuemin={0} aria-valuemax={100}>
			<div className="uiv2-progress-bar" style={{ width: `${Math.min(100, Math.max(0, value))}%` }} />
		</div>
	)
}
