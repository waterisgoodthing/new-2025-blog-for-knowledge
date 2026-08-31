import { describe, expect, it } from 'vitest'

import {
  attachmentPurposeLabel,
  attachmentStatusLabel,
  attachmentTargetLabel,
  attachmentVisibilityLabel,
  difficultyLabel,
  formatChineseDate,
  formatChineseDateTime,
  questionStatusLabel,
  questionTypeLabel,
} from './manage-display'

describe('manage display vocabulary', () => {
  it('maps stored enum values to Chinese product labels', () => {
    expect(difficultyLabel('medium')).toBe('中等')
    expect(difficultyLabel(null)).toBe('未设置')
    expect(questionTypeLabel('single_choice')).toBe('单选题')
    expect(questionStatusLabel('active')).toBe('使用中')
    expect(attachmentStatusLabel('missing')).toBe('文件缺失')
    expect(attachmentVisibilityLabel('private')).toBe('私有')
    expect(attachmentTargetLabel('question_draft')).toBe('题目草稿')
    expect(attachmentPurposeLabel('source')).toBe('学习资料')
  })

  it('uses one Chinese date convention and handles invalid input safely', () => {
    expect(formatChineseDate('2026-06-23T08:09:00+08:00')).toBe('2026年6月23日')
    expect(formatChineseDateTime('2026-06-23T08:09:00+08:00')).toBe('2026年6月23日 08:09')
    expect(formatChineseDate('not-a-date')).toBe('')
    expect(formatChineseDateTime('not-a-date')).toBe('')
  })
})
