import React, { useState, useEffect } from 'react'
import { Download, X, Sparkles } from 'lucide-react'

export default function PwaInstallPrompt() {
  const [deferredPrompt, setDeferredPrompt] = useState(null)
  const [showPrompt, setShowPrompt] = useState(false)

  useEffect(() => {
    const handleBeforeInstall = (e) => {
      e.preventDefault()
      setDeferredPrompt(e)
      setShowPrompt(true)
    }

    window.addEventListener('beforeinstallprompt', handleBeforeInstall)
    return () => window.removeEventListener('beforeinstallprompt', handleBeforeInstall)
  }, [])

  const handleInstall = async () => {
    if (!deferredPrompt) return
    deferredPrompt.prompt()
    const { outcome } = await deferredPrompt.userChoice
    if (outcome === 'accepted') {
      setShowPrompt(false)
    }
    setDeferredPrompt(null)
  }

  if (!showPrompt) return null

  return (
    <div className="fixed bottom-20 left-4 right-4 z-50 max-w-md mx-auto bg-walnut-900 text-white p-4 rounded-2xl border border-gold-500/40 shadow-warm-lg flex items-center justify-between gap-3 animate-fade-in">
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-gold-500 flex items-center justify-center text-white font-serif font-bold text-lg">
          G
        </div>
        <div>
          <h4 className="font-serif font-bold text-xs text-white">Install Glory Furniture App</h4>
          <p className="text-[10px] text-cream-200">Fast offline access & instant booking updates</p>
        </div>
      </div>

      <div className="flex items-center gap-2">
        <button
          onClick={handleInstall}
          className="py-2 px-3 bg-gold-500 hover:bg-gold-600 text-white font-semibold text-xs rounded-xl active-tap flex items-center gap-1"
        >
          <Download className="w-3.5 h-3.5" /> Add
        </button>
        <button
          onClick={() => setShowPrompt(false)}
          className="p-1.5 text-cream-300 hover:text-white rounded-full"
        >
          <X className="w-4 h-4" />
        </button>
      </div>
    </div>
  )
}
