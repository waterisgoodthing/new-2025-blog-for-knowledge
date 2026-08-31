'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAdminAuth } from '@/hooks/use-admin-auth'

export function AuthGate({ children }: { children: React.ReactNode }) {
  const { isAdmin, isLoading } = useAdminAuth({ mode: 'strict' })
  const router = useRouter()

  useEffect(() => {
    if (!isLoading && !isAdmin) {
      router.replace('/manage')
    }
  }, [isLoading, isAdmin, router])

  if (isLoading) {
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
