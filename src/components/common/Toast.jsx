import React, { useEffect } from 'react'
import { CheckCircle2, AlertCircle, Info, X } from 'lucide-react'

export default function Toast({
  message,
  type = 'success', // success, error, info
  onClose,
  duration = 3000
}) {
  useEffect(() => {
    if (message && duration) {
      const timer = setTimeout(() => {
        onClose?.()
      }, duration)
      return () => clearTimeout(timer)
    }
  }, [message, duration, onClose])

  if (!message) return null

  const icons = {
    success: <CheckCircle2 className="w-4 h-4 text-mutedgreen" />,
    error: <AlertCircle className="w-4 h-4 text-dustyrose" />,
    info: <Info className="w-4 h-4 text-gold-600" />
  }

  const borderStyles = {
    success: 'border-mutedgreen/30 bg-white text-walnut-900',
    error: 'border-dustyrose/30 bg-white text-walnut-900',
    info: 'border-gold-500/30 bg-white text-walnut-900'
  }

  return (
    <div className="fixed top-16 left-1/2 -translate-x-1/2 z-50 w-11/12 max-w-sm animate-fade-in">
      <div className={`p-3.5 rounded-2xl border shadow-warm-lg flex items-center justify-between gap-3 ${borderStyles[type] || borderStyles.success}`}>
        <div className="flex items-center gap-2.5">
          {icons[type]}
          <span className="text-xs font-semibold">{message}</span>
        </div>
        <button onClick={onClose} className="p-1 text-softgray hover:text-walnut-800">
          <X className="w-4 h-4" />
        </button>
      </div>
    </div>
  )
}
