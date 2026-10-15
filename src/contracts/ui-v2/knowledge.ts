// UI-facing contract: knowledge nodes (U7).
// Organized around Subject / KnowledgePoint / Learning State / related counts.
// Counts are nullable: no mastery/accuracy algorithm lives in the UI — missing
// data renders as “暂无足够数据 / 数据积累中”.

import type { MasterySource } from './mastery'

export type KnowledgeNodeKind = 'subject' | 'knowledge_point'

export type LearningState = 'not_started' | 'learning' | 'reviewing' | 'unknown'

export interface KnowledgeNode {
	id: string
	kind: KnowledgeNodeKind
	name: string
	description: string | null
	/** Null when the backend provides no learning signal. */
	learningState: LearningState
	/** Nullable relation counters; null => “数据积累中”. */
	relatedQuestions: number | null
	relatedMistakes: number | null
	relatedNotes: number | null
	children: KnowledgeNode[]
	source: MasterySource
}
