import React from 'react'
import { RefreshCw } from 'lucide-react'

export default function Button({
  children,
  variant = 'primary', // primary, secondary, accent, outline, ghost, danger
  size = 'md', // sm, md, lg
  isLoading = false,
  disabled = false,
  className = '',
  icon: Icon,
  type = 'button',
  onClick,
  ...props
}) {
  const baseStyles = 'inline-flex items-center justify-center font-semibold rounded-2xl transition-all duration-200 active-tap shadow-sm focus:outline-none'

  const variants = {
    primary: 'bg-walnut-500 hover:bg-walnut-600 text-white shadow-warm',
    secondary: 'bg-cream-200 hover:bg-cream-300 text-walnut-800 border border-walnut-200/60',
    accent: 'bg-gold-500 hover:bg-gold-600 text-white shadow-md',
    outline: 'bg-transparent border border-walnut-500 text-walnut-800 hover:bg-walnut-500/10',
    ghost: 'bg-transparent hover:bg-cream-200 text-walnut-700 shadow-none',
    danger: 'bg-dustyrose hover:bg-dustyrose/90 text-white'
  }

  const sizes = {
    sm: 'text-xs py-2 px-3 gap-1.5',
    md: 'text-xs py-3 px-4 gap-2',
    lg: 'text-sm py-4 px-6 gap-2.5'
  }

  return (
    <button
      type={type}
      disabled={disabled || isLoading}
      onClick={onClick}
      className={`${baseStyles} ${variants[variant] || variants.primary} ${sizes[size] || sizes.md} ${
        disabled || isLoading ? 'opacity-60 cursor-not-allowed transform-none' : ''
      } ${className}`}
      {...props}
    >
      {isLoading ? (
        <RefreshCw className="w-4 h-4 animate-spin text-current" />
      ) : Icon ? (
        <Icon className="w-4 h-4 text-current" />
      ) : null}
      <span>{children}</span>
    </button>
  )
}
