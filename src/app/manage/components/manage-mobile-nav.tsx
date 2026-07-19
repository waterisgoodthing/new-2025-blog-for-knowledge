'use client'

import { useCallback, useEffect, useRef, useState } from 'react'
import { createPortal } from 'react-dom'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { Menu, X } from 'lucide-react'
import { navGroups, allItems } from './manage-sidebar'
import { cn } from '@/lib/utils'

function getCurrentPageLabel(pathname: string): string {
  const matched = allItems.find((item) => item.match(pathname))
  return matched?.label ?? ''
}

/** Focusable element selector for trap computation. */
const FOCUSABLE_SELECTOR =
  'a[href], button:not([disabled]), textarea, select, input, [tabindex]:not([tabindex="-1"])'

export function ManageMobileNav() {
  const pathname = usePathname()
  const [isOpen, setIsOpen] = useState(false)
  const menuButtonRef = useRef<HTMLButtonElement>(null)
  const drawerRef = useRef<HTMLDivElement>(null)
  const firstLinkRef = useRef<HTMLAnchorElement>(null)
  /** Elements that received inert while the drawer is open. */
  const inertedRef = useRef<HTMLElement[]>([])

  const currentPageLabel = getCurrentPageLabel(pathname)

  // Auto-close on route change
  useEffect(() => {
    setIsOpen(false)
  }, [pathname])

  // Close drawer, remove inert from all isolated elements, and restore focus to menu button
  const closeDrawer = useCallback(() => {
    inertedRef.current.forEach((el) => el.removeAttribute('inert'))
    inertedRef.current = []
    setIsOpen(false)
    menuButtonRef.current?.focus()
  }, [])

  // Escape key, focus trap, and background isolation
  useEffect(() => {
    if (!isOpen) return

    const drawer = drawerRef.current
    const dialog = drawer?.closest<HTMLElement>('[role="dialog"]') ?? null

    // At every ancestor level, isolate sibling branches that do not contain
    // the dialog. This also covers site-wide navigation outside the workspace.
    const inerted: HTMLElement[] = []
    if (dialog) {
      let activeBranch: HTMLElement = dialog
      let parent = activeBranch.parentElement

      while (parent) {
        for (const child of Array.from(parent.children)) {
          if (child === activeBranch) continue
          if (child.hasAttribute('inert')) continue
          child.setAttribute('inert', '')
          inerted.push(child as HTMLElement)
        }

        if (parent === document.body) break
        activeBranch = parent
        parent = parent.parentElement
      }
    }
    inertedRef.current = inerted

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        e.preventDefault()
        closeDrawer()
        return
      }

      if (e.key !== 'Tab' || !drawer) return

      const focusable = drawer.querySelectorAll<HTMLElement>(FOCUSABLE_SELECTOR)
      if (focusable.length === 0) return

      const first = focusable[0]
      const last = focusable[focusable.length - 1]
      const activeEl = document.activeElement

      if (e.shiftKey) {
        // Shift+Tab at first element or outside drawer → wrap to last
        if (activeEl === first || !drawer.contains(activeEl)) {
          e.preventDefault()
          last.focus()
        }
      } else {
        // Tab at last element or outside drawer → wrap to first
        if (activeEl === last || !drawer.contains(activeEl)) {
          e.preventDefault()
          first.focus()
        }
      }
    }

    document.addEventListener('keydown', handleKeyDown)
    // Focus first link when drawer opens
    requestAnimationFrame(() => {
      firstLinkRef.current?.focus()
    })

    return () => {
      document.removeEventListener('keydown', handleKeyDown)
      inertedRef.current.forEach((el) => el.removeAttribute('inert'))
      inertedRef.current = []
    }
  }, [isOpen, closeDrawer])

  // Prevent body scroll when drawer is open
  useEffect(() => {
    if (!isOpen) return
    const originalOverflow = document.body.style.overflow
    document.body.style.overflow = 'hidden'
    return () => {
      document.body.style.overflow = originalOverflow
    }
  }, [isOpen])

  let linkCount = 0

  return (
    <>
      {/* Mobile top bar with menu button */}
      <div
        className='flex items-center justify-between border-b border-white/45 pb-4 md:hidden'
      >
        <button
          ref={menuButtonRef}
          type='button'
          onClick={() => setIsOpen(true)}
          aria-label='打开导航菜单'
          aria-expanded={isOpen}
          aria-controls='mobile-nav-drawer'
          className='inline-flex h-9 w-9 items-center justify-center rounded-lg bg-white/55 text-slate-600 transition-colors hover:bg-white/80 hover:text-slate-900 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-brand)]/45'
        >
          <Menu className='h-4 w-4' aria-hidden='true' />
        </button>
        <p className='text-sm font-medium text-slate-700'>
          {currentPageLabel || '学习管理'}
        </p>
        <Link
          href='/'
          aria-label='返回公开首页'
          className='inline-flex h-9 w-9 items-center justify-center rounded-lg bg-white/55 text-slate-600 transition-colors hover:bg-white/80 hover:text-slate-900 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-brand)]/45'
        >
          <span className='text-xs'>首页</span>
        </Link>
      </div>

      {/* Drawer overlay */}
      {isOpen
        ? createPortal(
          <div
          className='fixed inset-0 z-50 md:hidden'
          role='dialog'
          aria-modal='true'
          aria-label='导航菜单'
        >
          {/* Backdrop */}
          <div
            className='absolute inset-0 bg-slate-900/30 backdrop-blur-sm'
            onClick={closeDrawer}
            aria-hidden='true'
          />

          {/* Drawer panel */}
          <div
            ref={drawerRef}
            id='mobile-nav-drawer'
            className='absolute left-0 top-0 flex h-full w-72 max-w-[80vw] flex-col overflow-y-auto rounded-r-2xl border-r border-white/45 bg-white/95 shadow-2xl backdrop-blur-xl'
          >
            {/* Drawer header */}
            <div className='flex items-center justify-between border-b border-slate-100 px-4 py-3'>
              <p className='text-sm font-semibold text-slate-800'>导航</p>
              <button
                type='button'
                onClick={closeDrawer}
                aria-label='关闭导航菜单'
                className='inline-flex h-8 w-8 items-center justify-center rounded-lg text-slate-400 transition-colors hover:bg-slate-100 hover:text-slate-700 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-brand)]/45'
              >
                <X className='h-4 w-4' aria-hidden='true' />
              </button>
            </div>

            {/* Grouped navigation */}
            <nav className='flex flex-col gap-4 p-3' aria-label='移动端导航'>
              {navGroups.map((group) => {
                return (
                  <div key={group.title} className='flex flex-col gap-1.5'>
                    <p className='px-3 text-xs font-medium tracking-wide text-slate-400'>
                      {group.title}
                    </p>
                    {group.items.map(({ href, label, icon: Icon, match, status }) => {
                      const active = match(pathname)
                      linkCount++
                      const isFirst = linkCount === 1
                      return (
                        <Link
                          key={href}
                          ref={isFirst ? firstLinkRef : undefined}
                          href={href}
                          aria-current={active ? 'page' : undefined}
                          className={cn(
                            'group flex w-full items-center gap-2 rounded-2xl px-3 py-2.5 text-sm transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-brand)]/45',
                            active
                              ? 'bg-[var(--color-brand)]/14 font-medium text-[var(--color-brand)]'
                              : 'text-slate-500 hover:bg-white/65 hover:text-slate-800',
                          )}
                        >
                          <Icon className='h-4 w-4 shrink-0' aria-hidden='true' />
                          <span className='min-w-0 flex-1'>{label}</span>
                          {status === 'deferred' ? (
                            <span className='text-[10px] text-slate-400'>后续</span>
                          ) : null}
                        </Link>
                      )
                    })}
                  </div>
                )
              })}
            </nav>
          </div>
          </div>,
          document.body,
        )
        : null}
    </>
  )
}
