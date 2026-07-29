import { describe, expect, it } from 'vitest'

import { navGroups } from './manage-sidebar'

describe('ManageSidebar navigation facts', () => {
  it('marks the enabled Capture workspace as active instead of deferred', () => {
    const capture = navGroups.flatMap((group) => group.items).find((item) => item.href === '/manage/capture')

    expect(capture?.status).toBe('active')
  })
})
