'use client'

import useSWR from 'swr'
import { getMe } from '@/lib/api/auth'

export function useAdminAuth() {
	const { data, error, isLoading } = useSWR(
		'admin-session-check',
		async () => {
			try {
				const user = await getMe()
				return user.is_admin === true
			} catch {
				return false
			}
		},
		{
			revalidateOnFocus: false,
			revalidateOnReconnect: false,
			dedupingInterval: 60000,
		}
	)

	return {
		isAdmin: data ?? false,
		isLoading,
	}
}
