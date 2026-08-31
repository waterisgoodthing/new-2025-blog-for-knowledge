const questionTypeLabels = {
  short_answer: '简答题',
  single_choice: '单选题',
  multiple_choice: '多选题',
  true_false: '判断题',
  essay: '论述题',
} as const

const difficultyLabels = {
  unspecified: '未设置',
  easy: '简单',
  medium: '中等',
  hard: '困难',
} as const

const questionStatusLabels = {
  active: '使用中',
  archived: '已归档',
} as const

const attachmentStatusLabels = {
  active: '可用',
  missing: '文件缺失',
  deleted: '已删除',
} as const

const attachmentVisibilityLabels = {
  private: '私有',
} as const

const attachmentTargetLabels = {
  question_draft: '题目草稿',
  question: '题目',
  mistake: '错题',
} as const

const attachmentPurposeLabels = {
  source: '学习资料',
  question: '题目附件',
  answer: '答案附件',
  inline: '正文插图',
} as const

function labelFor<T extends Record<string, string>>(labels: T, value: string): string {
  return labels[value as keyof T] ?? value
}

export function questionTypeLabel(value: string): string {
  return labelFor(questionTypeLabels, value)
}

export function difficultyLabel(value: string | null | undefined): string {
  return value ? labelFor(difficultyLabels, value) : '未设置'
}

export function questionStatusLabel(value: string): string {
  return labelFor(questionStatusLabels, value)
}

export function attachmentStatusLabel(value: string): string {
  return labelFor(attachmentStatusLabels, value)
}

export function attachmentVisibilityLabel(value: string): string {
  return labelFor(attachmentVisibilityLabels, value)
}

export function attachmentTargetLabel(value: string): string {
  return labelFor(attachmentTargetLabels, value)
}

export function attachmentPurposeLabel(value: string): string {
  return labelFor(attachmentPurposeLabels, value)
}

function parseDate(value: string): Date | null {
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? null : date
}

export function formatChineseDate(value: string): string {
  const date = parseDate(value)
  if (!date) return ''
  return new Intl.DateTimeFormat('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    timeZone: 'Asia/Shanghai',
  }).format(date)
}

export function formatChineseDateTime(value: string): string {
  const date = parseDate(value)
  if (!date) return ''
  return new Intl.DateTimeFormat('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
    timeZone: 'Asia/Shanghai',
  }).format(date)
}
