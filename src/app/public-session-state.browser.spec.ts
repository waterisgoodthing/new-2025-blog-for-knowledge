import { expect, test } from '@playwright/test'

const apiBase = 'http://127.0.0.1:8001'
const publicNotes = { items: [], total: 0, page: 1, size: 100 }
const publicBlogDetail = {
	id: '00000000-0000-0000-0000-000000000101',
	slug: 'pss-public-blog',
	title: 'PSS public blog detail',
	type: 'blog',
	status: 'published',
	hidden: false,
	created_at: '2026-08-16T00:00:00Z',
	updated_at: '2026-08-16T00:00:00Z',
	tags: [],
	sort_order: 0,
	revision: 1,
	summary: 'Deterministic public blog detail fixture.',
	content: '# PSS public blog detail\n\nDeterministic anonymous content.'
}
const publicNoteDetail = {
	id: '00000000-0000-0000-0000-000000000102',
	slug: 'pss-public-note',
	title: 'PSS public note detail',
	type: 'note',
	status: 'published',
	hidden: false,
	created_at: '2026-08-16T00:00:00Z',
	updated_at: '2026-08-16T00:00:00Z',
	tags: [],
	sort_order: 0,
	revision: 1,
	content: '# PSS public note detail\n\nDeterministic anonymous note content.'
}
const publicSiteSettings = {
	siteContent: {
		meta: { title: 'PSS isolated browser', description: '', username: '' },
		theme: {},
		backgroundColors: [],
		artImages: [],
		currentArtImageId: '',
		backgroundImages: [],
		currentBackgroundImageId: '',
		socialButtons: [],
		clockShowSeconds: false,
		summaryInContent: false,
		isCachePem: false,
		hideEditButton: false,
		enableCategories: false,
		currentHatIndex: 0,
		hatFlipped: false,
		enableChristmas: false,
		beian: { text: '', link: '' }
	},
	cardStyles: {
		musicCard: { width: 280, height: 96, offsetX: null, offsetY: null, offset: 0 },
		hiCard: { width: 320, height: 160 },
		clockCard: { offset: 0 },
		calendarCard: { height: 160 }
	}
}

async function installPublicDataRoutes(page: import('@playwright/test').Page) {
	await page.route(`${apiBase}/api/content/site-settings`, route =>
		route.fulfill({ contentType: 'application/json', body: JSON.stringify(publicSiteSettings) })
	)
	await page.route(`${apiBase}/api/notes**`, route => {
		const { pathname } = new URL(route.request().url())
		const body = pathname === '/api/notes/pss-public-blog' ? publicBlogDetail : pathname === '/api/notes/pss-public-note' ? publicNoteDetail : publicNotes
		return route.fulfill({ contentType: 'application/json', body: JSON.stringify(body) })
	})
	await page.route(`${apiBase}/api/categories`, route => route.fulfill({ contentType: 'application/json', body: '[]' }))
	await page.route(`${apiBase}/api/tags`, route => route.fulfill({ contentType: 'application/json', body: '[]' }))
	await page.route(`${apiBase}/api/auth/passkey/status`, route =>
		route.fulfill({ contentType: 'application/json', body: JSON.stringify({ registered: false }) })
	)
}

function isAdministratorNoise(url: string): boolean {
	return /\/api\/(folders|review|admin|ai|attachments)/.test(url)
}

test.describe.serial('public session-state browser acceptance', () => {
	test('anonymous public blog detail remains readable with the mounted mobile navigation and no administrator side effects', async ({ browser }) => {
		const context = await browser.newContext({
			viewport: { width: 390, height: 844 },
			isMobile: true
		})
		const page = await context.newPage()
		const requests: string[] = []
		const pageErrors: Error[] = []
		const serverFailures: string[] = []
		const dialogs: string[] = []
		const downloads: string[] = []
		let postLoadNavigations = 0
		let loaded = false

		await installPublicDataRoutes(page)
		page.on('request', request => requests.push(request.url()))
		page.on('pageerror', error => pageErrors.push(error))
		page.on('response', response => {
			if (response.url().startsWith(apiBase) && response.status() >= 500) {
				serverFailures.push(`${response.status()} ${response.url()}`)
			}
		})
		page.on('dialog', dialog => {
			dialogs.push(dialog.type())
			void dialog.dismiss()
		})
		page.on('download', download => downloads.push(download.suggestedFilename()))
		page.on('framenavigated', frame => {
			if (loaded && frame === page.mainFrame()) postLoadNavigations += 1
		})

		await page.goto('/blog/pss-public-blog')
		await expect(page.getByRole('heading', { name: 'PSS public blog detail' })).toBeVisible()
		const mobileNavigation = page.getByRole('navigation', { name: '主要导航' })
		await expect(mobileNavigation).toBeVisible()
		await expect(mobileNavigation.getByRole('link', { name: '博客', exact: true })).toBeVisible()
		await expect(page.getByRole('link', { name: '管理' })).toHaveCount(0)
		loaded = true
		await page.waitForTimeout(150)

		expect(requests.filter(url => url.includes('/api/auth/me'))).toEqual([])
		expect(requests.filter(isAdministratorNoise)).toEqual([])
		expect(pageErrors).toEqual([])
		expect(serverFailures).toEqual([])
		expect(dialogs).toEqual([])
		expect(downloads).toEqual([])
		expect(postLoadNavigations).toBe(0)
		await context.close()
	})

	test('anonymous public note detail remains readable without strict or administrator side effects', async ({ page }) => {
		const requests: string[] = []
		const pageErrors: Error[] = []
		const serverFailures: string[] = []
		const dialogs: string[] = []
		const downloads: string[] = []
		let postLoadNavigations = 0
		let loaded = false

		await installPublicDataRoutes(page)
		page.on('request', request => requests.push(request.url()))
		page.on('pageerror', error => pageErrors.push(error))
		page.on('response', response => {
			if (response.url().startsWith(apiBase) && response.status() >= 500) {
				serverFailures.push(`${response.status()} ${response.url()}`)
			}
		})
		page.on('dialog', dialog => {
			dialogs.push(dialog.type())
			void dialog.dismiss()
		})
		page.on('download', download => downloads.push(download.suggestedFilename()))
		page.on('framenavigated', frame => {
			if (loaded && frame === page.mainFrame()) postLoadNavigations += 1
		})

		await page.goto('/notes/pss-public-note')
		await expect(page.getByRole('heading', { name: 'PSS public note detail' })).toBeVisible()
		await expect(page.getByRole('link', { name: '编辑' })).toHaveCount(0)
		loaded = true
		await page.waitForTimeout(150)

		expect(requests.filter(url => url.includes('/api/auth/me'))).toEqual([])
		expect(requests.filter(isAdministratorNoise)).toEqual([])
		expect(pageErrors).toEqual([])
		expect(serverFailures).toEqual([])
		expect(dialogs).toEqual([])
		expect(downloads).toEqual([])
		expect(postLoadNavigations).toBe(0)
	})

	test('anonymous public pages keep content visible without strict or administrator API requests', async ({ page }) => {
		const requests: string[] = []
		const pageErrors: Error[] = []
		await installPublicDataRoutes(page)
		page.on('request', request => requests.push(request.url()))
		page.on('pageerror', error => pageErrors.push(error))

		for (const pathname of ['/blog', '/notes', '/mistakes']) {
			const sessionRequestsBeforeNavigation = requests.filter(url => url.includes('/api/auth/session-state')).length
			await page.goto(pathname)
			await expect(page.locator('body')).not.toBeEmpty()
			await page.waitForTimeout(150)
			expect(requests.filter(url => url.includes('/api/auth/session-state')).length - sessionRequestsBeforeNavigation).toBe(1)
		}

		expect(requests.filter(url => url.includes('/api/auth/me'))).toEqual([])
		expect(requests.filter(isAdministratorNoise)).toEqual([])
		expect(pageErrors).toEqual([])
	})

	test('valid administrator session enables display state and logout returns to anonymous state', async ({ browser }) => {
		const context = await browser.newContext()
		await context.addCookies([
			{
				name: 'admin_session',
				value: 'pss-browser-admin',
				url: `${apiBase}/api`
			}
		])
		const page = await context.newPage()
		const requests: string[] = []
		await installPublicDataRoutes(page)
		page.on('request', request => requests.push(request.url()))

		await page.goto('/blog')
		await expect(page.getByRole('button', { name: '编辑' })).toBeVisible()
		expect(requests.filter(url => url.includes('/api/auth/me'))).toEqual([])

		await page.request.post(`${apiBase}/api/auth/logout`)
		await page.reload()
		await expect(page.getByRole('button', { name: '编辑' })).toHaveCount(0)
		await context.close()
	})

	test('expired synthetic session safely resolves as anonymous while strict management remains protected', async ({ browser }) => {
		const context = await browser.newContext()
		await context.addCookies([
			{
				name: 'admin_session',
				value: 'pss-browser-expired',
				url: `${apiBase}/api`
			}
		])
		const page = await context.newPage()
		const serverFailures: string[] = []
		await installPublicDataRoutes(page)
		page.on('response', response => {
			if (response.url().startsWith(apiBase) && response.status() >= 500) {
				serverFailures.push(`${response.status()} ${response.url()}`)
			}
		})

		await page.goto('/blog')
		await expect(page.getByRole('button', { name: '编辑' })).toHaveCount(0)
		const strict = await page.request.get(`${apiBase}/api/auth/me`)
		expect(strict.status()).toBe(401)

		await page.goto('/manage')
		await expect(page.getByRole('button', { name: '密码登录' })).toBeVisible()
		expect(serverFailures).toEqual([])
		await context.close()
	})
})
