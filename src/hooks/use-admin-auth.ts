'use client'

import useSWR, { mutate } from 'swr'
import { getMe, getSessionState } from '@/lib/api/auth'

export const OPTIONAL_ADMIN_SESSION_KEY = 'admin-session-check:optional'
export const STRICT_ADMIN_SESSION_KEY = 'admin-session-check:strict'

export type AdminAuthMode = 'optional' | 'strict'

export function useAdminAuth({ mode = 'strict' }: { mode?: AdminAuthMode } = {}) {
	const strict = mode === 'strict'
	const { data, error, isLoading } = useSWR(
		strict ? STRICT_ADMIN_SESSION_KEY : OPTIONAL_ADMIN_SESSION_KEY,
		async () => {
			if (strict) {
				const user = await getMe()
				return user.is_admin === true
			}
			const session = await getSessionState()
			return session.is_admin === true
		},
		{
			revalidateOnFocus: strict,
			revalidateOnReconnect: strict,
			dedupingInterval: strict ? 32 : 60000
		}
	)

	return {
		isAdmin: data ?? false,
		isLoading,
		error
	}
}

export async function invalidateAdminAuthState(): Promise<void> {
	await Promise.all([mutate(OPTIONAL_ADMIN_SESSION_KEY).catch(() => undefined), mutate(STRICT_ADMIN_SESSION_KEY).catch(() => undefined)])
}
