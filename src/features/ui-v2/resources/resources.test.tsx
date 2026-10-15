import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import { adaptResource } from '../../../adapters/ui-v2/from-backend'
import { formatBytes } from '../../../contracts/ui-v2/resource'
import {
	mockAttachmentDtos,
	mockResourcesEmpty,
	mockResourcesError,
	mockResourcesLoading,
	mockResourcesNormal,
} from '../../../mocks/ui-v2/resources-v2'
import { Uiv2ResourcesSection } from './ResourcesSection'

describe('formatBytes', () => {
	it('formats sizes and degrades unknown input to null', () => {
		expect(formatBytes(512)).toBe('512 B')
		expect(formatBytes(184320)).toBe('180 KB')
		expect(formatBytes(null)).toBeNull()
		expect(formatBytes(-1)).toBeNull()
		expect(formatBytes(Number.NaN)).toBeNull()
	})
})

describe('adaptResource', () => {
	it('maps the attachment DTO to a display item', () => {
		const [item] = mockAttachmentDtos().map(adaptResource)
		expect(item).toMatchObject({
			id: 'mock-att-1',
			name: '单调性手写推导.jpg',
			mimeType: 'image/jpeg',
			sizeLabel: '180 KB',
			source: 'backend',
		})
	})
})

describe('Uiv2ResourcesSection', () => {
	it('renders resource cards', () => {
		const items = mockResourcesNormal.data?.map(adaptResource) ?? []
		render(<Uiv2ResourcesSection model={{ state: 'ready', data: items, error: null, source: 'mock' }} />)
		expect(screen.getByText('单调性手写推导.jpg')).toBeInTheDocument()
		expect(screen.getByText('image/jpeg')).toBeInTheDocument()
	})

	it('covers loading / empty / error states', () => {
		const { rerender } = render(<Uiv2ResourcesSection model={mockResourcesLoading} />)
		expect(screen.getByRole('status', { name: '正在加载资料' })).toBeInTheDocument()

		rerender(<Uiv2ResourcesSection model={mockResourcesEmpty} />)
		expect(screen.getByText('还没有上传任何资料。')).toBeInTheDocument()

		rerender(<Uiv2ResourcesSection model={mockResourcesError} />)
		expect(screen.getByRole('alert')).toHaveTextContent('mock: 资料加载失败，请重试')
	})
})
