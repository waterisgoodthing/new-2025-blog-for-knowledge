'use client'

import { useEffect, useMemo, useState } from 'react'
import useSWR from 'swr'

import { getAdminProfile, updateAdminProfile, validateHomePreferences, type AdminProfile, type HomePreferences, type HomeSection } from '@/lib/api/admin-profile'
import { FeatureState } from '../../components/feature-state'
import { ManagePageHeader } from '../../components/manage-page-header'

const sections: Array<{ value: HomeSection; label: string }> = [
  { value: 'today', label: '今日任务' },
  { value: 'activity', label: '最近活动' },
  { value: 'stats', label: '内容统计' },
  { value: 'storage', label: '附件状态' },
]

type ProfileDraft = Omit<AdminProfile, 'id' | 'user_id'>

function toDraft(profile: AdminProfile): ProfileDraft {
  return {
    display_name: profile.display_name,
    identity_title: profile.identity_title,
    signature: profile.signature,
    welcome_message: profile.welcome_message,
    timezone: profile.timezone,
    home_preferences: {
      show_welcome: profile.home_preferences.show_welcome,
      section_order: [...profile.home_preferences.section_order],
      hidden_sections: [...profile.home_preferences.hidden_sections],
    },
  }
}

function updatePreferences(draft: ProfileDraft, next: Partial<HomePreferences>): ProfileDraft {
  return {
    ...draft,
    home_preferences: { ...draft.home_preferences, ...next },
  }
}

export function AdminProfileSettings() {
  const { data, error, isLoading, mutate } = useSWR('manage-admin-profile', getAdminProfile, { revalidateOnFocus: false })
  const [draft, setDraft] = useState<ProfileDraft | null>(null)
  const [isSaving, setIsSaving] = useState(false)
  const [saveError, setSaveError] = useState<string | null>(null)
  const [saved, setSaved] = useState(false)

  useEffect(() => {
    if (data) setDraft(toDraft(data))
  }, [data])

  const isDirty = useMemo(() => data && draft ? JSON.stringify(toDraft(data)) !== JSON.stringify(draft) : false, [data, draft])

  useEffect(() => {
    if (!isDirty) return
    const handleBeforeUnload = (event: BeforeUnloadEvent) => {
      event.preventDefault()
      event.returnValue = ''
    }
    window.addEventListener('beforeunload', handleBeforeUnload)
    return () => window.removeEventListener('beforeunload', handleBeforeUnload)
  }, [isDirty])

  const hiddenSet = useMemo(() => new Set(draft?.home_preferences.hidden_sections ?? []), [draft?.home_preferences.hidden_sections])

  if (isLoading || !draft) {
    if (error) {
      return <FeatureState state={{ kind: 'error', title: '私有设置加载失败', description: '请检查登录状态和服务状态后重试。', retry: () => void mutate() }} />
    }
    return <FeatureState state={{ kind: 'loading', label: '正在加载私有设置', rows: 5 }} />
  }

  const updateText = (key: keyof Omit<ProfileDraft, 'home_preferences'>, value: string) => {
    setSaved(false)
    setSaveError(null)
    setDraft(current => current ? { ...current, [key]: value } : current)
  }

  const toggleHiddenSection = (section: HomeSection, checked: boolean) => {
    const currentHidden = draft.home_preferences.hidden_sections
    const hidden_sections = checked
      ? [...currentHidden, section]
      : currentHidden.filter(item => item !== section)
    const nextPreferences = { ...draft.home_preferences, hidden_sections }
    const validationError = validateHomePreferences(nextPreferences)
    if (validationError) {
      setSaveError(validationError)
      return
    }
    setSaved(false)
    setSaveError(null)
    setDraft(current => current ? updatePreferences(current, { hidden_sections }) : current)
  }

  const reorderSection = (index: number, value: HomeSection) => {
    const order = [...draft.home_preferences.section_order]
    const currentIndex = order.indexOf(value)
    if (currentIndex < 0 || currentIndex === index) return
    ;[order[index], order[currentIndex]] = [order[currentIndex], order[index]]
    setSaved(false)
    setSaveError(null)
    setDraft(current => current ? updatePreferences(current, { section_order: order }) : current)
  }

  const handleReset = () => {
    if (data) {
      setDraft(toDraft(data))
      setSaveError(null)
      setSaved(false)
    }
  }

  const handleSave = async () => {
    setIsSaving(true)
    setSaveError(null)
    setSaved(false)
    try {
      const next = await updateAdminProfile(draft)
      setDraft(toDraft(next))
      await mutate(next, { revalidate: false })
      setSaved(true)
    } catch (err) {
      setSaveError(err instanceof Error ? err.message : '保存失败，请重试。')
    } finally {
      setIsSaving(false)
    }
  }

  return (
    <div className='space-y-8'>
      <ManagePageHeader
        eyebrow='系统设置'
        title='私有资料与首页偏好'
        description='这些内容只对当前管理员工作区生效，不会写入公开站点设置。'
      />

      <form className='space-y-8' onSubmit={event => { event.preventDefault(); void handleSave() }}>
        <section aria-labelledby='profile-fields-title' className='space-y-5'>
          <div className='border-b border-slate-200/70 pb-3'>
            <h2 id='profile-fields-title' className='font-semibold text-slate-900'>个人资料</h2>
            <p className='mt-1 text-sm text-slate-500'>用于管理工作区欢迎区域，不会出现在匿名公开页面。</p>
          </div>

          <div className='grid gap-5 md:grid-cols-2'>
            <label className='space-y-2 text-sm font-medium text-slate-700'>
              <span>显示名称</span>
              <input aria-label='显示名称' value={draft.display_name} onChange={event => updateText('display_name', event.target.value)} required maxLength={100} className='w-full rounded-xl border border-slate-200 bg-white/75 px-3 py-2.5 outline-none focus:border-[var(--color-brand)] focus:ring-2 focus:ring-[var(--color-brand)]/20' />
            </label>
            <label className='space-y-2 text-sm font-medium text-slate-700'>
              <span>身份标题</span>
              <input aria-label='身份标题' value={draft.identity_title} onChange={event => updateText('identity_title', event.target.value)} maxLength={100} className='w-full rounded-xl border border-slate-200 bg-white/75 px-3 py-2.5 outline-none focus:border-[var(--color-brand)] focus:ring-2 focus:ring-[var(--color-brand)]/20' />
            </label>
            <label className='space-y-2 text-sm font-medium text-slate-700 md:col-span-2'>
              <span>欢迎语</span>
              <input aria-label='欢迎语' value={draft.welcome_message} onChange={event => updateText('welcome_message', event.target.value)} maxLength={300} placeholder='例如：今天也继续积累一点。' className='w-full rounded-xl border border-slate-200 bg-white/75 px-3 py-2.5 outline-none focus:border-[var(--color-brand)] focus:ring-2 focus:ring-[var(--color-brand)]/20' />
            </label>
            <label className='space-y-2 text-sm font-medium text-slate-700 md:col-span-2'>
              <span>签名</span>
              <textarea aria-label='签名' value={draft.signature} onChange={event => updateText('signature', event.target.value)} maxLength={300} rows={3} className='w-full resize-y rounded-xl border border-slate-200 bg-white/75 px-3 py-2.5 outline-none focus:border-[var(--color-brand)] focus:ring-2 focus:ring-[var(--color-brand)]/20' />
            </label>
          </div>
        </section>

        <section aria-labelledby='time-preference-title' className='space-y-5'>
          <div className='border-b border-slate-200/70 pb-3'>
            <h2 id='time-preference-title' className='font-semibold text-slate-900'>时间与首页</h2>
            <p className='mt-1 text-sm text-slate-500'>使用 IANA 时区名称，例如 `Asia/Shanghai` 或 `UTC`。</p>
          </div>
          <label className='block max-w-md space-y-2 text-sm font-medium text-slate-700'>
            <span>时区</span>
            <input aria-label='时区' value={draft.timezone} onChange={event => updateText('timezone', event.target.value)} required maxLength={64} className='w-full rounded-xl border border-slate-200 bg-white/75 px-3 py-2.5 font-mono text-sm outline-none focus:border-[var(--color-brand)] focus:ring-2 focus:ring-[var(--color-brand)]/20' />
          </label>
          <label className='flex items-center gap-3 text-sm font-medium text-slate-700'>
            <input aria-label='显示欢迎区域' type='checkbox' checked={draft.home_preferences.show_welcome} onChange={event => { setSaved(false); setDraft(current => current ? updatePreferences(current, { show_welcome: event.target.checked }) : current) }} className='h-4 w-4 accent-[var(--color-brand)]' />
            显示欢迎区域
          </label>

          <div className='space-y-4'>
            <div>
              <h3 className='text-sm font-medium text-slate-700'>首页区块顺序</h3>
              <p className='mt-1 text-xs text-slate-500'>每个位置只能选择一个区块，保存后在 Dashboard 生效。</p>
            </div>
            <div className='grid gap-3 md:grid-cols-2'>
              {draft.home_preferences.section_order.map((section, index) => (
                <label key={index} className='space-y-2 text-sm text-slate-600'>
                  <span>第 {index + 1} 个区块</span>
                  <select aria-label={`第 ${index + 1} 个首页区块`} value={section} onChange={event => reorderSection(index, event.target.value as HomeSection)} className='w-full rounded-xl border border-slate-200 bg-white/75 px-3 py-2.5 outline-none focus:border-[var(--color-brand)] focus:ring-2 focus:ring-[var(--color-brand)]/20'>
                    {sections.map(option => <option key={option.value} value={option.value}>{option.label}</option>)}
                  </select>
                </label>
              ))}
            </div>
            <fieldset className='space-y-3'>
              <legend className='text-sm font-medium text-slate-700'>隐藏区块</legend>
              <div className='grid gap-3 sm:grid-cols-2'>
                {sections.map(section => (
                  <label key={section.value} className='flex items-center gap-3 text-sm text-slate-600'>
                    <input aria-label={`隐藏${section.label}`} type='checkbox' checked={hiddenSet.has(section.value)} onChange={event => toggleHiddenSection(section.value, event.target.checked)} className='h-4 w-4 accent-[var(--color-brand)]' />
                    {section.label}
                  </label>
                ))}
              </div>
            </fieldset>
          </div>
        </section>

        {saveError ? <p role='alert' className='rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700'>{saveError}</p> : null}
        {isDirty ? <p role='status' aria-label='有未保存修改' className='rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800'>有未保存修改，离开页面前请先保存或重置。</p> : null}
        {saved ? <p role='status' aria-label='设置已保存' className='rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700'>设置已保存</p> : null}
        <div className='flex flex-wrap gap-3 border-t border-slate-200/70 pt-5'>
          <button type='submit' disabled={isSaving} className='rounded-xl bg-[var(--color-brand)] px-5 py-2.5 text-sm font-medium text-white focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-brand)]/45 disabled:cursor-wait disabled:opacity-60'>{isSaving ? '保存中…' : '保存设置'}</button>
          <button type='button' onClick={handleReset} disabled={isSaving} className='rounded-xl border border-slate-200 bg-white/70 px-5 py-2.5 text-sm font-medium text-slate-700 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-brand)]/45 disabled:opacity-60'>重置未保存修改</button>
        </div>
      </form>
    </div>
  )
}
