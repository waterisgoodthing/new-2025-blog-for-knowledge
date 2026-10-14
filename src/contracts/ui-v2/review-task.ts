// UI-facing contract: review task (F4 skeleton).
// This is a UI Contract, NOT a backend DTO. Never derive backend schema from it.

export type ReviewTaskPriority = 'low' | 'medium' | 'high'
export type ReviewTaskStatus = 'pending' | 'completed' | 'overdue'

export interface ReviewTask {
	id: string
	title: string
	subject: string
	dueAt?: string
	priority: ReviewTaskPriority
	status: ReviewTaskStatus
	/** Where this object came from. Mocks must use 'mock'. */
	source: 'backend' | 'mock' | 'estimated'
}
