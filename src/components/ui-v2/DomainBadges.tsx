import { Uiv2Badge } from './Badge'
import type { MasterySource } from '../../contracts/ui-v2/mastery'

/** Domain badges (U4+): text-first status markers, never color-only. */

const SOURCE_LABEL: Record<MasterySource, string> = {
	backend: '真实数据',
	mock: '示例数据',
	estimated: '估算拼装',
}

/**
 * Data-provenance badge (U14/M1 fix): every section renders this from
 * model.source so mocks/estimates can never look authoritative.
 */
export function Uiv2SourceBadge({ source }: { source: MasterySource }) {
	return (
		<Uiv2Badge
			text={`数据来源：${SOURCE_LABEL[source]}`}
			tone={source === 'backend' ? 'neutral' : 'mistake'}
		/>
	)
}

export function Uiv2DueBadge({ overdue }: { overdue: boolean }) {
	return (
		<Uiv2Badge
			text={overdue ? '已逾期' : '待处理'}
			tone={overdue ? 'mistake' : 'neutral'}
		/>
	)
}

const DIFFICULTY_LABEL: Record<string, string> = {
	unspecified: '难度未标注',
	easy: '简单',
	medium: '中等',
	hard: '困难',
}

export function Uiv2DifficultyBadge({ difficulty }: { difficulty: string }) {
	return (
		<Uiv2Badge
			text={DIFFICULTY_LABEL[difficulty] ?? '难度未标注'}
			tone={difficulty === 'hard' ? 'mistake' : 'neutral'}
		/>
	)
}

export function Uiv2SubjectBadge({ label }: { label: string | null }) {
	return <Uiv2Badge text={label ?? '未关联科目'} tone="note" />
}
