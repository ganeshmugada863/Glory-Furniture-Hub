import React from 'react'
import { Sparkles } from 'lucide-react'
import { useLocation } from 'react-router-dom'
import { useAppStore } from '../../store/useAppStore'

export default function GloryAIFab() {
  const location = useLocation()
  const openAIChat = useAppStore(state => state.openAIChat)

  // Hide FAB on onboarding / auth screens
  const hiddenRoutes = ['/', '/onboarding', '/login', '/register', '/forgot-password']
  if (hiddenRoutes.includes(location.pathname) || location.pathname.startsWith('/admin')) {
    return null
  }

  return (
    <button
      onClick={() => openAIChat()}
      className="fixed bottom-20 right-4 z-40 flex items-center gap-2 bg-gradient-to-r from-walnut-500 to-walnut-700 text-gold-400 font-sans font-semibold text-xs py-3 px-4 rounded-full shadow-warm-lg hover:shadow-2xl hover:scale-105 active-tap transition-all ring-2 ring-gold-500/30"
      aria-label="Ask GloryAI Assistant"
    >
      <div className="relative">
        <Sparkles className="w-4 h-4 text-gold-400 animate-spin-slow" />
        <span className="absolute -top-1 -right-1 w-2 h-2 bg-gold-400 rounded-full animate-ping" />
      </div>
      <span className="tracking-wide text-white">GloryAI</span>
    </button>
  )
}
