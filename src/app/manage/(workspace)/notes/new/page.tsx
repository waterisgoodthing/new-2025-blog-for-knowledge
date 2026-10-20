'use client'

import { Suspense } from 'react'
import { useSearchParams } from 'next/navigation'
import { ContentEditor } from '../components/content-editor'

function NewNoteContent() {
	const params = useSearchParams()
	const type = params.get('type') === 'blog' ? 'blog' : 'note'
	return <ContentEditor mode='create' type={type} />
}

export default function NewNotePage() {
	return (
		<Suspense fallback={<p>加载中...</p>}>
			<NewNoteContent />
		</Suspense>
	)
}
