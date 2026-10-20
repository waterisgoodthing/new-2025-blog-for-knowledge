export interface Uiv2SkeletonProps {
	lines?: number
}

/** Minimal V2 skeleton (loading placeholder, reduced-motion safe). */
export function Uiv2Skeleton({ lines = 3 }: Uiv2SkeletonProps) {
	return (
		<div aria-hidden="true" className="uiv2-skeleton">
			{Array.from({ length: lines }, (_, i) => (
				<div key={i} className="uiv2-skeleton-line" />
			))}
		</div>
	)
}
