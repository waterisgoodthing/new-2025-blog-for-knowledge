// UI-facing contract: study task (U3).
// The "today" unified task list has NO backend endpoint (GAP-001). This type
// describes display intent only — it invents no scheduling semantics.
// Real integration stays BLOCKED; adapters must mark provenance honestly.

import type { MasterySource } from './mastery'

export type StudyTaskKind = 'review' | 'mistake_retry' | 'new_practice' | 'note_review'

export type StudyTaskStatus = 'pending' | 'in_progress' | 'completed' | 'overdue'

export type StudyTaskPriority = 'low' | 'medium' | 'high'

export interface StudyTask {
	id: string
	title: string
	kind: StudyTaskKind
	status: StudyTaskStatus
	priority: StudyTaskPriority
	subject: string
	dueAt?: string
	/** Deep link to the existing route that owns the work. */
	href: string
	/** Where this task came from. 'backend' only when a unified endpoint exists. */
	source: MasterySource
	/** Human-readable provenance note shown in the UI when not backend. */
	provenanceNote?: string
}
