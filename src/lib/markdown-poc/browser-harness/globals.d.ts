export type BrowserHarnessProps = {
	markdown: string
	mode: 'public' | 'admin-preview'
}

declare global {
	interface Window {
		__markdownPocBrowserHarness: {
			update(next: BrowserHarnessProps): void
			unmount(): void
		}
		__markdownPocBrowserInitial: BrowserHarnessProps
		__markdownPocObservedEvents: string[]
		__markdownPocXss: boolean
	}
}
