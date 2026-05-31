'use client'

import useSWR from 'swr'
import { listCategories } from '@/lib/api/meta'

export function useCategories() {
	const { data, error, isLoading } = useSWR(
		'/api/categories',
		() => listCategories(),
		{
			revalidateOnFocus: false,
			revalidateOnReconnect: true
		}
	)

	return {
		categories: data?.map(c => c.name) ?? [],
		loading: isLoading,
		error
	}
}
