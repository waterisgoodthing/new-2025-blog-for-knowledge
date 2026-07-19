import { describe, expect, it } from 'vitest'
import { render, screen } from '@testing-library/react'
import { readFileSync } from 'node:fs'

import ManageAiPage from './page'
import ManageAiRunsPage from './runs/page'
import ManageCapturePage from '../capture/page'

describe('Deferred AI and image-capture surfaces', () => {
  it('keeps all three routes under the shared manage AuthGate', () => {
    const layoutSource = readFileSync(
      'src/app/manage/(workspace)/layout.tsx',
      'utf8',
    )

    expect(layoutSource).toContain("import { AuthGate } from '@/components/auth-gate'")
    expect(layoutSource).toContain('<AuthGate>')
  })

  it('renders AI without provider or run state', () => {
    render(<ManageAiPage />)

    expect(screen.getByRole('heading', { name: 'AI 助手' })).toBeInTheDocument()
    expect(screen.getByText(/不调用 AI/)).toBeInTheDocument()
    expect(screen.queryByRole('table')).not.toBeInTheDocument()
    expect(screen.queryByRole('button')).not.toBeInTheDocument()
  })

  it('renders the run-history placeholder without historical rows', () => {
    render(<ManageAiRunsPage />)

    expect(screen.getByRole('heading', { name: 'AI 运行记录' })).toBeInTheDocument()
    expect(screen.getByText(/不读取、不重试/)).toBeInTheDocument()
  })

  it('renders Capture without upload or OCR processing controls', () => {
    render(<ManageCapturePage />)

    expect(screen.getByRole('heading', { name: '图片采集' })).toBeInTheDocument()
    expect(screen.getByText(/不读取 capture_items/)).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: /上传|识别|开始/ })).not.toBeInTheDocument()
  })
})
