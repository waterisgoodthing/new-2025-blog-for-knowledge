// UI-facing contract: mastery score (F4 skeleton).
// No mastery algorithm lives here. Unknown data => value: null and the UI
// must render "暂无足够数据" / "数据积累中". Fabricating precision is forbidden.

export type MasteryConfidence = 'low' | 'medium' | 'high'
export type MasterySource = 'backend' | 'mock' | 'estimated'

export interface MasteryScore {
	value: number | null
	confidence: MasteryConfidence
	source: MasterySource
}
