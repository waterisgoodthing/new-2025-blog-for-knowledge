'use client'

import { useState } from 'react'
import { toast } from 'sonner'
import { cn } from '@/lib/utils'

interface SecurityTabProps {
  authLevel?: string
}

export function SecurityTab({ authLevel }: SecurityTabProps) {
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [saving, setSaving] = useState(false)

  const handleSetPassword = async () => {
    if (newPassword.length < 6) {
      toast.error('密码至少需要6个字符')
      return
    }
    if (newPassword !== confirmPassword) {
      toast.error('两次输入的密码不一致')
      return
    }
    setSaving(true)
    try {
      const res = await fetch('/api/auth/set-password', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ password: newPassword }),
      })
      if (!res.ok) {
        const data = await res.json().catch(() => ({}))
        throw new Error(data.detail || `Error ${res.status}`)
      }
      toast.success('密码已更新')
      setNewPassword('')
      setConfirmPassword('')
    } catch (e: any) {
      toast.error('更新密码失败: ' + e.message)
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className='space-y-6'>
      <div className='rounded-2xl border border-white/40 bg-white/60 p-6 backdrop-blur-sm'>
        <h3 className='mb-4 font-medium'>认证状态</h3>
        <div className='flex items-center justify-between rounded-xl bg-white/40 p-4'>
          <div>
            <div className='font-medium'>当前认证方式</div>
            <div className='text-sm text-gray-500'>
              {authLevel === 'passkey' ? 'Passkey (最高权限)' : '密码 (普通权限)'}
            </div>
          </div>
          <span className={cn(
            'rounded-full px-3 py-1 text-xs',
            authLevel === 'passkey' ? 'bg-green-500/20 text-green-600' : 'bg-yellow-500/20 text-yellow-600'
          )}>
            {authLevel === 'passkey' ? '高级权限' : '普通权限'}
          </span>
        </div>
      </div>

      {authLevel === 'passkey' && (
        <div className='rounded-2xl border border-white/40 bg-white/60 p-6 backdrop-blur-sm'>
          <h3 className='mb-4 font-medium'>管理员密码</h3>
          <p className='mb-4 text-sm text-gray-500'>设置或更改管理员密码。密码认证可用于日常管理操作，但无法执行需要 Passkey 的敏感操作。</p>
          <div className='space-y-3'>
            <div>
              <label className='mb-1 block text-sm text-gray-500'>新密码</label>
              <input
                type='password'
                value={newPassword}
                onChange={e => setNewPassword(e.target.value)}
                placeholder='至少6个字符'
                className='w-full rounded-xl border border-white/40 bg-white/60 px-4 py-2.5 backdrop-blur-sm outline-none focus:border-[var(--color-brand)]'
              />
            </div>
            <div>
              <label className='mb-1 block text-sm text-gray-500'>确认密码</label>
              <input
                type='password'
                value={confirmPassword}
                onChange={e => setConfirmPassword(e.target.value)}
                placeholder='再次输入密码'
                className='w-full rounded-xl border border-white/40 bg-white/60 px-4 py-2.5 backdrop-blur-sm outline-none focus:border-[var(--color-brand)]'
              />
            </div>
            <button
              onClick={handleSetPassword}
              disabled={saving || !newPassword || newPassword.length < 6}
              className='rounded-xl bg-[var(--color-brand)] px-6 py-2.5 text-sm text-white disabled:opacity-50'
            >
              {saving ? '保存中...' : '更新密码'}
            </button>
          </div>
        </div>
      )}

      {authLevel !== 'passkey' && (
        <div className='rounded-2xl border border-yellow-200/40 bg-yellow-50/60 p-6 backdrop-blur-sm'>
          <h3 className='mb-2 font-medium text-yellow-800'>需要 Passkey 认证</h3>
          <p className='text-sm text-yellow-700'>密码更改和安全设置需要 Passkey 认证。请使用 Passkey 登录以获取完整安全权限。</p>
        </div>
      )}

      <div className='rounded-2xl border border-white/40 bg-white/60 p-6 backdrop-blur-sm'>
        <h3 className='mb-3 font-medium'>会话管理</h3>
        <p className='text-sm text-gray-500'>查看和管理活跃会话。注销会话将立即终止该会话的访问权限。</p>
        <button
          className='mt-3 rounded-lg bg-white/60 px-4 py-2 text-sm text-gray-600 hover:bg-white/80'
          onClick={async () => {
            try {
              const res = await fetch('/api/auth/sessions', { credentials: 'include' })
              if (res.ok) {
                const sessions = await res.json()
                toast.info(`活跃会话: ${sessions.length} 个`)
              }
            } catch {
              toast.error('获取会话失败')
            }
          }}
        >
          查看活跃会话
        </button>
      </div>
    </div>
  )
}
