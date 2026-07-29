import { describe, expect, it, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { readFileSync } from 'node:fs'

import ManageAiPage from './page'
import ManageAiRunsPage from './runs/page'
import ManageCapturePage from '../capture/page'

vi.mock('@/lib/api/ai-runs', () => ({
  getAiRuns: vi.fn().mockResolvedValue({ items: [], total: 0, limit: 20, offset: 0 }),
  getAiRun: vi.fn(),
  retryAiRun: vi.fn(),
  decideAiRun: vi.fn(),
}))

vi.mock('next/navigation', () => ({
  useRouter: () => ({ push: vi.fn() }),
}))

vi.mock('@/lib/api/captures', () => ({
  listCaptures: vi.fn().mockResolvedValue([]),
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

describe('AI governance and image-capture surfaces', () => {
  it('keeps all three routes under the shared manage AuthGate', () => {
    const layoutSource = readFileSync(
      'src/app/manage/(workspace)/layout.tsx',
      'utf8',
    )

    expect(layoutSource).toContain("import { AuthGate } from '@/components/auth-gate'")
    expect(layoutSource).toContain('<AuthGate>')
  })

  it('renders AI run governance without invoking a provider', () => {
    render(<ManageAiPage />)

    expect(screen.getByRole('heading', { name: 'AI 运行记录' })).toBeInTheDocument()
    expect(screen.getByText(/真实运行记录/)).toBeInTheDocument()
  })

  it('renders the run-history governance surface', () => {
    render(<ManageAiRunsPage />)

    expect(screen.getByRole('heading', { name: 'AI 运行记录' })).toBeInTheDocument()
    expect(screen.getByText(/真实来源、失败态/)).toBeInTheDocument()
  })

  it('renders the current Capture entry modes with an App Router fixture', async () => {
    render(<ManageCapturePage />)

    expect(screen.getByRole('heading', { name: '图片采集' })).toBeInTheDocument()
    expect(screen.getByRole('group', { name: '采集方式' })).toBeInTheDocument()
    await waitFor(() => {
      expect(screen.getByRole('button', { name: '点击上传图片' })).toBeInTheDocument()
    })
  })
})
