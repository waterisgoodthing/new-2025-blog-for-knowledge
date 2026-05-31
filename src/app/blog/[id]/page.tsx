'use client'

import dynamic from 'next/dynamic'

const BlogDetailContent = dynamic(() => import('./blog-detail-content'), { ssr: false })

export default function Page() {
	return <BlogDetailContent />
}
