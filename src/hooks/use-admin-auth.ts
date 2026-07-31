'use client'

import useSWR from 'swr'
import { getMe } from '@/lib/api/auth'

export function useAdminAuth({ strict = false }: { strict?: boolean } = {}) {
	const { data, error, isLoading } = useSWR(
		strict ? 'admin-session-check:strict' : 'admin-session-check',
		async () => {
			try {
				const user = await getMe()
				return user.is_admin === true
			} catch {
				return false
			}
		},
		{
			revalidateOnFocus: strict,
			revalidateOnReconnect: strict,
			dedupingInterval: strict ? 32 : 60000,
		}
	)

	return {
		isAdmin: data ?? false,
		isLoading,
	}
}
