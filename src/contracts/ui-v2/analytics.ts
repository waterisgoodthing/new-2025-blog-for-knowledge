// UI-facing contract: analytics display (U9).
// Presentation only: trend points, completion counts, weakness distribution,
// mastery display. NO Mastery / Weakness / Recommendation algorithms live in
// the UI — every numeric field is nullable and null renders as
// “暂无足够数据 / 数据积累中”.

import type { MasteryScore } from './mastery'
import type { MasterySource } from './mastery'

export interface TrendPoint {
	label: string
	/** Null = no data for this bucket (renders as 缺数据). */
	value: number | null
	source: MasterySource
}

export interface ReviewCompletion {
	completed: number | null
	total: number | null
	source: MasterySource
}

export interface MistakeTrendPoint {
	label: string
	newMistakes: number | null
	resolvedMistakes: number | null
	source: MasterySource
}

export interface WeaknessDistributionItem {
	name: string
	share: number | null
	count: number | null
	source: MasterySource
}

export interface AnalyticsModel {
	learningTrend: TrendPoint[]
	reviewCompletion: ReviewCompletion
	mistakeTrend: MistakeTrendPoint[]
	weaknessDistribution: WeaknessDistributionItem[]
	mastery: MasteryScore
	source: MasterySource
}
