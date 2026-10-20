'use client'

import { useEffect, useState } from 'react'
import { useParams } from 'next/navigation'
import { getNote, type NoteDetail } from '@/lib/api/notes'
import { EmptyState } from '@/components/empty-state'
import { ContentEditor } from '../components/content-editor'

export default function EditNotePage() {
	const { slug } = useParams<{ slug: string }>()
	const [note, setNote] = useState<NoteDetail | null>(null)
	const [failed, setFailed] = useState(false)
	useEffect(() => {
		getNote(slug)
			.then(setNote)
			.catch(() => setFailed(true))
	}, [slug])
	if (failed) return <EmptyState variant='load-error' />
	if (!note) return <p>加载中...</p>
	if (note.type !== 'note' && note.type !== 'blog') return <EmptyState variant='load-error' />
	return <ContentEditor mode='edit' type={note.type} initial={note} />
}
