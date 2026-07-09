import { NextConfig } from 'next'
import { codeInspectorPlugin } from 'code-inspector-plugin'

const nextConfig: NextConfig = {
	devIndicators: false,
	reactStrictMode: false,
	reactCompiler: true,
	pageExtensions: ['ts', 'tsx', 'js', 'jsx', 'md', 'mdx'],
	experimental: {
		scrollRestoration: false
	},
	turbopack: {
		rules: {
			'*.svg': {
				loaders: ['@svgr/webpack'],
				as: '*.js'
			}
			// ...codeInspectorPlugin({
			// 	bundler: 'turbopack'
			// })
		},

		resolveExtensions: ['.mdx', '.tsx', '.ts', '.jsx', '.js', '.mjs', '.json', 'css']
	},
	webpack: config => {
		config.module.rules.push({
			test: /\.svg$/i,
			use: [{ loader: '@svgr/webpack', options: { svgo: false } }]
		})

		return config
	},

	async redirects() {
		return [
			{
				source: '/zh',
				destination: '/',
				permanent: true
			},
			{
				source: '/en',
				destination: '/',
				permanent: true
			},
			// Route Cutover: legacy write-* 与旧入口下线，统一重定向到 /manage/* 主线
			{ source: '/write-mistake', destination: '/manage/capture', permanent: false },
			{ source: '/write-mistake/:slug', destination: '/manage/mistakes', permanent: false },
			{ source: '/write-note', destination: '/manage/dashboard', permanent: false },
			{ source: '/write-note/:slug', destination: '/manage/dashboard', permanent: false },
			{ source: '/write', destination: '/manage/dashboard', permanent: false },
			{ source: '/write/:slug', destination: '/manage/dashboard', permanent: false },
			{ source: '/mistakes/review', destination: '/manage/review', permanent: false },
			{ source: '/mistakes', destination: '/manage/mistakes', permanent: false }
		]
	}
}

export default nextConfig
