'use client'

import { useState, useEffect, useCallback } from 'react'
import { getMe, type User } from '@/lib/api/auth'

interface UseAdminAuthReturn {
  user: User | null
  isAdmin: boolean
  authLevel: string | null
  loading: boolean
  refetch: () => Promise<void>
}

export function useAdminAuth(): UseAdminAuthReturn {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  const fetchUser = useCallback(async () => {
    try {
      const u = await getMe()
      setUser(u)
    } catch {
      setUser(null)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchUser()
  }, [fetchUser])

  return {
    user,
    isAdmin: user?.is_admin ?? false,
    authLevel: user?.auth_level ?? null,
    loading,
    refetch: fetchUser,
  }
}
