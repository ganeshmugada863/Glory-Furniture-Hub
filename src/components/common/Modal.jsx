import React, { useEffect } from 'react'
import { X } from 'lucide-react'

export default function Modal({
  isOpen,
  onClose,
  title,
  children,
  position = 'bottom', // 'bottom' sheet or 'center' dialog
  className = ''
}) {
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden'
    } else {
      document.body.style.overflow = 'unset'
    }
    return () => {
      document.body.style.overflow = 'unset'
    }
  }, [isOpen])

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 bg-charcoal/60 backdrop-blur-sm flex justify-end flex-col animate-fade-in">
      <div
        className={`bg-white max-w-md w-full mx-auto border-walnut-200 shadow-warm-lg overflow-hidden flex flex-col ${
          position === 'bottom'
            ? 'rounded-t-3xl border-t max-h-[85vh]'
            : 'rounded-3xl my-auto border m-4 max-h-[90vh]'
        } ${className}`}
      >
        {/* Modal Header */}
        {title && (
          <div className="px-5 py-4 border-b border-cream-200 flex items-center justify-between bg-cream-100/60">
            <h3 className="font-sans font-bold text-base text-walnut-800 tracking-wide">{title}</h3>
            <button
              onClick={onClose}
              className="p-1.5 text-softgray hover:text-walnut-800 rounded-full hover:bg-cream-200 active-tap"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        )}

        {/* Modal Content */}
        <div className="p-5 overflow-y-auto flex-1">{children}</div>
      </div>
    </div>
  )
}
