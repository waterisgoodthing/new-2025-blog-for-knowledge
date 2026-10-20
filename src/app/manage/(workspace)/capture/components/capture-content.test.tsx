import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'

vi.mock('@/lib/utils', () => ({
  cn: (...classes: unknown[]) => classes.filter(Boolean).join(' '),
}))

vi.mock('./capture-workspace', () => ({
  CaptureWorkspace: () => <div data-testid='capture-workspace'>CaptureWorkspace</div>,
}))

vi.mock('./manual-question-entry', () => ({
  ManualQuestionEntry: () => {
    return (
      <div data-testid='manual-entry'>
        <input
          data-testid='manual-input'
          type='text'
          placeholder='题干'
        />
      </div>
    )
  },
}))

vi.mock('./mistake-draft-entry', () => ({
  MistakeDraftEntry: () => <div data-testid='mistake-entry'>MistakeDraftEntry</div>,
}))

const { CaptureContent } = await import('./capture-content')

describe('CaptureContent — state preservation (R-02 / P1-02)', () => {
  it('preserves manual entry state across mode switches', () => {
    const { container } = render(<CaptureContent />)

    // Initially image mode is active
    expect(screen.getByTestId('capture-workspace')).toBeVisible()

    // Switch to manual mode
    fireEvent.click(screen.getByRole('button', { name: /手工录入题目/ }))

    // Manual entry is now visible
    const input = screen.getByTestId('manual-input') as HTMLInputElement
    expect(input).toBeVisible()

    // Type something
    fireEvent.change(input, { target: { value: '测试题干内容' } })
    expect(input.value).toBe('测试题干内容')

    // Switch to image mode
    fireEvent.click(screen.getByRole('button', { name: /上传图片/ }))
    expect(screen.getByTestId('capture-workspace')).toBeVisible()

    // Manual entry should still be in DOM but hidden
    const hiddenInput = container.querySelector(
      '[data-testid="manual-input"]',
    ) as HTMLInputElement
    expect(hiddenInput).toBeInTheDocument()
    expect(hiddenInput.closest('.hidden')).toBeInTheDocument()
    // State should be preserved
    expect(hiddenInput.value).toBe('测试题干内容')

    // Switch back to manual mode
    fireEvent.click(screen.getByRole('button', { name: /手工录入题目/ }))

    // Input should be visible again with preserved value
    const restoredInput = screen.getByTestId('manual-input') as HTMLInputElement
    expect(restoredInput).toBeVisible()
    expect(restoredInput.value).toBe('测试题干内容')
  })

  it('lazy-mounts: mistake entry not in DOM until first activation', () => {
    const { container } = render(<CaptureContent />)

    // Initially only image mode is mounted
    expect(screen.getByTestId('capture-workspace')).toBeInTheDocument()
    expect(container.querySelector('[data-testid="mistake-entry"]')).toBeNull()

    // Switch to mistake mode
    fireEvent.click(screen.getByRole('button', { name: /从题库记录错题/ }))
    expect(screen.getByTestId('mistake-entry')).toBeVisible()

    // Switch back to image mode — mistake entry stays mounted but hidden
    fireEvent.click(screen.getByRole('button', { name: /上传图片/ }))
    expect(container.querySelector('[data-testid="mistake-entry"]')).toBeInTheDocument()
    expect(
      container.querySelector('[data-testid="mistake-entry"]')?.closest('.hidden'),
    ).toBeInTheDocument()
  })
})
