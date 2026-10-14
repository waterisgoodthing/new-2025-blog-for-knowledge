// UI-facing contract: review queue display (U5).
// Week2 owns review semantics (PR-06/07/08 NOT_VERIFIED): rating scales,
// scheduling, lapse/progression, and ReviewRecord shape are NOT defined here.
// This contract covers queue presentation only. Real integration is
// BLOCKED_BY_WEEK2 (DEPENDENCY-001); re-audit the contract after the Week2 Gate.

import type { MasterySource } from './mastery'
import type { ReviewTask } from './review-task'

export interface ReviewQueueItem {
	task: ReviewTask
	/** Display excerpt of the linked question/mistake. Nullable when absent. */
	questionExcerpt: string | null
	/** True only when the backend linked a reviewable entity. */
	hasReviewTarget: boolean
	source: MasterySource
}

export interface ReviewQueueModel {
	items: ReviewQueueItem[]
	/** Nullable: no completion ratio is computed by the UI. */
	completedToday: number | null
	source: MasterySource
}
