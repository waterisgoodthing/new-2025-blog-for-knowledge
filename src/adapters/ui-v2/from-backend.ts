// Adapter skeleton: Backend DTO (unknown shape) -> UI Contract (F4).
// Pure functions only. Missing fields => null + 'estimated', never fabricated values.
// This file must NOT import backend code; callers pass already-fetched DTOs.

import type { ReviewTask } from '../../contracts/ui-v2/review-task'
import type { MasteryScore } from '../../contracts/ui-v2/mastery'
import type {
	DashboardModel,
	DashboardRecentItem,
} from '../../contracts/ui-v2/dashboard'
import type { KnowledgeNode } from '../../contracts/ui-v2/knowledge'
import type { MistakeCardModel } from '../../contracts/ui-v2/mistake'
import type { NoteArtifact } from '../../contracts/ui-v2/note-artifact'
import type { QuestionCardModel } from '../../contracts/ui-v2/question'
import type { ResourceItem } from '../../contracts/ui-v2/resource'
import { formatBytes } from '../../contracts/ui-v2/resource'
import type { ReviewQueueItem } from '../../contracts/ui-v2/review-queue'
import type { StudyTask } from '../../contracts/ui-v2/study-task'
import type { Attachment } from '../../lib/api/attachments'
import type { DashboardSummary } from '../../lib/api/dashboard'
import type { Mistake } from '../../lib/api/mistakes'
import type { NoteDetail } from '../../lib/api/notes'
import type { Question } from '../../lib/api/questions'
import type { ReviewItem } from '../../lib/api/review-items'
import type { ReviewPlan } from '../../lib/api/review'
import type { KnowledgePointTreeNode, Subject } from '../../lib/api/taxonomy'

interface BackendReviewLike {
	id?: unknown
	title?: unknown
	subject?: unknown
	due_at?: unknown
}

function toText(v: unknown): string | null {
	return typeof v === 'string' && v.length > 0 ? v : null
}

/** Map a backend review-like DTO to a UI ReviewTask. Unknown => estimated. */
export function adaptReviewTask(raw: BackendReviewLike): ReviewTask {
	const id = toText(raw.id)
	const title = toText(raw.title)
	const subject = toText(raw.subject)
	const dueAt = toText(raw.due_at)
	return {
		id: id ?? 'unknown',
		title: title ?? '未知任务',
		subject: subject ?? '未知科目',
		dueAt: dueAt ?? undefined,
		priority: 'medium',
		status: 'pending',
		source: id && title ? 'backend' : 'estimated',
	}
}

/** Map an optional backend mastery value. Missing => null (UI shows 暂无足够数据). */
export function adaptMasteryScore(raw: unknown): MasteryScore {
	if (typeof raw === 'number' && Number.isFinite(raw)) {
		return { value: raw, confidence: 'low', source: 'backend' }
	}
	return { value: null, confidence: 'low', source: 'estimated' }
}

/**
 * Map the admin dashboard summary DTO to the UI dashboard model (U2).
 * Pure function. Sections flagged 'unavailable'/'empty' degrade to null/empty
 * with 'estimated' source — never fabricated numbers. Weakness/trend have no
 * backend source in this DTO, so they are honestly empty (UI shows 数据积累中).
 */
export function adaptDashboardSummary(dto: DashboardSummary): DashboardModel {
	const learningOk = dto.sections.learning === 'ready'
	const activityOk = dto.sections.activity === 'ready'
	const due = Number.isFinite(dto.counts.due_reviews) ? dto.counts.due_reviews : null

	const recent: DashboardRecentItem[] = []
	if (activityOk) {
		for (const q of dto.recent_questions.slice(0, 5)) {
			recent.push({
				id: `q-${q.id}`,
				title: q.title ?? q.question_text,
				kind: 'question',
				updatedAt: q.updated_at,
				source: 'backend',
			})
		}
		for (const m of dto.recent_mistakes.slice(0, 5)) {
			recent.push({
				id: `m-${m.id}`,
				title: m.title ?? m.question_text,
				kind: 'mistake',
				updatedAt: m.updated_at,
				source: 'backend',
			})
		}
	}

	return {
		today: {
			dueCount: learningOk ? due : null,
			overdueCount: null,
			nextTask: null,
			source: learningOk && due !== null ? 'backend' : 'estimated',
		},
		review: {
			pendingCount: null,
			dueTodayCount: learningOk ? due : null,
			source: learningOk && due !== null ? 'backend' : 'estimated',
		},
		weaknesses: [],
		recent,
		trend: [],
		nextAction:
			learningOk && due !== null && due > 0
				? {
						title: '处理到期复习',
						href: '/manage/review',
						reason: `${due} 项待处理`,
						source: 'backend',
					}
				: null,
		source: 'backend',
	}
}

/**
 * Derive a PARTIAL today list from real counts (U3).
 * There is no unified task endpoint (GAP-001), so the result is ALWAYS
 * source 'estimated' with a provenance note — never 'backend'. The UI must
 * show the note. Real integration stays BLOCKED (T-U3-3).
 */
export function adaptTodayTasks(
	dto: DashboardSummary,
	plan?: ReviewPlan | null,
): StudyTask[] {
	const tasks: StudyTask[] = []
	const note = '由仪表盘计数拼装，非统一任务流（GAP-001）'
	const due = dto.counts.due_reviews
	if (dto.sections.learning === 'ready' && due > 0) {
		tasks.push({
			id: 'estimated-today-review',
			title: `复习 ${due} 项到期内容`,
			kind: 'review',
			status: 'pending',
			priority: 'high',
			subject: '全部科目',
			href: '/manage/review',
			source: 'estimated',
			provenanceNote: note,
		})
	}
	if (plan && plan.overdue_count > 0) {
		tasks.push({
			id: 'estimated-today-overdue',
			title: `处理 ${plan.overdue_count} 项逾期复习`,
			kind: 'review',
			status: 'overdue',
			priority: 'high',
			subject: '全部科目',
			href: '/manage/review',
			source: 'estimated',
			provenanceNote: note,
		})
	}
	if (dto.sections.activity === 'ready' && dto.recent_mistakes.length > 0) {
		tasks.push({
			id: 'estimated-today-mistakes',
			title: `复盘最近 ${Math.min(dto.recent_mistakes.length, 5)} 道错题`,
			kind: 'mistake_retry',
			status: 'pending',
			priority: 'medium',
			subject: '全部科目',
			href: '/manage/mistakes',
			source: 'estimated',
			provenanceNote: note,
		})
	}
	return tasks
}

/**
 * Map a canonical Mistake DTO to its card model (U4). Pure function.
 * subjectLabel stays null: subject names need taxonomy data the adapter does
 * not fetch (callers may enrich later via the knowledge adapter). reviewItemId
 * passes through only when present — no review semantics invented.
 */
export function adaptMistake(dto: Mistake): MistakeCardModel {
	return {
		id: dto.id,
		title: dto.title ?? dto.question_text,
		questionText: dto.question_text,
		reasonCategory: dto.reason_category,
		difficulty: dto.difficulty ?? 'unspecified',
		status: dto.status,
		subjectLabel: null,
		knowledgePointIds: dto.knowledge_point_ids,
		reviewItemId: dto.review_item_id || null,
		updatedAt: dto.updated_at,
		source: 'backend',
	}
}

/**
 * Map a canonical Question DTO to its card model (U6). Pure function.
 * options pass through for display; answer/analysis are stored values revealed
 * only in the 'result' practice state. No grading is performed anywhere.
 */
export function adaptQuestion(dto: Question): QuestionCardModel {
	return {
		id: dto.id,
		title: dto.title ?? dto.question_text,
		stem: dto.stem_md || dto.question_text,
		questionType: dto.question_type,
		options: dto.options.map(option => ({ key: option.key, text: option.text })),
		correctAnswer: dto.correct_answer,
		analysis: dto.analysis_md ?? dto.explanation,
		difficulty: dto.difficulty,
		status: dto.status,
		subjectLabel: null,
		knowledgePointIds: dto.knowledge_point_ids,
		updatedAt: dto.updated_at,
		source: 'backend',
	}
}

/**
 * Map taxonomy subjects + knowledge trees to knowledge nodes (U7).
 * Learning state and relation counts are NOT computed here: the taxonomy DTO
 * carries no learning signals, so they stay 'unknown'/null and the UI renders
 * “数据积累中”. Structure (not a bare tree dump) comes from the section layer.
 */
export function adaptKnowledgeTree(
	subject: Pick<Subject, 'id' | 'name'>,
	nodes: KnowledgePointTreeNode[],
): KnowledgeNode {
	const mapNode = (node: KnowledgePointTreeNode): KnowledgeNode => ({
		id: `kp-${node.id}`,
		kind: 'knowledge_point',
		name: node.name,
		description: node.description,
		learningState: 'unknown',
		relatedQuestions: null,
		relatedMistakes: null,
		relatedNotes: null,
		children: node.children.map(mapNode),
		source: 'backend',
	})
	return {
		id: `subject-${subject.id}`,
		kind: 'subject',
		name: subject.name,
		description: null,
		learningState: 'unknown',
		relatedQuestions: null,
		relatedMistakes: null,
		relatedNotes: null,
		children: nodes.map(mapNode),
		source: 'backend',
	}
}

/**
 * Map a NoteDetail DTO to a knowledge artifact (U8). knowledge_points arrives
 * as a legacy free-text field — split on common separators, never invent IDs.
 * The editor entry is linked, not reimplemented.
 */
export function adaptNoteArtifact(dto: NoteDetail): NoteArtifact {
	const rawPoints = dto.knowledge_points ?? ''
	const knowledgePoints = rawPoints
		.split(/[,，、;；]/)
		.map(part => part.trim())
		.filter(part => part.length > 0)
	return {
		id: dto.id,
		slug: dto.slug,
		title: dto.title,
		summary: dto.summary ?? null,
		subjectLabel: dto.subject ?? null,
		knowledgePoints,
		tags: Array.isArray(dto.tags) ? dto.tags.map(tag => tag.name) : [],
		updatedAt: dto.updated_at,
		editorHref: `/manage/notes/${encodeURIComponent(dto.slug)}`,
		source: 'backend',
	}
}

/** Map an Attachment DTO to a resource item (U10). Pure display mapping. */
export function adaptResource(dto: Attachment): ResourceItem {
	return {
		id: dto.id,
		name: dto.original_name,
		mimeType: dto.mime_type,
		sizeLabel: formatBytes(dto.size_bytes),
		uploadedAt: dto.created_at,
		source: 'backend',
	}
}

/**
 * Map a canonical ReviewItem DTO to a queue display item (T-U5-3, post-PR-08
 * contract re-audit). Honesty rules: status derives from the REAL
 * next_review_at (overdue iff past); subject is '未知科目' (the DTO carries
 * none — never invent one); priority follows the real overdue signal.
 */
export function adaptReviewItem(dto: ReviewItem, now: Date = new Date()): ReviewQueueItem {
	const overdue = new Date(dto.next_review_at).getTime() < now.getTime()
	return {
		task: {
			id: dto.id,
			title: dto.question_text,
			subject: '未知科目',
			priority: overdue ? 'high' : 'medium',
			status: overdue ? 'overdue' : 'pending',
			source: 'backend',
		},
		questionExcerpt: dto.question_text,
		hasReviewTarget: true,
		source: 'backend',
	}
}
