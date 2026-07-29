import { describe, expect, it } from 'vitest'

import { navGroups } from './manage-sidebar'

describe('manage navigation information architecture', () => {
  it('makes the learning loop discoverable in product language', () => {
    const groups = navGroups.map((group) => ({
      title: group.title,
      labels: group.items.map((item) => item.label),
    }))

    expect(groups).toEqual(expect.arrayContaining([
      { title: '学习空间', labels: ['概览'] },
      { title: '内容管理', labels: ['草稿', '题目', '错题'] },
      { title: '知识体系', labels: ['科目', '知识点'] },
      { title: '学习计划', labels: ['复习'] },
      { title: '资料管理', labels: ['附件'] },
      { title: '工具', labels: ['采集', 'AI'] },
      { title: '系统', labels: ['设置'] },
    ]))

    const hrefs = navGroups.flatMap((group) => group.items.map((item) => item.href))
    expect(hrefs).toEqual(expect.arrayContaining([
      '/manage/dashboard',
      '/manage/drafts',
      '/manage/questions',
      '/manage/mistakes',
      '/manage/review',
      '/manage/attachments',
      '/manage/capture',
      '/manage/ai',
      '/manage/settings',
    ]))
  })
})
