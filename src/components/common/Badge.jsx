import React from 'react'

export default function Badge({
  children,
  variant = 'default', // default, success, warning, danger, gold, info
  className = '',
  icon: Icon
}) {
  const variantStyles = {
    default: 'bg-cream-200 text-walnut-800 border border-walnut-200/50',
    success: 'bg-mutedgreen/10 text-mutedgreen border border-mutedgreen/20',
    warning: 'bg-gold-500/10 text-gold-600 border border-gold-500/20',
    danger: 'bg-dustyrose/10 text-dustyrose border border-dustyrose/20',
    gold: 'bg-gold-500 text-white font-bold',
    info: 'bg-walnut-500/10 text-walnut-800 border border-walnut-500/20'
  }

  return (
    <span
      className={`inline-flex items-center gap-1 text-[10px] font-bold tracking-wide uppercase px-2.5 py-0.5 rounded-full ${
        variantStyles[variant] || variantStyles.default
      } ${className}`}
    >
      {Icon && <Icon className="w-3 h-3 text-current" />}
      <span>{children}</span>
    </span>
  )
}
