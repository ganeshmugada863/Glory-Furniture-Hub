import React from 'react'
import { useLocation } from 'react-router-dom'
import BottomNav from '../common/BottomNav'
import GloryAIFab from '../ai/GloryAIFab'
import GloryAIChatSheet from '../ai/GloryAIChatSheet'
import PwaInstallPrompt from '../common/PwaInstallPrompt'
import NavSidebarDrawer from '../common/NavSidebarDrawer'

export default function AppLayout({ children }) {
  const location = useLocation()
  const isAdminRoute = location.pathname.startsWith('/admin')

  // Dedicated clean container for Admin Console (No customer bot, no customer bottom nav)
  if (isAdminRoute) {
    return (
      <div className="min-h-screen bg-[#F4F6F8] text-walnut-900 selection:bg-gold-500 selection:text-white w-full overflow-x-hidden">
        {children}
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-cream-100 flex flex-col justify-between selection:bg-gold-500 selection:text-white relative pb-16 md:pb-0 w-full overflow-x-hidden">
      <main className="flex-1 w-full relative bg-cream-100 min-h-screen">
        {children}
      </main>
      <PwaInstallPrompt />
      <GloryAIFab />
      <GloryAIChatSheet />
      <NavSidebarDrawer />
      <BottomNav />
    </div>
  )
}
