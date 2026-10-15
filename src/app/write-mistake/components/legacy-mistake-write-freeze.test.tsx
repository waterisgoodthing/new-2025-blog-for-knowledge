import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const mocks = vi.hoisted(() => ({
  createNote: vi.fn(),
  updateNote: vi.fn(),
  uploadImage: vi.fn(),
  analyzeMistake: vi.fn(),
  analyzeText: vi.fn(),
  listSubjects: vi.fn(),
  generateQuestionDraft: vi.fn(),
  confirmQuestionDraft: vi.fn(),
  generateErrorInterpretation: vi.fn(),
  rejectErrorInterpretation: vi.fn(),
  generateFinalAnalysis: vi.fn(),
  generateDiagram: vi.fn(),
  toastError: vi.fn(),
}))

vi.mock('next/navigation', () => ({
  useRouter: () => ({ push: vi.fn(), replace: vi.fn() }),
  useSearchParams: () => new URLSearchParams(),
}))
vi.mock('motion/react', () => ({
  motion: new Proxy({}, {
    get: () => ({ children, initial, animate, transition, ...rest }: Record<string, unknown> & { children?: unknown }) => (
      <div {...rest}>{children as never}</div>
    ),
  }),
}))
vi.mock('sonner', () => ({
  toast: {
    error: (...args: unknown[]) => mocks.toastError(...args),
    success: vi.fn(),
    warning: vi.fn(),
  },
}))
vi.mock('@/lib/api/notes', () => ({
  createNote: mocks.createNote,
  updateNote: mocks.updateNote,
  uploadImage: mocks.uploadImage,
}))
vi.mock('@/lib/api/ai', () => ({
  analyzeMistake: mocks.analyzeMistake,
  analyzeText: mocks.analyzeText,
  generateQuestionDraft: mocks.generateQuestionDraft,
  confirmQuestionDraft: mocks.confirmQuestionDraft,
  generateErrorInterpretation: mocks.generateErrorInterpretation,
  rejectErrorInterpretation: mocks.rejectErrorInterpretation,
  generateFinalAnalysis: mocks.generateFinalAnalysis,
  generateDiagram: mocks.generateDiagram,
}))
vi.mock('@/lib/api/meta', () => ({ listSubjects: mocks.listSubjects }))
vi.mock('@/components/tag-suggestion-dialog', () => ({ TagSuggestionDialog: () => null }))

import { MistakeForm } from './mistake-form'
import { StagedMistakeForm } from './staged-mistake-form'

const questionDraft = {
  title: 'T',
  question: 'Q',
  options: [],
  visual_context: '',
  key_conditions: [],
  candidate_answer: 'A',
  knowledge_points: 'KP',
  question_type: 'choice',
  subject: 'Math',
  difficulty: 'medium',
  tags: [],
  image_dependency: '',
}

const interpretation = {
  interpretation_id: 'i-1',
  version: 1,
  summary: 'S',
  diagnosis: 'D',
  root_cause: 'R',
  knowledge_gap: 'G',
  suggested_correction: 'C',
  reasoning_trace: '',
}

const finalAnalysis = {
  analysis: 'ANALYSIS_BODY',
  error_reason: 'E',
  key_step: 'K',
  similar_traps: [],
  generalization: 'G',
  review_advice: 'A',
  variant_questions: [],
  accepted_interpretation_id: 'i-1',
  accepted_interpretation_version: 1,
}

describe('legacy mistake writer UI freeze (W3-D09 F-4/F-5)', () => {
  beforeEach(() => {
    for (const fn of Object.values(mocks)) fn.mockReset?.()
    mocks.listSubjects.mockResolvedValue([])
  })

  it('freezes MistakeForm submit behind a visible notice', async () => {
    render(<MistakeForm mode='create' />)

    expect(await screen.findByTestId('legacy-mistake-write-frozen')).toHaveTextContent(
      'legacy 错题写入已冻结，请使用 canonical 错题流程',
    )
    const save = screen.getByTestId('legacy-mistake-save-disabled')
    expect(save).toBeDisabled()
    expect(save).toHaveTextContent('已冻结')
  })

  it('freezes StagedMistakeForm save after the full AI pipeline', async () => {
    mocks.generateQuestionDraft.mockResolvedValue(questionDraft)
    mocks.confirmQuestionDraft.mockResolvedValue({ status: 'confirmed', draft: questionDraft, confirmed_at: '' })
    mocks.generateErrorInterpretation.mockResolvedValue(interpretation)
    mocks.generateFinalAnalysis.mockResolvedValue(finalAnalysis)

    render(<StagedMistakeForm />)

    expect(await screen.findByTestId('legacy-mistake-write-frozen')).toBeInTheDocument()

    const paste = await screen.findByPlaceholderText('粘贴题目内容...')
    fireEvent.change(paste, { target: { value: '题干文本' } })
    fireEvent.click(screen.getByRole('button', { name: /识别题目/ }))

    fireEvent.click(await screen.findByRole('button', { name: /确认题目/ }))

    fireEvent.change(await screen.findByPlaceholderText(/例如：没有结合/), {
      target: { value: '概念混淆' },
    })
    fireEvent.click(screen.getByRole('button', { name: /生成错因理解/ }))

    fireEvent.click(await screen.findByRole('button', { name: /^采纳$/ }))

    fireEvent.click(await screen.findByRole('button', { name: /生成解析/ }))

    const save = await screen.findByTestId('legacy-mistake-save-disabled')
    expect(save).toBeDisabled()
    expect(save).toHaveTextContent('保存错题（已冻结）')
    await waitFor(() => expect(mocks.createNote).not.toHaveBeenCalled())
    await waitFor(() => expect(mocks.updateNote).not.toHaveBeenCalled())
  })
})
