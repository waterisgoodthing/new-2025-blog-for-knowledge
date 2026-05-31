'use client'

import { useEffect, useState, useRef, type ReactElement, Fragment } from 'react'
import { renderMarkdown, type TocItem } from '@/lib/markdown-renderer'
import { MarkdownImage } from '@/components/markdown-image'
import { CodeBlock } from '@/components/code-block'
import { MermaidBlock } from '@/components/mermaid-block'

let parseModule: typeof import('html-react-parser') | null = null

async function loadParser() {
	if (parseModule) return parseModule
	const mod = await import('html-react-parser')
	parseModule = mod
	return mod
}

type MarkdownRenderResult = {
	content: ReactElement | null
	toc: TocItem[]
	loading: boolean
}

export function useMarkdownRender(markdown: string, debounceMs = 300): MarkdownRenderResult {
	const [content, setContent] = useState<ReactElement | null>(null)
	const [toc, setToc] = useState<TocItem[]>([])
	const [loading, setLoading] = useState<boolean>(true)
	const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null)
	const latestMarkdown = useRef(markdown)
	latestMarkdown.current = markdown

	useEffect(() => {
		let cancelled = false

		if (timerRef.current) clearTimeout(timerRef.current)
		timerRef.current = setTimeout(async () => {
			const md = latestMarkdown.current
			setLoading(true)
			try {
				const [{ html, toc }, parseMod] = await Promise.all([renderMarkdown(md), loadParser()])
				const parse = parseMod.default
				if (cancelled || md !== latestMarkdown.current) return

				const codeBlocks: Array<{ placeholder: string; code: string; preHtml: string }> = []
				const mathBlocks: Array<{ placeholder: string; tag: string; html: string }> = []
				let processedHtml = html.replace(/<div class="ag-code-block" data-code="([^"]*)">([\s\S]*?)<\/div><!--ag-code-block-end-->/g, (match, codeAttr, content) => {
					const placeholder = `__CODE_BLOCK_${codeBlocks.length}__`
					const code = codeAttr
						.replace(/&quot;/g, '"')
						.replace(/&#39;/g, "'")
						.replace(/&lt;/g, '<')
						.replace(/&gt;/g, '>')
						.replace(/&amp;/g, '&')
					codeBlocks.push({
						placeholder,
						code,
						preHtml: content.trim()
					})
					return placeholder
				})

				processedHtml = processedHtml.replace(/<(div|span) class="ag-math-container"><!--ag-math-start-->([\s\S]*?)<!--ag-math-end--><\/\1>/g, (match, tag, mathHtml) => {
					const placeholder = `__MATH_BLOCK_${mathBlocks.length}__`
					mathBlocks.push({ placeholder, tag, html: mathHtml })
					return placeholder
				})

				const options = {
					replace(domNode: any) {
						if (domNode instanceof parseMod.Element && domNode.name === 'img') {
							const { src, alt, title } = domNode.attribs
							return <MarkdownImage src={src} alt={alt} title={title} />
						}
						if (domNode instanceof parseMod.Element && domNode.name === 'div' && domNode.attribs?.class?.includes('mermaid')) {
							const code = (domNode.children?.[0] as any)?.data || ''
							const decoded = code
								.replace(/&amp;/g, '&')
								.replace(/&lt;/g, '<')
								.replace(/&gt;/g, '>')
								.replace(/&quot;/g, '"')
								.replace(/&#39;/g, "'")
							return <MermaidBlock code={decoded} />
						}
						if (domNode.type === 'text' && domNode.data) {
							const text = domNode.data
							if (text.includes('__CODE_BLOCK_') || text.includes('__MATH_BLOCK_')) {
								const result = text
									.split(/(__(?:CODE|MATH)_BLOCK_\d+__)/)
									.filter(Boolean)

								return (
									<>
										{result.map((item, index) => {
											if (item.startsWith('__CODE_BLOCK_')) {
												const block = codeBlocks.find(b => b.placeholder === item)
												if (block) {
													if (block.preHtml.includes('class="mermaid"')) {
														return <MermaidBlock key={block.placeholder} code={block.code} />
													}
													const preElement = parse(block.preHtml) as ReactElement
													return (
														<CodeBlock key={block.placeholder} code={block.code}>{preElement}</CodeBlock>
													)
												}
											} else if (item.startsWith('__MATH_BLOCK_')) {
												const block = mathBlocks.find(b => b.placeholder === item)
												if (block) {
													const Tag = block.tag as any
													return <Tag key={block.placeholder} className="ag-math" dangerouslySetInnerHTML={{ __html: block.html }} />
												}
											}
											return item ? <Fragment key={index}>{item}</Fragment> : null
										})}
									</>
								)
							}
						}
					}
				}
				const reactContent = parse(processedHtml, options) as ReactElement
				if (cancelled) return
				setContent(reactContent)
				setToc(toc)
			} catch (error) {
				console.error('Markdown render error:', error)
				if (!cancelled) {
					setContent(null)
					setToc([])
				}
			} finally {
				if (!cancelled) {
					setLoading(false)
				}
			}
		}, debounceMs)

		return () => {
			cancelled = true
			if (timerRef.current) clearTimeout(timerRef.current)
		}
	}, [markdown, debounceMs])

	return { content, toc, loading }
}
