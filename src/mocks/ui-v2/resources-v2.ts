import type { UiPageModel } from '../../contracts/ui-v2/ui-state'
import type { Attachment } from '../../lib/api/attachments'

// Resource mocks (U10): raw Attachment DTO shapes.

const mockDto: Attachment = {
	id: 'mock-att-1',
	original_name: '单调性手写推导.jpg',
	storage_provider: 'local',
	mime_type: 'image/jpeg',
	size_bytes: 184320,
	checksum_sha256: 'mock-checksum',
	visibility: 'private',
	status: 'active',
	created_at: '2026-09-12',
	updated_at: '2026-09-12',
	deleted_at: null,
}

export function mockAttachmentDtos(): Attachment[] {
	return [mockDto]
}

export const mockResourcesNormal: UiPageModel<Attachment[]> = {
	state: 'ready',
	data: [mockDto],
	error: null,
	source: 'mock',
}

export const mockResourcesEmpty: UiPageModel<Attachment[]> = {
	state: 'empty',
	data: [],
	error: null,
	source: 'mock',
}

export const mockResourcesLoading: UiPageModel<Attachment[]> = {
	state: 'loading',
	data: null,
	error: null,
	source: 'mock',
}

export const mockResourcesError: UiPageModel<Attachment[]> = {
	state: 'error',
	data: null,
	error: 'mock: 资料加载失败，请重试',
	source: 'mock',
}
