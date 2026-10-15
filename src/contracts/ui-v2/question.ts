// UI-facing contract: question card model (U6).
// Adapted from the canonical Question DTO (src/lib/api/questions.ts, read-only).
// Practice states are DISPLAY-ONLY: 'answering' holds a local selection with no
// correctness judgment; 'result' reveals the stored correct answer/analysis.
// Grading/attempt persistence does not exist in this track (GAP-006).

import type { MasterySource } from './mastery'

export type QuestionTypeLabel =
	| 'single_choice'
	| 'multiple_choice'
	| 'true_false'
	| 'short_answer'
	| 'essay'

export type QuestionPracticeState = 'browse' | 'answering' | 'result'

export interface QuestionOptionModel {
	key: string
	text: string
}

export interface QuestionCardModel {
	id: string
	title: string
	stem: string
	questionType: QuestionTypeLabel
	options: QuestionOptionModel[]
	/** Stored answer revealed only in 'result' state. Null when absent. */
	correctAnswer: string | null
	/** Stored analysis revealed only in 'result' state. Null when absent. */
	analysis: string | null
	difficulty: 'unspecified' | 'easy' | 'medium' | 'hard'
	status: 'active' | 'archived'
	/** Nullable: subject names need taxonomy data the adapter does not fetch. */
	subjectLabel: string | null
	knowledgePointIds: number[]
	updatedAt: string
	source: MasterySource
}
