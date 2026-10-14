import { fireEvent, render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import {
	mockSettingsError,
	mockSettingsLoading,
	mockSettingsNormal,
} from '../../../mocks/ui-v2/settings-v2'
import { Uiv2SettingsSection } from './SettingsSection'

describe('Uiv2SettingsSection', () => {
	it('renders learning preferences with local editing and an honesty note', () => {
		render(<Uiv2SettingsSection model={mockSettingsNormal} />)
		expect(screen.getByRole('heading', { name: '设置' })).toBeInTheDocument()
		const goal = screen.getByLabelText('每日复习目标数量')
		expect(goal).toHaveValue(10)
		fireEvent.change(goal, { target: { value: '20' } })
		expect(goal).toHaveValue(20)

		const toggle = screen.getByLabelText('显示掌握度详情')
		expect(toggle).toBeChecked()
		fireEvent.click(toggle)
		expect(toggle).not.toBeChecked()

		fireEvent.click(screen.getByLabelText('紧凑'))
		expect(screen.getByLabelText('紧凑')).toBeChecked()

		expect(screen.getByText('偏好仅保存在当前视图，不修改账号与登录设置。')).toBeInTheDocument()
		// no auth controls: no password fields, no session/account forms
		expect(screen.queryByLabelText(/密码/)).not.toBeInTheDocument()
		expect(screen.queryByRole('button', { name: /登录|登出|退出登录/ })).not.toBeInTheDocument()
	})

	it('covers loading and error states', () => {
		const { rerender } = render(<Uiv2SettingsSection model={mockSettingsLoading} />)
		expect(screen.getByRole('status', { name: '正在加载学习设置' })).toBeInTheDocument()

		rerender(<Uiv2SettingsSection model={mockSettingsError} />)
		expect(screen.getByRole('alert')).toHaveTextContent('mock: 学习设置加载失败，请重试')
	})
})
