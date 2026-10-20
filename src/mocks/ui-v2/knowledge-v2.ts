import type { KnowledgeNode } from '../../contracts/ui-v2/knowledge'
import type { UiPageModel } from '../../contracts/ui-v2/ui-state'

// Knowledge mocks (U7): structure with honest null counts. Not a bare tree
// dump: the section layer groups by learning state + relations.

const mathTree: KnowledgeNode = {
	id: 'subject-1',
	kind: 'subject',
	name: '数学',
	description: null,
	learningState: 'learning',
	relatedQuestions: 8,
	relatedMistakes: 3,
	relatedNotes: 2,
	children: [
		{
			id: 'kp-11',
			kind: 'knowledge_point',
			name: '函数单调性',
			description: '导数符号与单调区间',
			learningState: 'reviewing',
			relatedQuestions: 5,
			relatedMistakes: 3,
			relatedNotes: 1,
			children: [],
			source: 'mock',
		},
		{
			id: 'kp-12',
			kind: 'knowledge_point',
			name: '解析几何',
			description: null,
			learningState: 'unknown',
			relatedQuestions: null,
			relatedMistakes: null,
			relatedNotes: null,
			children: [],
			source: 'mock',
		},
	],
	source: 'mock',
}

export const mockKnowledgeNormal: UiPageModel<KnowledgeNode[]> = {
	state: 'ready',
	data: [mathTree],
	error: null,
	source: 'mock',
}

export const mockKnowledgeEmpty: UiPageModel<KnowledgeNode[]> = {
	state: 'empty',
	data: [],
	error: null,
	source: 'mock',
}

export const mockKnowledgeLoading: UiPageModel<KnowledgeNode[]> = {
	state: 'loading',
	data: null,
	error: null,
	source: 'mock',
}

export const mockKnowledgeError: UiPageModel<KnowledgeNode[]> = {
	state: 'error',
	data: null,
	error: 'mock: 知识体系加载失败，请重试',
	source: 'mock',
}
