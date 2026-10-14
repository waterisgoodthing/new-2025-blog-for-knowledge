import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { fireEvent, render, screen, waitFor } from '@testing-library/react'

import type { Capture } from '@/lib/api/captures'

vi.mock('next/navigation', () => ({
  useRouter: () => ({ push: vi.fn() }),
}))

vi.mock('sonner', () => ({
  toast: { error: vi.fn(), success: vi.fn() },
}))

vi.mock('@/lib/utils', () => ({
  cn: (...classes: unknown[]) => classes.filter(Boolean).join(' '),
}))

vi.mock('@/lib/api/config', () => ({
  getApiBase: () => 'http://localhost:8000',
}))

vi.mock('@/lib/api/captures', () => ({
  listCaptures: vi.fn(),
  getCapture: vi.fn(),
  createCapture: vi.fn(),
  patchCapture: vi.fn(),
  triggerRecognition: vi.fn(),
  triggerDraft: vi.fn(),
  convertCapture: vi.fn(),
}))

vi.mock('@/lib/api/taxonomy', () => ({
  listSubjects: vi.fn().mockResolvedValue([]),
  listKnowledgePoints: vi.fn().mockResolvedValue([]),
}))

vi.mock('@/lib/api/attachments', () => ({
  getAttachmentContentUrl: (id: string) => `http://attachments/${id}`,
  uploadAttachment: vi.fn(),
}))

const capturesApi = await import('@/lib/api/captures')
const taxonomyApi = await import('@/lib/api/taxonomy')
const { CaptureWorkspace } = await import('./capture-workspace')

function makeCapture(overrides: Partial<Capture> = {}): Capture {
  return {
    id: '11111111-1111-1111-1111-111111111111',
    source_attachment_id: '22222222-2222-2222-2222-222222222222',
    status: 'recognized',
    recognized_text: null,
    user_error_context: null,
    question_draft_text: null,
    analysis_draft_text: null,
    error_summary_draft: null,
    subject_id: null,
    knowledge_point_suggestions: [],
    model_output_version: 'v1',
    attempt_count: 1,
    last_stage: 'recognize',
    error_code: null,
    error_message_safe: null,
    failure_category: null,
    started_at: null,
    finished_at: null,
    mistake_draft_item_id: null,
    created_by: null,
    created_at: '2026-09-26T00:00:00Z',
    updated_at: '2026-09-26T00:00:00Z',
    ...overrides,
  }
}

describe('CaptureWorkspace — OCR states', () => {
  beforeEach(() => {
    vi.mocked(taxonomyApi.listSubjects).mockResolvedValue([])
    vi.mocked(taxonomyApi.listKnowledgePoints).mockResolvedValue([])
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({ ok: false, status: 404 }),
    )
  })

  afterEach(() => {
    vi.unstubAllGlobals()
    vi.unstubAllEnvs()
    vi.clearAllMocks()
  })

  it('shows a loading indicator while the capture list is pending', () => {
    vi.mocked(taxonomyApi.listSubjects).mockReturnValue(
      new Promise(() => {}),
    )
    vi.mocked(capturesApi.listCaptures).mockReturnValue(
      new Promise<Capture[]>(() => {}),
    )

    const { container } = render(<CaptureWorkspace />)

    expect(container.querySelector('.animate-spin')).not.toBeNull()
  })

  it('renders recognized text on success', async () => {
    const capture = makeCapture({
      status: 'recognized',
      recognized_text: '测试题目文字',
    })
    vi.mocked(capturesApi.listCaptures).mockResolvedValue([capture])
    vi.mocked(capturesApi.getCapture).mockResolvedValue(capture)

    render(<CaptureWorkspace />)

    expect(await screen.findByDisplayValue('测试题目文字')).toBeInTheDocument()
    expect(screen.getAllByText('已识别').length).toBeGreaterThan(0)
  })

  it('renders the failure category label with the safe error message', async () => {
    vi.stubEnv('NEXT_PUBLIC_OCR_AUTO_RECOGNITION_ENABLED', 'true')
    const capture = makeCapture({
      status: 'failed',
      last_stage: 'recognize',
      error_code: 'provider_auth',
      error_message_safe: 'AI provider authentication failed',
      failure_category: 'provider_auth',
    })
    vi.mocked(capturesApi.listCaptures).mockResolvedValue([capture])
    vi.mocked(capturesApi.getCapture).mockResolvedValue(capture)

    render(<CaptureWorkspace />)

    expect(
      await screen.findByText('AI 服务未授权或额度不足'),
    ).toBeInTheDocument()
    expect(
      screen.getByText('AI provider authentication failed'),
    ).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /重新识别/ })).toBeInTheDocument()
  })

  it('renders draft-stage failure text instead of OCR-image text', async () => {
    const capture = makeCapture({
      status: 'failed',
      last_stage: 'draft',
      error_code: 'provider_error',
      error_message_safe: 'AI provider error',
      failure_category: 'unknown',
    })
    vi.mocked(capturesApi.listCaptures).mockResolvedValue([capture])
    vi.mocked(capturesApi.getCapture).mockResolvedValue(capture)

    render(<CaptureWorkspace />)

    expect(await screen.findByText('草稿生成失败')).toBeInTheDocument()
    expect(screen.queryByText('图片读取失败')).not.toBeInTheDocument()
    expect(screen.queryByText('未识别到内容')).not.toBeInTheDocument()
  })

  it('does not show the empty-result state for a draft-stage empty failure', async () => {
    const capture = makeCapture({
      status: 'failed',
      last_stage: 'draft',
      error_code: 'empty_result',
      error_message_safe: 'Recognition returned empty text',
      failure_category: 'invalid_response',
    })
    vi.mocked(capturesApi.listCaptures).mockResolvedValue([capture])
    vi.mocked(capturesApi.getCapture).mockResolvedValue(capture)

    render(<CaptureWorkspace />)

    expect(await screen.findByText('草稿结果无效')).toBeInTheDocument()
    expect(screen.queryByText('未识别到内容')).not.toBeInTheDocument()
  })

  it('shows a distinct empty-result state for error_code empty_result', async () => {
    vi.stubEnv('NEXT_PUBLIC_OCR_AUTO_RECOGNITION_ENABLED', 'true')
    const capture = makeCapture({
      status: 'failed',
      error_code: 'empty_result',
      error_message_safe: 'Recognition returned empty text',
      failure_category: 'invalid_response',
    })
    vi.mocked(capturesApi.listCaptures).mockResolvedValue([capture])
    vi.mocked(capturesApi.getCapture).mockResolvedValue(capture)

    render(<CaptureWorkspace />)

    await waitFor(() =>
      expect(screen.getByText('未识别到内容')).toBeInTheDocument(),
    )
    expect(
      screen.queryByText('Recognition returned empty text'),
    ).not.toBeInTheDocument()
    expect(screen.getByRole('button', { name: /重新识别/ })).toBeInTheDocument()
  })

  it('disables automatic OCR by default and keeps the manual entry path', async () => {
    const capture = makeCapture({ status: 'uploaded', recognized_text: null })
    vi.mocked(capturesApi.listCaptures).mockResolvedValue([capture])
    vi.mocked(capturesApi.getCapture).mockResolvedValue(capture)

    render(<CaptureWorkspace />)

    expect(
      await screen.findByText(/自动识别当前已关闭/),
    ).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: /开始识别/ })).not.toBeInTheDocument()
    // manual recognized-text input is still available
    expect(
      screen.getByPlaceholderText('识别文字将显示在这里，可手动修正'),
    ).toBeInTheDocument()
  })
})

// NOTE: appended outside the describe below is invalid; we re-open a new describe at module top-level.
describe('CaptureWorkspace — EV05 manual capture path', () => {
  beforeEach(() => {
    vi.stubEnv('NEXT_PUBLIC_OCR_AUTO_RECOGNITION_ENABLED', 'false')
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({ ok: false, status: 404 }),
    )
  })

  afterEach(() => {
    vi.unstubAllGlobals()
    vi.unstubAllEnvs()
    vi.clearAllMocks()
  })

  it('lets a fresh uploaded capture enter the question text manually and save to ready', async () => {
    const uploaded = makeCapture({ status: 'uploaded', recognized_text: null })
    const ready = makeCapture({
      status: 'ready',
      question_draft_text: '手动题面',
    })
    vi.mocked(capturesApi.listCaptures).mockResolvedValue([uploaded])
    vi.mocked(capturesApi.getCapture).mockResolvedValue(uploaded)
    vi.mocked(capturesApi.patchCapture).mockResolvedValue(ready)

    render(<CaptureWorkspace />)

    // the manual question-text section is offered on a fresh uploaded item
    expect(await screen.findByText('人工题面（可编辑）')).toBeInTheDocument()

    const questionBox = screen.getByPlaceholderText('题面草稿')
    fireEvent.change(questionBox, { target: { value: '人工填写的题面' } })
    fireEvent.click(screen.getByRole('button', { name: '保存修改' }))

    await waitFor(() =>
      expect(capturesApi.patchCapture).toHaveBeenCalledWith(
        uploaded.id,
        {
          question_draft_text: '人工填写的题面',
          analysis_draft_text: null,
          error_summary_draft: null,
        },
      ),
    )

    // the patch returns the ready capture: convert form becomes reachable
    expect(await screen.findByText('确认并转为错题草稿')).toBeInTheDocument()
  })

  it('offers the manual next step when only recognized text exists', async () => {
    const capture = makeCapture({
      status: 'recognized',
      recognized_text: '识别文字',
      question_draft_text: null,
    })
    vi.mocked(capturesApi.listCaptures).mockResolvedValue([capture])
    vi.mocked(capturesApi.getCapture).mockResolvedValue(capture)

    render(<CaptureWorkspace />)

    expect(
      await screen.findByText(/请继续在下方填写题面并保存/),
    ).toBeInTheDocument()
  })
})
