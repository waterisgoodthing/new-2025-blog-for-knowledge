'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAdminAuth } from '@/hooks/use-admin-auth'

export function AuthGate({ children }: { children: React.ReactNode }) {
  const { isAdmin, loading } = useAdminAuth()
  const router = useRouter()

  useEffect(() => {
    if (!loading && !isAdmin) {
      router.replace('/manage')
    }
  }, [loading, isAdmin, router])

  if (loading) {
    return (
      <div className='flex h-screen items-center justify-center'>
        <div className='text-gray-400'>验证中...</div>
      </div>
    )
  }

  if (!isAdmin) {
    return null
  }

  return <>{children}</>
}
