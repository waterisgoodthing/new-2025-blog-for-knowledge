import { AuthGate } from '@/components/auth-gate'
import { ManageSidebar } from '../components/manage-sidebar'
import { ManageTopbar } from '../components/manage-topbar'
import { ManageMobileNav } from '../components/manage-mobile-nav'

export default function ManageWorkspaceLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <AuthGate>
      <div className='min-h-screen min-w-0 overflow-x-hidden px-4 py-6 sm:px-6 md:py-8 md:pl-20 lg:pr-10 lg:pl-24'>
        <div className='mx-auto flex max-w-7xl flex-col gap-4 md:flex-row md:gap-6'>
          <ManageSidebar />
          <section className='w-full min-w-0 flex-1 overflow-hidden rounded-[28px] border border-white/45 bg-white/48 p-5 shadow-[0_24px_90px_-46px_rgba(66,107,113,0.5)] backdrop-blur-xl sm:p-7 lg:p-9'>
            <ManageMobileNav />
            <ManageTopbar />
            <main className='pt-4 md:pt-8'>{children}</main>
          </section>
        </div>
      </div>
    </AuthGate>
  )
}
