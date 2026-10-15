/**
 * M3 jsdom DOM 安全合同 — DOM-level safety assertions via jsdom.
 *
 * jsdom 不执行脚本、不渲染 SVG、不模拟真实浏览器事件分发。
 * 本测试只能验证 HTML 字符串结构层面的安全合同：
 *   - 危险标签（script、iframe、svg）不出现在输出中
 *   - 事件处理器属性（onerror、onload 等）不出现在输出中
 *   - 危险协议（javascript:、vbscript:、data:）不出现在 href/src 中
 *   - 安全内容存在（非真空断言，stub 下产生红灯）
 *
 * 真实浏览器 SVG/Canvas/事件/导航执行验证推迟到 M5/M6。
 * G2 是硬门：没有真实浏览器证据不得给 GO。
 */

import { describe, it, expect } from 'vitest'
import { renderMarkdownPoC } from '../render-poc'
import { markdownFixtures } from '../fixtures'
import { hasDangerousUrlAttribute, hasEventHandlerAttribute, hasLiveElement } from './dom-contract'

// ---------------------------------------------------------------------------
// 危险标签检查 — 所有 security fixture 的输出不得包含危险标签
// ---------------------------------------------------------------------------

describe('jsdom DOM 安全合同: dangerous tags are absent in output HTML', () => {
	const attackFixtures = markdownFixtures.filter(f => f.markdown.includes('__markdownPocXss') || f.markdown.includes('onerror'))

	for (const fixture of attackFixtures) {
		it(`fixture "${fixture.id}": no <script> element in output`, () => {
			const result = renderMarkdownPoC(fixture.markdown, { mode: fixture.mode })
			expect(hasLiveElement(result.html, 'script')).toBe(false)
		})

		it(`fixture "${fixture.id}": no event handler attributes in output`, () => {
			const result = renderMarkdownPoC(fixture.markdown, { mode: fixture.mode })
			expect(hasEventHandlerAttribute(result.html)).toBe(false)
		})
	}
})

describe('jsdom DOM 安全合同: dangerous navigation protocols are blocked', () => {
	const linkFixtures = markdownFixtures.filter(f => f.markdown.includes('javascript:') || f.markdown.includes('vbscript:'))

	for (const fixture of linkFixtures) {
		it(`fixture "${fixture.id}": no dangerous protocol in href/src`, () => {
			const result = renderMarkdownPoC(fixture.markdown, { mode: fixture.mode })
			expect(hasDangerousUrlAttribute(result.html)).toBe(false)
		})
	}
})

describe('jsdom DOM 安全合同: all security fixtures produce structurally safe HTML', () => {
	const securityFixtures = markdownFixtures.filter(f => f.id.startsWith('security-'))

	for (const fixture of securityFixtures) {
		it(`fixture "${fixture.id}": no script, iframe, svg, or event handlers in HTML`, () => {
			const result = renderMarkdownPoC(fixture.markdown, { mode: fixture.mode })
			expect(hasLiveElement(result.html, 'script')).toBe(false)
			expect(hasLiveElement(result.html, 'iframe')).toBe(false)
			expect(hasLiveElement(result.html, 'svg')).toBe(false)
			expect(hasEventHandlerAttribute(result.html)).toBe(false)
			expect(hasDangerousUrlAttribute(result.html)).toBe(false)
		})
	}
})

describe('jsdom DOM 安全合同: special renderer output is inert in HTML structure', () => {
	const specialMalicious = markdownFixtures.filter(
		f => f.id.startsWith('special-') && (f.id.includes('malicious') || f.id.includes('malformed') || f.id.includes('invalid'))
	)

	for (const fixture of specialMalicious) {
		it(`fixture "${fixture.id}": no script/event/dangerous-protocol in HTML`, () => {
			const result = renderMarkdownPoC(fixture.markdown, { mode: fixture.mode })
			expect(hasLiveElement(result.html, 'script')).toBe(false)
			expect(hasEventHandlerAttribute(result.html)).toBe(false)
			expect(hasDangerousUrlAttribute(result.html)).toBe(false)
		})
	}
})

// ---------------------------------------------------------------------------
// 非真空断言 — stub 空输出必须导致红灯
// ---------------------------------------------------------------------------

describe('jsdom DOM 安全合同: non-vacuum safety sentinel (red for stub)', () => {
	// The stub returns empty html.  These tests assert that secure, semantic
	// content MUST exist in the output.  Empty output = RED (expected failure
	// until M4–M6 implement real bounded parsing).
	//
	// jsdom 只验证 HTML 字符串结构，不证明真实浏览器执行。
	// 真实浏览器 SVG/Canvas/事件/导航验证推迟到 M5/M6。

	it('semantic fixture output is non-empty', () => {
		const fixture = markdownFixtures.find(f => f.id === 'semantic-headings-stable-toc')!
		const result = renderMarkdownPoC(fixture.markdown, { mode: fixture.mode })
		expect(result.html.length).toBeGreaterThan(0)
		expect(result.html).toContain('安全标题')
	})

	it('semantic fixture TOC is non-empty', () => {
		const fixture = markdownFixtures.find(f => f.id === 'semantic-headings-stable-toc')!
		const result = renderMarkdownPoC(fixture.markdown, { mode: fixture.mode })
		expect(result.toc.length).toBeGreaterThan(0)
	})

	it('safe link fixture output contains expected content', () => {
		const fixture = markdownFixtures.find(f => f.id === 'semantic-safe-links-relative-anchor-mail')!
		const result = renderMarkdownPoC(fixture.markdown, { mode: fixture.mode })
		expect(result.html.length).toBeGreaterThan(0)
		expect(result.html).toContain('https://example.test/docs')
	})

	it('code fixture output is non-empty and contains inert code text', () => {
		const fixture = markdownFixtures.find(f => f.id === 'special-code-valid')!
		const result = renderMarkdownPoC(fixture.markdown, { mode: fixture.mode })
		expect(result.html.length).toBeGreaterThan(0)
		expect(result.html).toContain('console.log')
	})

	it('code fixture hostile text is present but inert', () => {
		const fixture = markdownFixtures.find(f => f.id === 'special-code-hostile-text-is-inert')!
		const result = renderMarkdownPoC(fixture.markdown, { mode: fixture.mode })
		expect(result.html.length).toBeGreaterThan(0)
		expect(result.html).toContain('window.__markdownPocXss')
		// The script tag text must appear as escaped text, NOT as a live element
		expect(hasLiveElement(result.html, 'script')).toBe(false)
	})

	it('security-malformed-local-fallback preserves safe heading', () => {
		const fixture = markdownFixtures.find(f => f.id === 'security-malformed-local-fallback')!
		const result = renderMarkdownPoC(fixture.markdown, { mode: fixture.mode })
		expect(result.html).toContain('Keep this heading')
		expect(result.html.length).toBeGreaterThan(0)
	})
})
