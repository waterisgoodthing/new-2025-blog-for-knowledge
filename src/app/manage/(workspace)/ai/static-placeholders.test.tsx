import { describe, expect, it } from 'vitest'
import { render, screen } from '@testing-library/react'
import { readFileSync } from 'node:fs'

import ManageAiPage from './page'
import ManageAiRunsPage from './runs/page'
import ManageCapturePage from '../capture/page'

describe('Batch 6 static AI/OCR placeholders', () => {
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

    expect(screen.getByRole('heading', { name: 'AI' })).toBeInTheDocument()
    expect(screen.getByText(/不读取 AI runs/)).toBeInTheDocument()
    expect(screen.queryByRole('table')).not.toBeInTheDocument()
    expect(screen.queryByRole('button')).not.toBeInTheDocument()
  })

  it('renders the run-history placeholder without historical rows', () => {
    render(<ManageAiRunsPage />)

    expect(screen.getByRole('heading', { name: 'AI Runs' })).toBeInTheDocument()
    expect(screen.getByText(/不显示 ai_runs 或 ai_call_logs/)).toBeInTheDocument()
  })

  it('renders Capture without upload or OCR processing controls', () => {
    render(<ManageCapturePage />)

    expect(screen.getByRole('heading', { name: 'Capture' })).toBeInTheDocument()
    expect(screen.getByText(/不上传文件/)).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: /上传|识别|开始/ })).not.toBeInTheDocument()
  })
})
