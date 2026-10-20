export interface Uiv2ErrorStateProps {
	message: string
	onRetry?: () => void
}

/** Minimal V2 error state (color + text, retry optional). */
export function Uiv2ErrorState({ message, onRetry }: Uiv2ErrorStateProps) {
	return (
		<div role="alert" className="uiv2-error">
			<p>{message}</p>
			{onRetry ? (
				<button type="button" onClick={onRetry} className="uiv2-btn uiv2-btn-ghost">
					重试
				</button>
			) : null}
		</div>
	)
}
