import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import type { ReactNode } from 'react'

vi.mock('sonner', () => ({
  toast: {
    error: vi.fn(),
    success: vi.fn(),
  },
}))

vi.mock('@/lib/api/client', () => ({
  ApiError: class ApiError extends Error {
    status: number
    constructor(message: string, status: number) {
      super(message)
      this.name = 'ApiError'
      this.status = status
    }
  },
}))

vi.mock('@/lib/api/ai-runs', () => ({
  getAiRuns: vi.fn(),
  getAiRun: vi.fn(),
  retryAiRun: vi.fn(),
  decideAiRun: vi.fn(),
}))

vi.mock('../../../components/manage-empty-state', () => ({
  ManageEmptyState: ({ message }: { message: string }) => <div>{message}</div>,
}))
vi.mock('../../../components/manage-status-badge', () => ({
  ManageStatusBadge: ({ children }: { children: ReactNode }) => (
    <span>{children}</span>
  ),
}))

const aiRunsApi = await import('@/lib/api/ai-runs')
const { AiRunsPanel } = await import('./ai-runs-panel')

const mockRuns = [
  {
    id: 'run-1',
    task_type: 'analyze_mistake',
    target_type: null,
    target_id: null,
    provider_used: 'openai',
    model: 'gpt-4',
    prompt_version: 'v1',
    status: 'succeeded' as const,
    validation_status: 'passed' as const,
    review_status: 'pending' as const,
    review_revision: 1,
    attempt: 1,
    parent_run_id: null,
    latency_ms: 5000,
    error_code: null,
    error_message_safe: null,
    started_at: '2025-01-15T10:00:00Z',
    finished_at: '2025-01-15T10:00:05Z',
    created_at: '2025-01-15T10:00:00Z',
    updated_at: '2025-01-15T10:00:05Z',
  },
  {
    id: 'run-2',
    task_type: 'generate_variant',
    target_type: null,
    target_id: null,
    provider_used: 'anthropic',
    model: 'claude-3',
    prompt_version: 'v2',
    status: 'failed' as const,
    validation_status: 'not_applicable' as const,
    review_status: 'not_required' as const,
    review_revision: 1,
    attempt: 1,
    parent_run_id: null,
    latency_ms: 3000,
    error_code: 'PROVIDER_ERROR',
    error_message_safe: '调用失败',
    started_at: '2025-01-15T11:00:00Z',
    finished_at: '2025-01-15T11:00:03Z',
    created_at: '2025-01-15T11:00:00Z',
    updated_at: '2025-01-15T11:00:03Z',
  },
]

const mockRunDetail = {
  ...mockRuns[0],
  output_data: { result: 'controlled output test' },
  warnings: null,
  reviewed_at: null,
  review_note: null,
}

describe('AiRunsPanel — focusable records and Enter to open detail (R-05)', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.mocked(aiRunsApi.getAiRuns).mockResolvedValue({
      items: mockRuns,
      total: 2,
      limit: 20,
      offset: 0,
    })
    vi.mocked(aiRunsApi.getAiRun).mockResolvedValue(mockRunDetail)
  })

  it('renders record rows that are focusable via tabIndex=0', async () => {
    render(<AiRunsPanel />)

    await waitFor(() => {
      expect(screen.getByTestId('ai-runs-table')).toBeInTheDocument()
    })

    // Get all rows — skip the header row
    const rows = screen.getAllByRole('row')
    expect(rows.length).toBe(3) // header + 2 data rows

    const dataRows = rows.slice(1)
    for (const row of dataRows) {
      expect(row.getAttribute('tabindex')).toBe('0')
    }
  })

  it('provides aria-label instructing Enter to view details', async () => {
    render(<AiRunsPanel />)

    await waitFor(() => {
      expect(screen.getByTestId('ai-runs-table')).toBeInTheDocument()
    })

    const rows = screen.getAllByRole('row')
    const firstDataRow = rows[1]
    const label = firstDataRow.getAttribute('aria-label') ?? ''
    expect(label).toContain('按 Enter 查看详情')
  })

  it('opens detail panel when Enter is pressed on a focused row', async () => {
    render(<AiRunsPanel />)

    await waitFor(() => {
      expect(screen.getByTestId('ai-runs-table')).toBeInTheDocument()
    })

    // Before pressing Enter, detail panel shows empty state
    expect(screen.getByText('选择一条记录查看详情。')).toBeInTheDocument()

    // Focus and press Enter on the first data row
    const rows = screen.getAllByRole('row')
    const firstDataRow = rows[1]
    fireEvent.keyDown(firstDataRow, { key: 'Enter' })

    // Verify getAiRun was called with the correct ID
    expect(vi.mocked(aiRunsApi.getAiRun)).toHaveBeenCalledWith('run-1')

    // Wait for detail panel to appear
    await waitFor(() => {
      expect(screen.getByText('受控输出')).toBeInTheDocument()
    })

    // Detail panel should show the output data
    expect(screen.getByText(/controlled output test/)).toBeInTheDocument()
  })
})
