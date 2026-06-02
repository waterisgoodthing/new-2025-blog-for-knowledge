import { DiagramViewer } from '@/components/diagram-viewer'

type MarkdownImageProps = {
	src: string
	alt?: string
	title?: string
}

export function MarkdownImage({ src, alt = '', title = '' }: MarkdownImageProps) {
	return <DiagramViewer kind='image' src={src} alt={alt} title={title} />
}
