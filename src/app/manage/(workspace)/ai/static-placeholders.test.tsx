import { describe, expect, it, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
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

  it('renders Capture without upload or OCR processing controls', () => {
    render(<ManageCapturePage />)

    expect(screen.getByRole('heading', { name: '图片采集' })).toBeInTheDocument()
    expect(screen.getByText(/不读取 capture_items/)).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: /上传|识别|开始/ })).not.toBeInTheDocument()
  })
})
