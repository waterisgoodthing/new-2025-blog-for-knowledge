import { apiFetch } from './client'

export type HomeSection = 'today' | 'activity' | 'stats' | 'storage'

export const HOME_SECTIONS: readonly HomeSection[] = ['today', 'activity', 'stats', 'storage']
export const LEARNING_ACTION_SECTIONS: readonly HomeSection[] = ['today', 'activity']
export const DEFAULT_HOME_PREFERENCES: HomePreferences = {
  show_welcome: true,
  section_order: [...HOME_SECTIONS],
  hidden_sections: [],
}

export interface HomePreferences {
  show_welcome: boolean
  section_order: HomeSection[]
  hidden_sections: HomeSection[]
}

export function validateHomePreferences(preferences: HomePreferences): string | null {
  if (preferences.section_order.length !== HOME_SECTIONS.length || new Set(preferences.section_order).size !== HOME_SECTIONS.length || !HOME_SECTIONS.every(section => preferences.section_order.includes(section))) {
    return '首页区块顺序必须包含每个支持的区块且不能重复。'
  }
  if (new Set(preferences.hidden_sections).size !== preferences.hidden_sections.length || preferences.hidden_sections.some(section => !HOME_SECTIONS.includes(section))) {
    return '隐藏区块包含无效或重复值。'
  }
  if (!LEARNING_ACTION_SECTIONS.some(section => !preferences.hidden_sections.includes(section))) {
    return '至少保留一个学习行动区块（今日任务或最近活动）。'
  }
  return null
}

export function normalizeHomePreferences(preferences?: Partial<HomePreferences>): HomePreferences {
  const candidate: HomePreferences = {
    show_welcome: preferences?.show_welcome ?? DEFAULT_HOME_PREFERENCES.show_welcome,
    section_order: preferences?.section_order ? [...preferences.section_order] : [...DEFAULT_HOME_PREFERENCES.section_order],
    hidden_sections: preferences?.hidden_sections ? [...preferences.hidden_sections] : [],
  }
  return validateHomePreferences(candidate) ? { ...DEFAULT_HOME_PREFERENCES, section_order: [...HOME_SECTIONS], hidden_sections: [] } : candidate
}

export interface AdminProfile {
  id: string
  user_id: string
  display_name: string
  identity_title: string
  signature: string
  welcome_message: string
  timezone: string
  home_preferences: HomePreferences
}

export async function getAdminProfile(): Promise<AdminProfile> {
  return apiFetch<AdminProfile>('/api/admin/profile')
}

export async function updateAdminProfile(payload: Omit<AdminProfile, 'id' | 'user_id'>): Promise<AdminProfile> {
  return apiFetch<AdminProfile>('/api/admin/profile', {
    method: 'PUT',
    body: JSON.stringify(payload),
  })
}
