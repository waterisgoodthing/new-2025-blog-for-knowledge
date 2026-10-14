import { describe, expect, it } from 'vitest'

import { navGroups } from './manage-sidebar'

describe('ManageSidebar navigation facts', () => {
	it('marks the enabled Capture workspace as active instead of deferred', () => {
		const capture = navGroups.flatMap(group => group.items).find(item => item.href === '/manage/capture')

		expect(capture?.status).toBe('active')
	})

	it('exposes the converged notes authoring workspace first in content management', () => {
		const content = navGroups.find(group => group.title === '内容管理')
		expect(content?.items[0]).toMatchObject({ href: '/manage/notes', label: '笔记写作' })
	})
})
