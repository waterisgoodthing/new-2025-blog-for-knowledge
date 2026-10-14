// UI-facing contract: mistake card model (U4).
// Adapted from the canonical Mistake DTO (src/lib/api/mistakes.ts, read-only).
// Review/due semantics are NOT invented here: review entry availability is
// derived only from the presence of review_item_id.

import type { MasterySource } from './mastery'

export type MistakeReasonLabel =
	| 'concept'
	| 'calculation'
	| 'reading'
	| 'careless'
	| 'unknown'

export type MistakeDifficulty = 'unspecified' | 'easy' | 'medium' | 'hard'

export type MistakeCardStatus = 'active' | 'archived'

export interface MistakeCardModel {
	id: string
	title: string
	questionText: string
	reasonCategory: MistakeReasonLabel
	difficulty: MistakeDifficulty
	status: MistakeCardStatus
	/** Nullable: adapter cannot resolve subject names without taxonomy data. */
	subjectLabel: string | null
	knowledgePointIds: number[]
	/** Present only when the backend linked a review item. */
	reviewItemId: string | null
	updatedAt: string
	source: MasterySource
}

export interface MistakeFilterModel {
	status: 'all' | MistakeCardStatus
	reason: 'all' | MistakeReasonLabel
	/** Null = no knowledge-point filter. */
	knowledgePointId: number | null
	/** Null/empty = no text query. */
	query: string
}
