import React, { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAppStore } from '../store/useAppStore'
import { Sparkles } from 'lucide-react'

export default function SplashScreen() {
  const navigate = useNavigate()
  const { user } = useAppStore()

  useEffect(() => {
    const timer = setTimeout(() => {
      // Role-based initial route: Admin to Admin console, Customer to Home/Onboarding
      if (user?.role === 'admin') {
        navigate('/admin', { replace: true })
        return
      }

      const hasSeenOnboarding = localStorage.getItem('hasSeenOnboarding')
      if (hasSeenOnboarding) {
        navigate('/home')
      } else {
        navigate('/onboarding')
      }
    }, 1500)

    return () => clearTimeout(timer)
  }, [navigate, user])

  return (
    <div className="min-h-screen bg-cream-200 flex flex-col items-center justify-center p-6 text-center animate-fade-in relative overflow-hidden">
      {/* Ambient Decorative Rings */}
      <div className="absolute w-96 h-96 rounded-full border border-walnut-200/40 scale-125 animate-ping-slow" />
      <div className="absolute w-72 h-72 rounded-full border border-gold-500/20" />

      {/* Brand Badge */}
      <div className="w-24 h-24 rounded-3xl bg-walnut-500 flex items-center justify-center text-gold-500 font-sans font-bold text-4xl shadow-warm-lg mb-6 ring-4 ring-gold-500/20 animate-bounce">
        G
      </div>

      <h1 className="font-sans font-bold text-3xl text-walnut-800 tracking-wide mb-2">
        Glory Furniture Hub
      </h1>
      <p className="text-xs text-gold-600 font-medium tracking-widest uppercase mb-8">
        Handcrafted Elegance • Timeless Craft
      </p>

      {/* Loading Indicator */}
      <div className="flex items-center gap-2 text-walnut-600 text-xs font-sans tracking-wide">
        <Sparkles className="w-4 h-4 text-gold-500 animate-spin" />
        <span>Crafting your experience...</span>
      </div>
    </div>
  )
}
