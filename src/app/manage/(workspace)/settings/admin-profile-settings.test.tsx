import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const mutate = vi.fn()
let swrState: { data?: unknown; error?: unknown; isLoading: boolean; mutate: typeof mutate }

const updateAdminProfile = vi.fn()

vi.mock('swr', () => ({
  default: () => swrState,
}))

vi.mock('@/lib/api/admin-profile', () => ({
  getAdminProfile: vi.fn(),
  updateAdminProfile: (...args: unknown[]) => updateAdminProfile(...args),
  validateHomePreferences: (preferences: { hidden_sections: string[] }) => preferences.hidden_sections.includes('today') && preferences.hidden_sections.includes('activity') ? '至少保留一个学习行动区块（今日任务或最近活动）。' : null,
}))

const { AdminProfileSettings } = await import('./admin-profile-settings')

const profile = {
  id: 'profile-1',
  user_id: 'user-1',
  display_name: 'I5 Owner',
  identity_title: 'Learner',
  signature: 'Keep learning',
  welcome_message: '欢迎回来',
  timezone: 'Asia/Shanghai',
  home_preferences: {
    show_welcome: true,
    section_order: ['today', 'activity', 'stats', 'storage'],
    hidden_sections: [],
  },
}

describe('AdminProfileSettings', () => {
  beforeEach(() => {
    mutate.mockReset()
    updateAdminProfile.mockReset()
    swrState = { data: profile, isLoading: false, mutate }
    updateAdminProfile.mockResolvedValue(profile)
  })

  it('renders private profile fields and saves them with an explicit success state', async () => {
    render(<AdminProfileSettings />)

    expect(screen.getByRole('textbox', { name: '显示名称' })).toHaveValue('I5 Owner')
    fireEvent.change(screen.getByRole('textbox', { name: '欢迎语' }), { target: { value: '今天继续学习' } })
    expect(screen.getByRole('status', { name: '有未保存修改' })).toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: '保存设置' }))

    await waitFor(() => expect(updateAdminProfile).toHaveBeenCalledOnce())
    expect(updateAdminProfile.mock.calls[0][0]).toMatchObject({ welcome_message: '今天继续学习' })
    expect(await screen.findByRole('status', { name: '设置已保存' })).toBeInTheDocument()
  })

  it('keeps a retry state when the private profile request fails', () => {
    swrState = { error: new Error('offline'), isLoading: false, mutate }
    render(<AdminProfileSettings />)

    fireEvent.click(screen.getByRole('button', { name: '重新尝试' }))
    expect(mutate).toHaveBeenCalledOnce()
  })

  it('shows a labelled loading state', () => {
    swrState = { isLoading: true, mutate }
    render(<AdminProfileSettings />)

    expect(screen.getByRole('status', { name: '正在加载私有设置' })).toBeInTheDocument()
  })

  it('prevents hiding both learning action sections and saves reordered preferences', async () => {
    render(<AdminProfileSettings />)

    fireEvent.click(screen.getByRole('checkbox', { name: '隐藏今日任务' }))
    fireEvent.click(screen.getByRole('checkbox', { name: '隐藏最近活动' }))
    expect(screen.getByRole('alert')).toHaveTextContent('至少保留一个学习行动区块')

    fireEvent.change(screen.getByRole('combobox', { name: '第 1 个首页区块' }), { target: { value: 'activity' } })
    fireEvent.click(screen.getByRole('button', { name: '保存设置' }))

    await waitFor(() => expect(updateAdminProfile).toHaveBeenCalledOnce())
    expect(updateAdminProfile.mock.calls[0][0].home_preferences).toMatchObject({
      section_order: ['activity', 'today', 'stats', 'storage'],
      hidden_sections: ['today'],
    })
  })
})
