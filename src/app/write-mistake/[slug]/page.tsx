'use client'

import { useParams } from 'next/navigation'
import useSWR from 'swr'
import { getNote, type NoteDetail } from '@/lib/api/notes'
import { MistakeForm } from '../components/mistake-form'
import { EmptyState } from '@/components/empty-state'
import { AuthGate } from '@/components/auth-gate'

export default function EditMistakePage() {
	return (
		<AuthGate>
			<EditMistakeContent />
		</AuthGate>
	)
}

function EditMistakeContent() {
	const { slug } = useParams<{ slug: string }>()
	const { data: note, isLoading } = useSWR<NoteDetail>(
		slug ? `/api/notes/${slug}` : null,
		() => getNote(slug),
		{ revalidateOnFocus: false }
	)

	if (isLoading) return <div className='py-20 text-center text-gray-400'>加载中...</div>
	if (!note) return <div className='py-20'><EmptyState variant='load-error' title='未找到错题' description='该错题可能已被删除或链接无效' action={{ label: '返回错题集', href: '/mistakes' }} /></div>

	return <MistakeForm mode='edit' initialData={note} />
}
