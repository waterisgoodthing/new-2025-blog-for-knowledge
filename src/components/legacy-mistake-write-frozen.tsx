export const LEGACY_MISTAKE_WRITE_FROZEN_MESSAGE =
	'legacy 错题写入已冻结，请使用 canonical 错题流程'

export function LegacyMistakeWriteFrozenNotice() {
	return (
		<div
			role='status'
			data-testid='legacy-mistake-write-frozen'
			className='mb-4 rounded-xl border border-amber-300/70 bg-amber-50/90 px-4 py-3 text-sm leading-6 text-amber-900'
		>
			{LEGACY_MISTAKE_WRITE_FROZEN_MESSAGE}
		</div>
	)
}
