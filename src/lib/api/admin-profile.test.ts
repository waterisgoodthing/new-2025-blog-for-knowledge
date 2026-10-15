import { describe, expect, it } from 'vitest'

import { validateHomePreferences, type HomePreferences } from './admin-profile'

const validPreferences: HomePreferences = {
  show_welcome: true,
  section_order: ['today', 'activity', 'stats', 'storage'],
  hidden_sections: [],
}

describe('home preferences contract', () => {
  it('requires at least one learning action section to remain visible', () => {
    expect(validateHomePreferences({
      ...validPreferences,
      hidden_sections: ['today', 'activity'],
    })).toBe('至少保留一个学习行动区块（今日任务或最近活动）。')
  })
})
